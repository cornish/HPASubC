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
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

# CHANGE LOG:
# 11-08-2014 TC first version using multiprocessing for parallel downloads
# 11-09-2014 TC swapped in multithreading for multiprocessing
# 04-30-2015 TC corrected error in arg parsing
# 12-19-2017 TC rewrote to source image url data from hpasubc REST api

from future import standard_library
standard_library.install_aliases()
from builtins import zip
from builtins import input
from builtins import str

__author__ = "Marc Halushka, Toby Cornish"
__copyright__ = "Copyright 2014-2017, Johns Hopkins University"
__credits__ = ["Marc Halushka", "Toby Cornish"]
__license__ = "GPL"
__version__ = "1.2.0"
__maintainer__ = "Toby C. Cornish"
__email__ = "tcornish@gmail.com"

import logging
import urllib.request, urllib.error, urllib.parse
import csv
import time
import sys
import os
import re
import datetime
import traceback
import json
import piexif
import piexif.helper
from itertools import repeat
import multiprocessing as mp
from multiprocessing.dummy import Pool as ThreadPool
from api_client import get_tissues, get_genes, get_images

#configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# create a file handler
log_file = 'download_images.log'
handler = logging.FileHandler(log_file)
handler.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)


def main(infile,outfile,tissue,outdir,create,skip,numWorkers):

	fieldnames = ['image_file','ensg_id','tissue_or_cancer','antibody','protein_url','image_url']

	if os.path.exists(outfile):
		mode = 'a' # append if already exists
	else:
		mode = 'w' # make a new file if not
	
	# there are some 2 v. 3 differences here to avoid extra blank lines
	if (sys.version_info > (3, 0)):	
		f = open(outfile,mode,newline='\n')
	else:
		f = open(outfile,mode+'b')
	writer = csv.DictWriter(f, dialect='excel',fieldnames=fieldnames,extrasaction='ignore')
	if mode == 'w':
		writer.writeheader()
	f.close()

	geneList = []
	skipList = []
	with open(infile, "r") as f: # Input file here
		for gene in f.readlines():
			gene = gene.strip()
			if gene in skip:
				skipList.append(gene)
				logger.info('Skipping %s' % gene)
			else:
				geneList.append(gene)

	print('\nSkipping a total of %s ensg_ids' % len(skipList))
	print('Processing a total of %s ensg_ids' % len(geneList))

	#create a pool of workers
	print('Creating a pool of %s workers.\n' % numWorkers)
	pool = ThreadPool(numWorkers)

	#create shared queue to handle writing to our output FILE
	manager = mp.Manager()
	outQ = manager.Queue()

	#use a shared variable to keep a count of errors
	errorCount = manager.Value('i',0)

	logger.info('Getting image list...')
	images = get_images(geneList,[tissue,])
	print('  done.')
	logger.info('Found a total of %s images on HPA' % len(images))

	#find duplicate images
	duplicate_images = [x ['image_file'] for x in images if os.path.exists(os.path.join(outdir,x['image_file']))]

	#if any of the images already exist in the outdir, query if we should overwrite 
	if duplicate_images:
		logger.info('%s images with duplicate names found in output directory "%s".',len(duplicate_images),outdir)
		overwrite_images = query_yes_no('Duplicate images found. Overwrite images?',default="no")
		if overwrite_images:
			logger.info('Will overwrite %s duplicate images.' % len(duplicate_images))
		else:
			logger.info('Will skip %s duplicate images.' % len(duplicate_images))
	else:
		overwrite_images = True

	# remove duplicate_images from list of images
	if not overwrite_images:
		images = [x for x in images if x['image_file'] not in duplicate_images]
	logger.info('Queuing %s images for download' % len(images))

	#zip together the data into an array of tuples so that we can use a map function
	data = list(zip(images,repeat(outdir),repeat(outQ),repeat(errorCount)))

	#start the listener threads for the file writing queues
	pool.apply_async(resultListener, (outQ,outfile,fieldnames))

	#map our data to a pool of workers, i.e. do the work
	pool.map(worker, data)

	#kill off the queue listeners and close the pool
	outQ.put('kill')
	pool.close()

	logger.info("Finished")
	if errorCount.value > 0:
		print("There were %s errors.\n\nPlease check the log file: %s" % (errorCount.value,log_file))

