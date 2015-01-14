#!/usr/bin/env python

"""image_viewer.py: uses pygame to view jpg images in a folder, and tag images that meet the user's criteria.  The image path to a selected image is recorded as a row in the output csv file.

The HPA image download script in this suite embeds metadata (ensg_id, antibody, etc.) as json in the image file's Exif.UserComment tag. This script uses that Exif data to populate the corresponding columns in the output_file.  If the metadata is not in the image, those columns will be blank.

If a gamepad/joystick is plugged in, it will be detected (the first one found will be used).  The gamepad/joystick left and right go forward and backward through images. Other buttons are configurable under BUTTON_BINDINGS in this file.  The script will print the button being pressed to stdout if you need to know the number scheme for your gamepad/joystick, and want to remap the buttons for your gamepad (very likely).

The keyboard can be used as well. The keys can be remapped in this file under KEY_BINDINGS. A complete list of all pygame key events can be found at http://www.pygame.org/docs/ref/key.html

Default key bindings are: LEFT ARROW goes to previous image. RIGHT ARROW goes to next image. SPACE BAR selects. The MINUS key zooms out.  The EQUALS (unshifted plus) key zooms in. The ESCAPE key exits and closes the window.

The output file is a CSV file (with header) listing one row for each that was selected by the user. The file is appended as each image is selected. Columns are:

  image_file: the name of the image file downloaded
  ensg_id: the Ensembl gene id
  tissue: the tissue represented in the image
  antibody: the id of the antibody in the image
  image_url: the HPA url the image was downloaded from

The score will be displayed in an animation, this can be shut off by setting animate to False

Finally, if the default zoom level (33% or 0.33) is not appropriate for your monitor, you can change that setting in this file as well.

usage: image_viewer.py <input_dir> <output_file>
"""
# CHANGE LOG:
# 06-18-2013 MK initial build
# 08-29-2013 TC clean up and standardize code
# 07-11-2014 TC additional code clean up and documentation
# 07-23-2014 TC refactor code
# 08-05-2014 TC added exif metadata reading and handling

