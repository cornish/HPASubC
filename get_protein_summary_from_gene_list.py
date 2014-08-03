#!/usr/bin/env python

"""get_protein_summary_from_gene_list.py: given a file listing Ensembl gene ids, will return a csv file with the tissue specificity and staining summary from HPA

usage: get_protein_summary_from_gene_list.py <input_file> <output_file>
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
import sys
import os
import re
import traceback 
from bs4 import BeautifulSoup

def main(infile,outfile):
	try:
		with open(infile, "r") as f: # Input file here
			results = [] 
			for gene in f.readlines():
				#makes sequential URLs from file of IDs
				gene = gene.strip()
				url = 'http://www.proteinatlas.org/' + gene
				# parses out the tissue specificity data from each URL
				html = urllib.urlopen(url).read()
				soup = BeautifulSoup(html)
				# find the th by its text
				header = soup.find(text='Protein summary')
				# get the associated tr by traversing up three levels
				row = header.parent.parent.parent
				# get the td contents and strip them to create plain text
				pattern = stripTagsAndJoin(row.td.contents)
				print gene, pattern
				results.append([gene,pattern]) # add this data result to results

		with open(outfile , 'wb') as f: #output as an excel-compatible csv
			fieldnames = ['ENSGID','protein expression']
			output = csv.writer(f, dialect='excel')
			output.writerow(fieldnames)
			for result in results:
				output.writerow(result)
				
		print 'Complete.'
		
	except Exception,e: # catch any errors & pass on the message
		print 'Caught Exception: %s' % str(e)
		print traceback.format_exc()
		
def stripTagsAndJoin(tagList):
	stripped = []
	for t in tagList:
		s = str(t)
		s = s.strip() #remove extra whitespace
		s = re.sub('<[^>]*>', '', s) #remove the text of the actual tags
		stripped.append(s)
	joined = ' '.join(stripped) #join with spaces
	joined = re.sub(' +', ' ', joined) #eliminate any multiple spaces
	return joined
	
if __name__ == '__main__':
	if len(sys.argv) != 3:
		print 'usage: %s <input_file> <output_file>' % os.path.basename(sys.argv[0])
		sys.exit()
	else:
		main(sys.argv[1],sys.argv[2])