def resultListener(q,filepath,fieldnames):
	'''listens for messages on the q, writes to file using a csv writer. '''

	# there are some 2 v. 3 differences here to avoid extra blank lines
	mode = 'a'
	if (sys.version_info > (3, 0)):	
		f = open(filepath,mode,newline='\n')
	else:
		f = open(filepath,mode+'b')
	writer = csv.DictWriter(f, dialect='excel',fieldnames=fieldnames,extrasaction='ignore')
	while 1:
		result = q.get()
		if result == 'kill':
			break
		writer.writerow(result)
	f.close()


def worker(xxx_todo_changeme):
	(image,outdir,outQ,errorCount) = xxx_todo_changeme
	logger.info('Downloading %s (%s)' % (image['image_url']
		,image['ensg_id']))
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
		print('Exiting')
		sys.exit()
	except Exception as e: # catch any errors & pass on the message
		errorCount.value += 1
		message = '%s %s %s' % (image['ensg_id'],image['image_url'],str(e))
		logger.error('Caught Exception: %s' % str(e))
		logger.error(traceback.format_exc())

def downloadImage(imageUrl,image_name,outdir):
	MAX_ATTEMPTS = 10
	attempts = 0
	while attempts < MAX_ATTEMPTS:
		try:
			attempts += 1
			image_data = urllib.request.urlopen(imageUrl).read()
			# Open output file in binary mode, write, and close.
			imagePath = os.path.join(outdir,image_name)
			with open(imagePath,'wb') as fout:
				fout.write(image_data)
			logger.info('Finished download for %s',image_name)
			break
		except Exception as e: # catch any errors & pass on the message
			# write the exception only if this is the last attempt; this may not work
			print(attempts)
			if attempts == MAX_ATTEMPTS:
				logger.error('Caught Exception: %s for %s',str(e),imageUrl)
				logger.error(traceback.format_exc())
			time.sleep(1)

def writeExifUserComment(imagePath,userCommentAsDict):
	# read in the exif data, add the user comment as json, and write it
	exif_dict = piexif.load(imagePath)
	# convert the jason to proper encoding	
	user_comment = piexif.helper.UserComment.dump(json.dumps(userCommentAsDict))
	# pop it into the exif_dict
	exif_dict["Exif"][piexif.ExifIFD.UserComment] = user_comment
	# get the exif as bytes
	exif_bytes = piexif.dump(exif_dict)
	# insert the modified exif_bytes
	piexif.insert(exif_bytes, imagePath)

def fileIsWriteable(filePath):
	exists = os.path.exists(filePath)
	try:
		f = open(filePath , 'a')
		f.close()
		if not exists:
			os.remove(filePath)
		return True
	except Exception as e:
		print(e)
		return False

def readProgress(filePath):
	# open csv file
	uniqueIds = []
	with open(filePath, 'r') as f:
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
			choice = input().lower()
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
		tissues = get_tissues()
		with open(tissues_file,'w') as f:
			for tissue in tissues:
				f.write(tissue+'\n')
		return tissues
	else:
		lines = []
		with open(tissues_file,'r') as f:
			lines = f.readlines()
		return [l.strip() for l in lines] 


if __name__ == '__main__':
	if len(sys.argv) < 5 or len(sys.argv) > 6:
		print('\nIncorrect number of arguments!\n\n')
		print('usage: %s <input_file> <output_file> <tissue> <output_dir> [workers]' % os.path.basename(sys.argv[0]))
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
			print('The tissue %s is not a valid option.' % tissue)
			print('Valid tissues are: %s' % ', '.join(tissues))
			sys.exit()

		if not os.path.isfile(inFile):
			print('The input file %s does not exist.' % inFile)
			sys.exit()

		try:
			if not os.path.exists(outDir):
				# make the directory if it doesn't exist
				os.makedirs(outDir)
		except Exception as e: #catch error making directory
			print(e)
			print('Error creating directory %s' % outDir)
			sys.exit()

		if not fileIsWriteable(outFile):
			print('The output file %s is not writable -- is it open?' % outFile)
			sys.exit()

		create = True
		skip = []
		if os.path.exists(outFile):
			create = False
			print('The output file %s exists.' % outFile)
			overwrite = query_yes_no('Overwrite?',default="no")
			if overwrite:
				os.remove(outFile)
				create = True
			else:
				append = query_yes_no('Append the file (or n to quit)?',default="yes")
				if not append:
					print('ok. exiting...')
					sys.exit()

		#logger.info(inFile,outFile,tissue,outDir,create,skip,numWorkers)
		logger.info(inFile)
		main(inFile,outFile,tissue,outDir,create,skip,numWorkers)
