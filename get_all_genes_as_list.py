#!/usr/bin/env python

"""get_all_genes_as_list.py: will retrieve all the valid ensg ids and save to a text file

usage: get_all_genes_as_list.py
"""
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

# CHANGE LOG:
# 2018-04-19 TC created script  

from future import standard_library
standard_library.install_aliases()
from builtins import str

__author__ = "Toby Cornish"
__copyright__ = "Copyright 2017, Johns Hopkins University"
__credits__ = ["Toby Cornish"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Toby C. Cornish"
__email__ = "tcornish@gmail.com"

from api_client import get_genes

def main():
	out_file = 'all_ensg_ids.txt'
	ensg_ids = get_genes()
	print('retrieved %s gene ids.' % len(ensg_ids))
	print('writing to file %s...' %out_file)
	with open(out_file,'w') as f:
		for ensg_id in ensg_ids:
			f.write(ensg_id+'\n')
	print('done.')

if __name__ == '__main__':
	main()