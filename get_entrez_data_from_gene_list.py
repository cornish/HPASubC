#!/usr/bin/env python

"""get_entrez_data_from_gene_list.py: retrieves the Entrez Gene Summary (if it exists) from HPA for each gene in a gene list.

usage: get_entrez_data_from_gene_list.py <input_file> <output_file>
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
import csv
from bs4 import BeautifulSoup
import os
import sys
import traceback 

def main(infile,outfile):
	try:
		with open(infile, 'rb') as f:    # Input file here
			results = [] 
			for gene in f.readlines():
				#makes sequential URLs from file of IDs
				gene = gene.strip()
				url = 'http://www.proteinatlas.org/%s/gene' % gene
				# parses out the tissue specificity data from each URL
				html = urllib.urlopen(url).read()
				soup = BeautifulSoup(html)
				# find the right header in the table, work up to the row
				row = soup.find(text='Entrez gene summary').parent.parent.parent
				#get the content of the cell
				entrez = row.td.string
				print gene, entrez, '\n'
				results.append([gene,entrez])  # add this data result to results
	
		with open(outfile , 'wb') as f: #create output file to write to here
			fieldnames = ['ENSGID','Entrez data']
			output = csv.writer(f, dialect='excel')
			output.writerow(fieldnames)
			for result in results: # still has the results b/c it was declared outside the while block
				output.writerow(result)

		print 'Complete.'

	except Exception,e: # catch any errors & pass on the message
		print 'Caught Exception: %s' % str(e)
		print traceback.format_exc()

if __name__ == '__main__':
	if len(sys.argv) != 3:
		print 'usage: %s <input_file> <output_file>' % os.path.basename(sys.argv[0])
		exit()
	else:
		main(sys.argv[1],sys.argv[2])
