#!/usr/bin/env python

"""get_gene_info_from_gene_list.py: retrieves the gene names, descriptions, and protein classes from HPA for each gene in a gene list. 

Note that since the recent rebuild of the HPA website, an XML or TSV download is available, but this script still screen scrapes. It could be converted in the future to parse the structured downloads directly

usage: get_gene_info_from_gene_list.py <input_file> <output_file>
"""
# CHANGE LOG:
# 06-18-2013 MK initial build
# 08-29-2013 TC clean up and standardize code
# 07-11-2014 TC additional code clean up and documentation
# 07-20-2014 TC fix to accomodate new HPA website html

__author__ = "Marc Halushka, Toby Cornish"
__copyright__ = "Copyright 2014, Johns Hopkins University"
__credits__ = ["Marc Halushka", "Toby Cornish"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Toby Cornish"
__email__ = "tcornis3@jhmi.edu"

import urllib
from bs4 import BeautifulSoup
import csv
import sys
import os
import re
import traceback 

def main(infile,outfile):
	try:
		with open(infile, "r") as f:
			results = [] 
			for gene in f.readlines():
				#makes sequential URLs from file of IDs
				gene = gene.strip()
				url = 'http://www.proteinatlas.org/search/'+gene
				#parses out the Gene Name from each page
				soup = BeautifulSoup(urllib.urlopen(url).read())
				# find the right row in the table, extract our data
				row = soup.find('tr',attrs={'class':'odd'})
				geneName = row.findAll('td')[0].text
				geneDesc = row.findAll('td')[1].text
				proteinClass = row.findAll('td')[2].text
				print gene,geneName,geneDesc,proteinClass
				results.append([gene,geneName,geneDesc,proteinClass])

		with open(outfile, "wb") as f: #create .csv output file to write to here
			fieldnames = ["ENSGID","Gene Name","Gene Description","Protein Class"]
			output = csv.writer(f, dialect='excel')
			output.writerow(fieldnames)
			for result in results:
				output.writerow(result)

		print "Complete."

	except Exception,e: # catch any errors & pass on the message
		print 'Caught Exception: %s' % str(e)
		print traceback.format_exc()

		
if __name__ == '__main__':
	if len(sys.argv) != 3:
		print 'usage: %s <input_file> <output_file>' % os.path.basename(sys.argv[0])
		exit()
	else:
		main(sys.argv[1],sys.argv[2])

