#!/usr/bin/env python

"""download_images_from_gene_list_multi.py: given a file of Ensembl gene ids, a valid tissue, and an output directory will download the full size images for that gene id, and create a CSV file with columns containing the following data from HPA:

	image_file: the name of the image file downloaded
	ensg_id: the Ensembl gene id
	tissue_or_cancer: the tissue_or_cancer represented in the image
	antibody: the id of the antibody in the image
	protein_url: the HPA url for the ensg_id
	image_url: the HPA url the image was downloaded from
	workers: the number of workers to use, default (and minimum) is 4

For cancers, the ouput file contains these additional fields:
	demographic: sex and age of patient
	tissue: tissue source with Snomed code
	diagnoses: |-separated list of diagnoses with Snomed code
	patient_id: hpa patient id
	staining: is staining present?
	intensity: staining intensity
	quantity: staining quantity
	location: staining location

Known tissue (and cancer) types are listed in the APPENDICES of the README file

This script also embeds the above information as json in the Exif.UserComment tag in each downloaded image. This Exif data is used by the subsequent software (viewer, scorer) to associate the image file with the ensg_id, antibody, etc.

usage: download_images_from_gene_list_multi.py <input_file> <output_file> <tissue> <output_dir> [workers]
"""

# CHANGE LOG:
# 11-08-2014 TC first version using multiprocessing for parallel downloads
# 11-09-2014 TC swapped in multithreading for multiprocessing
# 04-30-2015 TC corrected error in arg parsing

