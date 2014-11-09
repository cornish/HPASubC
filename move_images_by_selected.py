#!/usr/bin/env python

"""move_images_by_selected.py: move images in a folder have a particular value of selected (TRUE,FALSE,None) in a provided csv file.

This is meant to be used on the output of the image_viewer.py script

The input file is a CSV file (with header) with at least these columns:

	image_file: the name of the image file
	selected: TRUE or FALSE (or something else?

This script will move images in the input_dir to the output_dir a value

usage: move_images_by_selected.py <input_dir> <output_dir> <value>
"""
# CHANGE LOG:
# 11-09-2014 TC created, re-used bits of image_viewer.py code

__author__ = "Marc Halushka, Toby Cornish"
__copyright__ = "Copyright 2014, Johns Hopkins University"
__credits__ = ["Marc Halushka", "Toby Cornish"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Toby Cornish"
__email__ = "tcornis3@jhmi.edu"

import os
import sys
import csv
import shutil

def main(indir,outdir,inputFile,value):

	imageExtensions = ['.jpg','.JPG',]
	images = getImageFiles(indir,imageExtensions)

	imagesTrue = []
	imagesFalse = []
	imagesOther = []
	imagesAll = []

	try:
		with open(inputFile,'rb') as f:
			reader = csv.DictReader(f)
			for row in reader:
				imagesAll.append(row['image_file'])
				if row['selected'] == 'True':
					imagesTrue.append(row['image_file'])
				elif row['selected'] == 'False':
					imagesFalse.append(row['image_file'])
				else:
					imagesOther.append(row['image_file'])
	except Exception,e:
		#catch error reading the file
		print '\nAn error occurred reading the input file %s :\n' % inputFile
		print e

	print '\nFound %s images in file %s total' % (len(imagesAll),inputFile)
	print 'Found %s images in file %s with value TRUE' % (len(imagesTrue),inputFile)
	print 'Found %s images in file %s with value FALSE' % (len(imagesFalse),inputFile)
	print 'Found %s images in file %s with some other value' % (len(imagesOther),inputFile)

	trueIntersection = set(images).intersection(imagesTrue)
	falseIntersection = set(images).intersection(imagesFalse)
	otherIntersection = set(images).intersection(imagesOther)
	noneIntersection = set(images).difference(imagesAll)

	print '\nFound %s images in directory %s with value TRUE' % (len(trueIntersection),indir)
	print 'Found %s images in directory %s with value FALSE' % (len(falseIntersection),indir)
	print 'Found %s images in directory %s with some other value' % (len(otherIntersection),indir)
	print 'Found %s images in directory %s not in file %s\n' % (len(noneIntersection),indir,inputFile)

	if value == "TRUE":
		moveFileList(indir,outdir,trueIntersection)
	elif value == "FALSE":
		moveFileList(indir,outdir,falseIntersection)
	elif value == "OTHER":
		moveFileList(indir,outdir,otherIntersection)
	elif value == "NONE":
		moveFileList(indir,outdir,noneIntersection)

	sys.exit()

def moveFileList(inDir,outDir,fileList):
	for file in fileList:
		sourcepath = os.path.join(inDir,file)
		destpath = os.path.join(outDir,file)
		print 'Moving %s to %s ...' % (sourcepath,destpath)
		try:
			shutil.move(sourcepath, destpath)
		except (OSError, IOError), e:
			print '  Error moving %s to %s: %s' % (sourcepath, destpath, e)

def getImageFiles(dir,exts):
	files = []
	for file in os.listdir(dir):
		if os.path.splitext(file)[1] in exts:
			files.append(file)
	return files

if __name__ == '__main__':
	if len(sys.argv) != 5:
		print '\nusage: %s <input dir> <output dir> <input file> <value>' % os.path.basename(sys.argv[0])
		print '\n       <value> can be: TRUE, FALSE, OTHER or NONE\n'
		sys.exit()
	else:
		inputDir = sys.argv[1]
		outputDir = sys.argv[2]
		inputFile = sys.argv[3]
		value = sys.argv[4].upper()
		if value not in ['TRUE','FALSE','OTHER','NONE']:
			print '\n%s is not a valid value!\n\n<value> can be: TRUE, FALSE, OTHER or NONE' % value
			sys.exit()

	if not os.path.isfile(inputFile):
		print 'The input file %s does not exist.' % inputFile
		sys.exit()

	try:
		if not os.path.exists(outputDir):
			# make the directory if it doesn't exist
			os.makedirs(outputDir)
	except Exception,e:
		#catch error making directory
		print e
		print 'Error creating directory %s' % outputDir
		sys.exit()

	main(inputDir,outputDir,inputFile,value)
