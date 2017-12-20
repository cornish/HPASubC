#!/usr/bin/env python

"""download_images_from_gene_list_multi.py: given a file of Ensembl gene ids, a valid tissue, and an output directory will download the full size images for that gene id, and create a CSV file with columns containing the following data from HPA:

	image_file: the name of the image file downloaded
	ensg_id: the Ensembl gene id
	tissue_or_cancer: the tissue_or_cancer represented in the image
	antibody: the id of the antibody in the image
	protein_url: deprecated
	image_url: the HPA url the image was downloaded from
	workers: the number of workers to use, default (and minimum) is 4

Known tissue (and cancer) types are listed in the APPENDICES of the README file

This script also embeds the above information as json in the Exif.UserComment tag in each downloaded image. This Exif data is used by the subsequent software (viewer, scorer) to associate the image file with the ensg_id, antibody, etc.

usage: download_images_from_gene_list_multi.py <input_file> <output_file> <tissue> <output_dir> [workers]
"""

# CHANGE LOG:
# 11-08-2014 TC first version using multiprocessing for parallel downloads
# 11-09-2014 TC swapped in multithreading for multiprocessing
# 04-30-2015 TC corrected error in arg parsing
# 12-19-2017 TC rewrote to source image url data from hpasubc REST api

__author__ = "Marc Halushka, Toby Cornish"
__copyright__ = "Copyright 2014-2017, Johns Hopkins University"
__credits__ = ["Marc Halushka", "Toby Cornish"]
__license__ = "GPL"
__version__ = "1.1.0"
__maintainer__ = "Toby Cornish"
__email__ = "tcornish@gmail.com"

import urllib2
import csv
import sys
import os
import re
import datetime
import traceback
import json
import pyexiv2
from itertools import repeat
import multiprocessing as mp
from multiprocessing.dummy import Pool as ThreadPool
from api_client import get_tissues, get_genes, get_images

def main(infile,outfile,tissue,outdir,create,skip,numWorkers):
	logFile = os.path.join(outDir,'log.txt')

	fieldnames = ['image_file','ensg_id','tissue_or_cancer','antibody','protein_url','image_url']

	with open(outfile, "ab") as f: #create or append .csv output file to write to here
		writer = csv.DictWriter(f, dialect='excel',fieldnames=fieldnames)
		#add the header if this is a new file
		if create:
			writer.writerow(dict((fn,fn) for fn in fieldnames))

	geneList = []
	skipList = []
	with open(infile, "r") as f: # Input file here
		for gene in f.readlines():
			gene = gene.strip()
			if gene in skip:
				skipList.append(gene)
				print 'Skipping %s ...' % gene
			else:
				geneList.append(gene)

	print '\nSkipping a total of %s ensg_ids' % len(skipList)
	print 'Processing a total of %s ensg_ids' % len(geneList)

	#create a pool of workers
	print 'Creating a pool of %s workers.\n' % numWorkers
	pool = ThreadPool(numWorkers)

	#create shared queues to handle writing to our output and log files
	manager = mp.Manager()
	outQ = manager.Queue()
	logQ = manager.Queue()

	#use a shared variable to keep a count of errors
	errorCount = manager.Value('i',0)

	print 'Getting image list...'
	images = get_images(geneList,[tissue,])
	print '  done.'
	print 'Found a total of %s images' % len(images)

	#zip together the data into an array of tuples so that we can use a map function
	data = zip(images,repeat(outdir),repeat(outQ),repeat(logQ),repeat(errorCount))
	#print data

	#start the listener threads for the file writing queues
	pool.apply_async(resultListener, (outQ,outfile,fieldnames))
	pool.apply_async(logListener, (logQ,logFile))

	#map our data to a pool of workers, i.e. do the work
	pool.map(worker, data)

	#kill off the queue listeners and close the pool
	outQ.put('kill')
	logQ.put('kill','')
	pool.close()

	print "Complete.\n"
	if errorCount.value > 0:
		print "There were %s errors.\n\nPlease check the log file: %s" % (errorCount.value,os.path.abspath(logFile))

def resultListener(q,filepath,fieldnames):
	'''listens for messages on the q, writes to file using a csv writer. '''
	with open(filepath, "ab") as f: #create or append .csv output file to write to here
		writer = csv.DictWriter(f, dialect='excel',fieldnames=fieldnames)
		while 1:
			result = q.get()
			if result == 'kill':
				break
			writer.writerow(result)

def logListener(q,filepath):
	with open(filepath, "ab") as f:
		while 1:
			(type,message) = q.get()
			if type == 'kill':
				break
			timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			f.write('%s %s  %s\n' % (timestamp,type,message) )

def worker((image,outdir,outQ,logQ,errorCount)):
	print 'Downloading %s (%s) ...\n' % (image['image_url']
		,image['ensg_id'])
	try:
		result = {}
		result['ensg_id'] = image['ensg_id']
		result['tissue_or_cancer'] = image['tissue_or_cancer']
		result['protein_url'] = 'deprecated'
		result['image_url'] = image['image_url']
		result['antibody'] = image['antibody_id']
		result['image_file'] = image['image_file']
		# download the image
		downloadImage(image['image_url'],image['image_file'],outdir)
		imagePath = os.path.join(outdir,result['image_file'])
		# add the exif data to it
		writeExifUserComment(imagePath,result)
		# write the row to our output file
		outQ.put(result)

	except KeyboardInterrupt: #handle a ctrl-c
		print 'Exiting'
		sys.exit()
	except Exception,e: # catch any errors & pass on the message
		errorCount.value += 1
		message = '%s %s %s' % (image['ensg_id'],image['image_url'],str(e))
		logQ.put('ERROR',message)
		print 'Caught Exception: %s' % str(e)
		print traceback.format_exc()

