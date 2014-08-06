#!/usr/bin/env python

"""download_gene_data_from_gene_list.py: given a file listing Ensembl gene ids, will return a csv file columns with the following data from HPA:

  ensg_id: the Ensembl gene id
  gene_name: the corresponding short gene name
  gene_description: the full gene name and/or description
  protein_class: the class of the gene product
  entrez_data: the Entrez Gene Summary (if it exists)
  protein_expr: a summary of the expression pattern across HPA samples

Note that since the recent rebuild of the HPA website, an XML or TSV download is available, but this script still screen scrapes. It could be converted in the future to parse the structured downloads directly

usage: download_gene_data_from_gene_list.py <input_file> <output_file>
"""
# CHANGE LOG:
# 06-18-2013 MK initial build
# 08-29-2013 TC clean up and standardize code
# 07-11-2014 TC additional code clean up and documentation
# 07-13-2014 TC fix to accomodate new HPA website html
# 08-05-2012 TC consolidate all metadata downloads into one script

__author__ = "Marc Halushka, Toby Cornish"
__copyright__ = "Copyright 2014, Johns Hopkins University"
__credits__ = ["Marc Halushka", "Toby Cornish"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Toby Cornish"
__email__ = "tcornis3@jhmi.edu"

import urllib
import csv
import os
import sys
import re
import traceback 
from bs4 import BeautifulSoup

def main(infile,outfile):
	try:
		results = [] 
		with open(infile, 'rb') as f:    # Input file here
			print '='*60
			for gene in f.readlines():
				# read the gene and clean up ====================
				gene = gene.strip()
				result = {}
				result['ensg_id'] = gene
				print 'ENSG_ID: %s\n' % gene
				
				# get the entrez data ===========================
				url = 'http://www.proteinatlas.org/%s/gene' % gene
				# parses out the tissue specificity data from each URL
				html = urllib.urlopen(url).read()
				soup = BeautifulSoup(html)
				# find the right header in the table, work up to the row
				row = soup.find(text='Entrez gene summary').parent.parent.parent
				#get the content of the cell
				result['entrez_data'] = row.td.string
				print 'ENTREZ_DATA: %s\n' % result['entrez_data']
				
				# get the gene info ===============================
				url = 'http://www.proteinatlas.org/search/%s' % gene
				#parses out the Gene Name from each page
				soup = BeautifulSoup(urllib.urlopen(url).read())
				# find the right row in the table, extract our data
				row = soup.find('tr',attrs={'class':'odd'})
				result['gene_name'] = row.findAll('td')[0].text
				result['gene_desc'] = row.findAll('td')[1].text
				result['protein_class'] = row.findAll('td')[2].text
				print 'GENE_NAME: %s\n' % result['gene_name']
				print 'GENE_DESC: %s\n' % result['gene_desc']
				print 'PROTEIN_CLASS: %s\n' % result['protein_class']
				
				# get the protein summary ==========================
				url = 'http://www.proteinatlas.org/%s' % gene
				# parses out the tissue specificity data from each URL
				html = urllib.urlopen(url).read()
				soup = BeautifulSoup(html)
				# find the th by its text
				header = soup.find(text='Protein summary')
				# get the associated tr by traversing up three levels
				row = header.parent.parent.parent
				# get the td contents and strip them to create plain text
				result['protein_expr'] = stripTagsAndJoin(row.td.contents)
				print 'PROTEIN_EXPR: %s\n' % result['protein_expr']
				
				results.append(result)
				print '='*60
	
		with open(outfile , 'wb') as f: #create output file to write to here
			fieldnames = ['ensg_id','gene_name','gene_desc','protein_class','entrez_data','protein_expr']
			writer = csv.DictWriter(f, dialect='excel',fieldnames=fieldnames)
			writer.writerow(dict((fn,fn) for fn in fieldnames))
			for result in results:
				writer.writerow(result)
				
		print 'Done.'

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

def fileIsWriteable(filePath):
	try:
		f = open(filePath , 'ab')
		f.close()
		return True
	except Exception,e:
		print e
		return False
	
if __name__ == '__main__':
	if len(sys.argv) != 3:
		print 'usage: %s <input_file> <output_file>' % os.path.basename(sys.argv[0])
		exit()
	else:
		inFile = sys.argv[1]
		outFile = sys.argv[2]
		
		if not fileIsWriteable(outFile):
			print 'The output file %s is not writeable -- is it open?' % outFile
			sys.exit()

		main(inFile,outFile)
