#!/usr/bin/env python

"""get_all_genes_as_list.py: will retrieve all the valid ensg ids and save to a text file

usage: get_all_genes_as_list.py [hpa_version]

currently supported hpa_versions are 18 and 19; if omitted, it defaults to 19
"""
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

# CHANGE LOG:
# 2018-04-19 TC created script
# 2020-08-26 TC updated to support multiple hpa versions; added argument parser

from future import standard_library
standard_library.install_aliases()
from builtins import str
import argparse

__author__ = "Toby Cornish"
__copyright__ = "Copyright 2017-2020"
__credits__ = ["Toby Cornish"]
__license__ = "GPL"
__version__ = "1.1.0"
__maintainer__ = "Toby C. Cornish"
__email__ = "tcornish@gmail.com"

from api_client import get_genes

valid_hpa_versions = [18,19] #restricts valid commandline arguments

def main(hpa_version):
	out_file = 'all_ensg_ids_v%s.txt' % hpa_version
	ensg_ids = get_genes(hpa_version)
	print('retrieved %s gene ids.' % len(ensg_ids))
	print('writing to file %s...' % out_file)
	with open(out_file,'w') as f:
		for ensg_id in ensg_ids:
			f.write(ensg_id+'\n')
	print('done.')

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument("-v", "--hpa_version", help='HPA version, valid options are 18 or 19',
						type=int, choices=valid_hpa_versions, default=max(valid_hpa_versions))
	return parser.parse_args()


if __name__ == '__main__':
	# parse our command line arguments
	args = parse_args()
	main(args.hpa_version)