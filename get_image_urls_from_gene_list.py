#!/usr/bin/env python

"""get_image_urls_from_gene_list.py: given a file of Ensembl gene ids and a tissue will return a csv file with TMA core image urls from HPA. Known tissue types are listed in the README file

usage: get_image_urls_from_gene_list.py <input_file> <output_file> <tissue>
"""
# CHANGE LOG:
# 06-18-2013 MK initial build
# 08-29-2013 TC clean up and standardize code
# 07-11-2014 TC additional code clean up and documentation
# 07-13-2014 TC fix to accomodate new HPA website html

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
from bs4 import BeautifulSoup

def main(infile,outfile,tissue):
	try:
		with open(infile, "r") as f: # Input file here
			results = [] 
			for gene in f.readlines():
				gene = gene.strip()
				url = 'http://www.proteinatlas.org/%s/normal/%s' % (gene, urllib.quote(tissue))
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
								src = 'http://www.proteinatlas.org' + image.get('src')
								print gene,src
								results.append([gene,tissue,url,src])
				else:
					# tissue is not found
					print 'HPA response is: "Tissue %s not found!"' % tissue
					print 'Please check the validity of the tissue you are querying.'
					sys.exit()

		with open(outfile, "wb") as f: #create .csv output file to write to here
			fieldnames = ["proteinID","tissue","proteinURL","imageURL"]
			output = csv.writer(f, dialect='excel')
			output.writerow(fieldnames)
			for result in results:
				output.writerow(result)
					
		print "Complete."

	except Exception,e: # catch any errors & pass on the message
		print 'Caught Exception: %s' % str(e)
		print traceback.format_exc()

if __name__ == '__main__':
	if len(sys.argv) != 4:
		print 'usage: %s <input_file> <output_file> <tissue>' % os.path.basename(sys.argv[0])
		sys.exit()
	else:
		main(sys.argv[1],sys.argv[2],sys.argv[3])