def downloadImage(imageUrl,image_name,outdir):
	try:
		print '    image: %s -> %s\n' % (imageUrl,image_name)
		image_data = urllib2.urlopen(imageUrl).read()
		# Open output file in binary mode, write, and close.
		imagePath = os.path.join(outdir,image_name)
		with open(imagePath,'wb') as fout:
			fout.write(image_data)
	except Exception,e: # catch any errors & pass on the message
		print 'Caught Exception: %s' % str(e)
		print traceback.format_exc()

def writeExifUserComment(imagePath,userCommentAsDict):
	# read in the exif data, add the user comment as json, and write it
	metadata = pyexiv2.ImageMetadata(imagePath)
	metadata.read()
	metadata['Exif.Photo.UserComment'] = json.dumps(userCommentAsDict)
	metadata.write()

def fileIsWriteable(filePath):
	exists = os.path.exists(filePath)
	try:
		f = open(filePath , 'ab')
		f.close()
		if not exists:
			os.remove(filePath)
		return True
	except Exception,e:
		print e
		return False

def readProgress(filePath):
	# open csv file
	uniqueIds = []
	with open(filePath, 'rb') as f:
		# get number of columns
		for line in f.readlines():
			id = line.split(',')[1]
			if id not in uniqueIds:
				uniqueIds.append(id)
	#remove the last id on the list
	if len(uniqueIds) > 0:
		uniqueIds.pop()
	return uniqueIds

def query_yes_no(question, default="yes"):
	"""Ask a yes/no question via raw_input() and return their answer.
	see http://code.activestate.com/recipes/577058/"""

	valid = {"yes": True, "y": True, "ye": True,
					 "no": False, "n": False}
	if default is None:
		prompt = " [y/n] "
	elif default == "yes":
		prompt = " [Y/n] "
	elif default == "no":
		prompt = " [y/N] "
	else:
		raise ValueError("invalid default answer: '%s'" % default)

	while True:
		try:
			sys.stdout.write(question + prompt)
			choice = raw_input().lower()
			if default is not None and choice == '':
				return valid[default]
			elif choice in valid:
				return valid[choice]
			else:
				sys.stdout.write("Please respond with 'yes' or 'no' "
												 "(or 'y' or 'n').\n")
		except KeyboardInterrupt: #handle a ctrl-c
			sys.exit()

def get_valid_tissues():
	tissues_file = 'valid_tissues.txt'
	if not os.path.isfile(tissues_file):
		tissues = [i.tissue_or_cancer.lower() for i in Image.select(Image.tissue_or_cancer).distinct()]
		with open(tissues_file,'wb') as f:
			for tissue in tissues:
				f.write(tissue+'\n')
		return tissues
	else:
		lines = []
		with open(tissues_file,'rb') as f:
			lines = f.readlines()
		return [l.strip() for l in lines] 


if __name__ == '__main__':
	if len(sys.argv) < 5 or len(sys.argv) > 6:
		print '\nIncorrect number of arguments!\n\n'
		print 'usage: %s <input_file> <output_file> <tissue> <output_dir> [workers]' % os.path.basename(sys.argv[0])
		sys.exit()
	else:
		inFile = sys.argv[1]
		outFile = sys.argv[2]
		tissue = sys.argv[3]
		outDir = sys.argv[4]
		if len(sys.argv) == 6 and int(sys.argv[5]) > 3:
			numWorkers = int(sys.argv[5])
		else:
			# no number of workers provided or number < 3, so use default minimum
			numWorkers = 3

		tissues = get_valid_tissues()

		if tissue.lower() not in tissues:
			print 'The tissue %s is not a valid option.' % tissue
			print 'Valid tissues are: %s' % ', '.join(tissues)
			sys.exit()

		if not os.path.isfile(inFile):
			print 'The input file %s does not exist.' % inFile
			sys.exit()

		try:
			if not os.path.exists(outDir):
				# make the directory if it doesn't exist
				os.makedirs(outDir)
		except Exception,e: #catch error making directory
			print e
			print 'Error creating directory %s' % outDir
			sys.exit()

		if not fileIsWriteable(outFile):
			print 'The output file %s is not writable -- is it open?' % outFile
			sys.exit()

		create = True
		skip = []
		if os.path.exists(outFile):
			create = False
			print 'The output file %s exists.' % outFile
			overwrite = query_yes_no('Overwrite?',default="no")
			if overwrite:
				os.remove(outFile)
				create = True
			else:
				resume = query_yes_no('Try to resume?',default="yes")
				if resume:
					skip = readProgress(outFile)
				else:
					append = query_yes_no('Append the file (or n to quit)?',default="yes")
					if not append:
						print 'ok. exiting...'
						sys.exit()

		main(inFile,outFile,tissue,outDir,create,skip,numWorkers)