__author__ = "Marc Halushka, Toby Cornish"
__copyright__ = "Copyright 2014, Johns Hopkins University"
__credits__ = ["Marc Halushka", "Toby Cornish"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Toby Cornish"
__email__ = "tcornis3@jhmi.edu"

import os
import sys
import pygame
import math
import csv
import json
import pyexiv2

import time

# KEY_BINDINGS
selectKey = pygame.K_SPACE
nextKey = pygame.K_RIGHT
prevKey = pygame.K_LEFT
exitKey = pygame.K_ESCAPE
zoomInKey = pygame.K_MINUS
zoomOutKey = pygame.K_EQUALS

# BUTTON_BINDINGS
# joy/pad left and right are next and prev, respectively
# joy/pad up and down are zoom in and out, respectively
selectButton = 2
zoomInButton = 3
zoomOutButton = 1

# GLOBALS
defaultScale = 0.33
imageExtensions = ['.jpg','.JPG',]
animate = True

def main(indir,outfile):
	#initialize pygame and controller if present
	pygame.init()
	pygame.joystick.init()
	identifyGamepad()

	#identify files; quit if no image files found
	files = getImageFiles(indir,imageExtensions)
	numImages = len(files)
	if numImages < 1:
		print 'No image files found in input directory.'
		sys.exit()

	images = readAllImageMetadata(files)

	#initialize variables
	scale = defaultScale
	i = 0
	screen = reset_screen((200,200)) #to initialize the pygame screen
	fullImage = pygame.image.load(images[i]['image_path']).convert()

# Initialise clock
	clock = pygame.time.Clock()

	while True: #pygame loop
		clock.tick(10)
		title = '%s of %s : %s : %.2f%%' % (i+1,numImages,images[i]['image_file'],scale*100)
		for e in pygame.event.get(): #check the event loop
			if e.type == pygame.QUIT:
				sys.exit()
			if e.type == pygame.KEYDOWN:
				if e.key == exitKey:
					sys.exit()
				if e.key == zoomInKey: #zoom out
					scale = scale / 1.5
				if e.key == zoomOutKey: #zoom in
					scale = scale * 1.5
				if e.key == selectKey: #save and advance
					selectImage(outfile,images,i)
					animateText(fullImage,title,scale,'Selected')
					fullImage,i = nextImage(images,i)
				if e.key == nextKey: #advance
					fullImage,i = nextImage(images,i)
				if e.key == prevKey: #previous
					fullImage,i = prevImage(images,i)

			if e.type == pygame.JOYBUTTONDOWN:
				print("Joystick button % s pressed." % e.dict['button'])
				if e.dict['button'] == selectButton and i < numImages-1: #save and advance
					selectImage(outfile,images,i)
					animateText(fullImage,title,scale,'Selected')
					fullImage,i = nextImage(images,i)
				if e.dict['button'] == zoomInButton: #zoom in
					scale = scale * 1.5
				if e.dict['button'] == zoomOutButton: #zoom out
					scale = scale / 1.5

			if e.type == pygame.JOYAXISMOTION:
				print("Joystick axis %s" % e.dict['axis'])
				print("Joystick value %s" % e.dict['value'])
				#axis: X = 0
				value = int(round(e.dict['value']))
				if e.dict['axis'] == 0:
					if value > 0 and i < numImages-1:
						fullImage,i = nextImage(images,i)
					elif value < 0 and i > 0:
						fullImage,i = prevImage(images,i)
				#axis: Y = 1
				if e.dict['axis'] == 1:
					if value < 0:
						scale = scale * 1.5
					elif value > 0:
						scale = scale / 1.5
				print i

			if e.type == pygame.JOYHATMOTION:
				print("Joystick hat %s" % e.dict['hat'])
				print("Joystick hat value %s, %s" % e.dict['value'])
				x = e.dict['value'][0]
				y = e.dict['value'][1]
				#right-left axis:
				if x > 0 and i < numImages-1:
						fullImage,i = nextImage(images,i)
				elif x < 0 and i > 0:
						fullImage,i = prevImage(images,i)

		showImage(fullImage,'%s of %s : %s : %.2f%%' % (i+1,numImages,images[i]['image_file'],scale*100),scale)
		pygame.display.flip()
		pygame.time.delay(25)

def showImage(fullImage,title,scale):
	scaledImage = scaleImage(fullImage,scale)
	screen = reset_screen((scaledImage.get_width(), scaledImage.get_height()))
	addTextToImage(scaledImage,title)
	screen.blit(scaledImage, (0,0))

def scaleImage(fullImage,scale):
	(w,h) = fullImage.get_rect().size
	(w,h) = scaleTuple(fullImage.get_rect().size,scale)
	scaledImage = pygame.transform.scale(fullImage, (w,h))
	return scaledImage

def addTextToImage(surf,s):
	font = pygame.font.Font(None, 36)
	text = font.render(s, 1, (255, 0, 0))
	textpos = text.get_rect()
	textpos.centerx = surf.get_rect().centerx
	surf.blit(text, textpos)

def selectImage(outfile,images,i):
	print 'selectImage -> %s' % images[i]['image_file']
	writeResult(outfile,images,i)

def animateText(fullImage,title,scale,animateString):
	if animate:
		scaledImage = scaleImage(fullImage,scale)
		scaledH = scaledImage.get_height()
		scaledW = scaledImage.get_width()
		addTextToImage(scaledImage,title)
		#do some calculations to better fit the fontsize to the image size
		startSize = int(round(36*scale))
		endSize = int(round(scaledH))
		stepSize = int(round((endSize - startSize)/20)) #divide into 20 steps
		for size in range(startSize,endSize,stepSize): # animate the text
			screen = reset_screen((scaledImage.get_width(), scaledImage.get_height()))
			screen.blit(scaledImage, (0,0))
			font = pygame.font.Font(None, size)
			text = font.render(str(animateString), 1, (255, 0, 0))
			textpos = text.get_rect()
			if textpos.width >= scaledW:
				#if we have reach the width of the scaledImage, break the animation
				break
			textpos.centerx = scaledImage.get_rect().centerx
			textpos.centery = scaledImage.get_rect().centery
			screen.blit(text, textpos)
			pygame.display.flip()
			pygame.time.delay(1)

def writeResult(outfile,images,i):
	with open(outfile,'a+b') as f:
		#open with a+ mode, read at beginning, write at the end
		fieldnames = ['image_file','ensg_id','tissue','antibody','image_url']
		writer = csv.DictWriter(f, dialect='excel',fieldnames=fieldnames,extrasaction='ignore')
		lineCount = 0
		for lineCount,l in enumerate(f):
			pass
		if lineCount == 0: #if the file length is zero lines, write the header
			writer.writerow(dict((fn,fn) for fn in fieldnames))
		writer.writerow(images[i])

def nextImage(images,i):
	print 'nextImage   -> %s' % images[i]['image_file']
	i += 1
	if i > len(images) - 1:
		i = len(images) - 1
	fullImage = pygame.image.load(images[i]['image_path']).convert()
	return fullImage,i

def prevImage(images,i):
	print 'prevImage   -> %s' % images[i]['image_file']
	i -= 1
	if i < 0:
		i = 0
	fullImage = pygame.image.load(images[i]['image_path']).convert()
	return fullImage,i

def scaleTuple(tup,scale):
	return tuple([int(round(scale*i)) for i in tup])

def reset_screen(res) :
	screen = pygame.display.set_mode(res)
	pygame.display.set_caption("HPASubC image_viewer")
	return screen

def getImageFiles(dir,exts):
	files = []
	for file in os.listdir(dir):
		if os.path.splitext(file)[1] in exts:
			print file
			files.append(os.path.join(dir,file))
	return files

def readAllImageMetadata(files):
	images = []
	print 'Reading image file metadata...'
	for filePath in files:
		image = readExifUserComment(filePath)
		image['image_path'] = filePath
		images.append(image)
	print '  done.'
	return images

def readExifUserComment(imagePath):
	# read in the exif data, convert the user comment from json to dict, return it
	# use empty values if the data isn't found
	userComment = {	'ensg_id' : '',
									'tissue' : '',
									'protein_url' : '',
									'image_url' : '',
									'antibody' : '',
									'image_file' : '',
								}
	try:
		metadata = pyexiv2.ImageMetadata(imagePath)
		metadata.read()
		userComment = json.loads(metadata['Exif.Photo.UserComment'].value)
	except Exception, e:
		# the tag or exif isn't there, return the empty one
		pass
	return userComment

def identifyGamepad():
	if pygame.joystick.get_count() > 0:
		print 'found %s gamepad(s).' % pygame.joystick.get_count()
		joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
		for i,j in enumerate(joysticks):
			pygame.joystick.Joystick(i).init()
			print
			print 'Gamepad %s, : %s' % (i,j.get_name())
			print '  found %s axes (%s joysticks)' % (j.get_numaxes(),j.get_numaxes()/2)
			print '  found %s buttons' % j.get_numbuttons()
			numhats = j.get_numhats()
			print '  found %s hats' % numhats
			print
	else:
		print 'No joysticks found!'

if __name__ == '__main__':
	if len(sys.argv) != 3:
		print 'usage: %s <input dir> <output file>' % os.path.basename(sys.argv[0])
		exit()
	else:
		main(sys.argv[1],sys.argv[2])