__author__ = "Marc Halushka, Toby Cornish"
__copyright__ = "Copyright 2014, Johns Hopkins University"
__credits__ = ["Marc Halushka", "Toby Cornish"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Toby Cornish"
__email__ = "tcornis3@jhmi.edu"

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
from bs4 import BeautifulSoup

cancers =   ['colorectal cancer','breast cancer','prostate cancer',
			'ovarian cancer','cervical cancer','endometrial cancer',
			'carcinoid','head and neck cancer','thyroid cancer',
			'glioma','lymphoma','lung cancer','melanoma',
			'skin cancer','testis cancer','urothelial cancer',
			'renal cancer','stomach cancer','pancreatic cancer',
			'liver cancer']

def main(infile,outfile,tissue,outdir,create,skip,numWorkers):
	logFile = os.path.join(outDir,'log.txt')

	isCancer = tissue.lower() in cancers #the cancers have different web pages and urls
	fieldnames = ['image_file','ensg_id','tissue_or_cancer','antibody','protein_url','image_url']
	if isCancer:
		fieldnames.extend(['demographic','tissue','diagnosis','patient_id','staining','intensity','quantity','location'])

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

	print '\nSkipping a total of %s\n' % len(skipList)
	print 'Processing a total of %s\n' % len(geneList)

	#create a pool of workers
	print 'Creating a pool of %s workers.\n' % numWorkers
	pool = ThreadPool(numWorkers)

	#create shared queues to handle writing to our output and log files
	manager = mp.Manager()
	outQ = manager.Queue()
	logQ = manager.Queue()

	#use a shared variable to keep a count of errors
	errorCount = manager.Value('i',0)

	#zip together the data into an array of tuples so that we can use a map function
	data = zip(geneList,repeat(tissue),repeat(isCancer),repeat(outdir),repeat(outQ),repeat(logQ),repeat(errorCount))
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

def worker((gene,tissue,isCancer,outdir,outQ,logQ,errorCount)):
	print 'Sending %s to worker...\n' % (gene,)
	if isCancer:
		url = 'http://www.proteinatlas.org/%s/cancer/tissue/%s' % (gene, urllib2.quote(tissue))
		attrib = 'name' #for some reason cancer uses name
	else:
		url = 'http://www.proteinatlas.org/%s/tissue/%s' % (gene, urllib2.quote(tissue))
		attrib = 'id' #for some reason tissue uses id
	try:
		# retrieve the html page from HPA and parse it
		print '  requesting %s ...\n' % url
		soup = BeautifulSoup(urllib2.urlopen(url).read())
		# first check to see if the tissue is not found
		if soup.find(text='Tissue %s not found!' % tissue) is None:
			# tissue is found
			links = soup.findAll('a') #find all the links in the page
			for link in links:
				if link.get(attrib) is not None: # ignore links that do not have names
					if re.match('_image\d*',link.get(attrib)) is not None:
						# all the image links are named '_imageN', ignore if no match
						image = link.img # get the img displayed for this link
						imageUrl = 'http://www.proteinatlas.org' + image.get('src')
						print '      url: %s' % imageUrl
						imageUrl = imageUrl.replace('_medium','') # get the full resolution images
						imageUrl = imageUrl.replace('_thumb','') # get the full resolution images
						antibodyPlusImage = imageUrl.replace('http://www.proteinatlas.org/images/','')
						antibody,imageFile = antibodyPlusImage.split('/')
						result = {}
						result['ensg_id'] = gene
						result['tissue_or_cancer'] = tissue
						result['protein_url'] = url
						result['image_url'] = imageUrl
						result['antibody'] = antibody
						result['image_file'] = imageFile
						if isCancer:
							mo = image.get('onmouseover')
							patientInfo = parsePatientInfo(mo)
							stainingInfo = parseStainingInfo(mo)
							result.update(patientInfo)
							result.update(stainingInfo)
						# download the image
						downloadImage(result['image_url'],result['image_file'],outdir)
						imagePath = os.path.join(outdir,result['image_file'])
						# add the exif data to it
						writeExifUserComment(imagePath,result)
						# write the row to our output file
						outQ.put(result)

		else:
			# tissue is not found
			errorCount.value += 1
			logQ.put( ('ERROR',"Tissue %s not found!" % tissue ))
			print 'HPA response is: "Tissue %s not found!"' % tissue
			print 'Please check the validity of the tissue you are querying.'
			sys.exit()

	except KeyboardInterrupt: #handle a ctrl-c
		print 'Exiting'
		sys.exit()
	except Exception,e: # catch any errors & pass on the message
		errorCount.value += 1
		message = '%s %s %s' % (gene,url,str(e))
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

def parsePatientInfo(mo):
	patientInfo = {'demographic' : '','tissue' : '','diagnosis' : '', 'patient_id' : ''}
	mo = mo.replace('<br>','\n') #convert to newlines / multiline
	#mo = mo.replace('<b>','')
	#mo = mo.replace('</b>','')
	#mo = mo.replace("tooltip('",'')
	#mo = mo.replace("', 0);",'')

	m = re.search(r'<b>(Female|Male), age (.*?)</b>',mo)
	if m:
		patientInfo['demographic'] = '%s %s' % (m.group(1),m.group(2))

	m = re.search(r'<b>(.*?)</b> \((T-.*?)\)',mo)
	if m:
		patientInfo['tissue'] = '%s %s' % (m.group(1),m.group(2))

	m = re.findall(r'<b>(.*?)</b> \((M-.*?)\)',mo,re.M)
	patientInfo['diagnosis'] = '|'.join( ['%s %s' % dx for dx in m] )

	m = re.search(r'<b>Patient id:</b> *(\d+)',mo)
	if m:
		patientInfo['patient_id'] = m.group(1)

	return patientInfo

def parseStainingInfo(mo):
	stainingInfo = {'staining' : '','intensity' : '', 'quantity' : '', 'location' : ''}
	mo = mo.replace('<br>','\n') #convert to newlines / multiline

	m = re.search(r'<b>Antibody staining:</b> *(.+) *',mo)
	if m:
		stainingInfo['staining'] = m.group(1)

	m = re.search(r'<b>Intensity:</b> *(.+) *',mo)
	if m:
		stainingInfo['intensity'] = m.group(1)

	m = re.search(r'<b>Quantity:</b> *(.+) *',mo)
	if m:
		stainingInfo['quantity'] = m.group(1)

	m = re.search(r"<b>Location:</b> *(.+)'",mo)
	if m:
		stainingInfo['location'] = m.group(1)

	return stainingInfo

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
