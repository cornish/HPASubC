#!/usr/bin/env python

"""download_images_from_gene_list.py: given a file of Ensembl gene ids, a valid tissue, and an output directory will download the full size images for that gene id, and create a CSV file with columns containing the following data from HPA:

  image_file: the name of the image file downloaded
  ensg_id: the Ensembl gene id
  tissue: the tissue represented in the image
  antibody: the id of the antibody in the image
  protein_url: the HPA url for the ensg_id
  image_url: the HPA url the image was downloaded from

Known tissue (and cancer) types are listed in the APPENDICES of the README file

This script also embeds the above information as json in the Exif.UserComment tag in each downloaded image. This Exif data is used by the subsequent software (viewer, scorer) to associate the image file with the ensg_id, antibody, etc.

usage: download_images_from_gene_list.py <input_file> <output_file> <tissue> <output_dir>
"""

# CHANGE LOG:
# 06-18-2013 MK initial build
# 08-29-2013 TC clean up and standardize code
# 07-11-2014 TC additional code clean up and documentation
# 07-13-2014 TC fix to accomodate new HPA website html
# 08-05-2014 TC combined two scripts to create this one

__author__ = "Marc Halushka, Toby Cornish"
__copyright__ = "Copyright 2014, Johns Hopkins University"
__credits__ = ["Marc Halushka", "Toby Cornish"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Toby Cornish"
__email__ = "tcornis3@jhmi.edu"

import urllib
import urlparse
import csv
import sys
import os
import re
import traceback
import json
import pyexiv2
from bs4 import BeautifulSoup

cancers = 	['colorectal cancer','breast cancer','prostate cancer',
						'ovarian cancer','cervical cancer','endometrial cancer',
						'carcinoid','head and neck cancer','thyroid cancer',
						'glioma','lymphoma','lung cancer','melanoma',
						'skin cancer','testis cancer','urothelial cancer',
						'renal cancer','stomach cancer','pancreatic cancer',
						'liver cancer']

def main(infile,outfile,tissue,outdir):
	try:
		with open(infile, "r") as f: # Input file here
			results = []
			for gene in f.readlines():
				gene = gene.strip()
				if tissue.lower() in cancers: #the cancers need a different url
					url = 'http://www.proteinatlas.org/%s/cancer/tissue/%s' % (gene, urllib.quote(tissue))
				else:
					url = 'http://www.proteinatlas.org/%s/tissue/%s' % (gene, urllib.quote(tissue))
				# retrieve the html page from HPA and parse it
				soup = BeautifulSoup(urllib.urlopen(url).read())
				# first check to see if the tissue is not found
				if soup.find(text='Tissue %s not found!' % tissue) is None:
					# tissue is found
					links = soup.findAll('a') #find all the links in the page
					for link in links:
						if link.get('name') is not None: # ignore links that do not have names
							if re.match('_image\d*',link.get('name')) is not None:
								# all the image links are named '_imageN', ignore if no match
								image = link.img # get the img displayed for this link
								imageUrl = 'http://www.proteinatlas.org' + image.get('src')
								print gene,imageUrl
								imageUrl = imageUrl.replace('_medium','') # get the full resolution images
								imageUrl = imageUrl.replace('_thumb','') # get the full resolution images
								antibodyPlusImage = imageUrl.replace('http://www.proteinatlas.org/images/','')
								antibody,imageFile = antibodyPlusImage.split('/')
								result = {}
								result['ensg_id'] = gene
								result['tissue'] = tissue
								result['protein_url'] = url
								result['image_url'] = imageUrl
								result['antibody'] = antibody
								result['image_file'] = imageFile
								results.append(result)
				else:
					# tissue is not found
					print 'HPA response is: "Tissue %s not found!"' % tissue
					print 'Please check the validity of the tissue you are querying.'
					sys.exit()

		with open(outfile, "wb") as f: #create .csv output file to write to here
			fieldnames = ['image_file','ensg_id','tissue','antibody','protein_url','image_url']
			writer = csv.DictWriter(f, dialect='excel',fieldnames=fieldnames)
			writer.writerow(dict((fn,fn) for fn in fieldnames))
			for result in results:
				writer.writerow(result)
				# download the image
				downloadImage(result['image_url'],result['image_file'],outdir)
				imagePath = os.path.join(outdir,result['image_file'])
				# add the exif data to it
				writeExifUserComment(imagePath,result)

		print "Complete."

	except Exception,e: # catch any errors & pass on the message
		print 'Caught Exception: %s' % str(e)
		print traceback.format_exc()

def downloadImage(imageUrl,image_name,outdir):
	try:
		print '%s -> %s' % (imageUrl,image_name)
		image_data = urllib.urlopen(imageUrl).read()
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
	try:
		f = open(filePath , 'ab')
		f.close()
		return True
	except Exception,e:
		print e
		return False

if __name__ == '__main__':
	if len(sys.argv) != 5:
		print 'usage: %s <input_file> <output_file> <tissue> <output_dir>' % os.path.basename(sys.argv[0])
		sys.exit()
	else:
		inFile = sys.argv[1]
		outFile = sys.argv[2]
		tissue = sys.argv[3]
		outDir = sys.argv[4]

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
			print 'The output file %s is not writeable -- is it open?' % outFile
			sys.exit()

		main(inFile,outFile,tissue,outDir)

