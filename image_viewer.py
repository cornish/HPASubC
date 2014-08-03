#!/usr/bin/env python

"""image_viewer.py: uses pygame to view jpg images in a folder, and tag images that meet the user's criteria.  The image path to a selected image is recorded as a row in the output csv file.

If a gamepad/joystick is plugged in, it will be detected (the first one found will be used).  The gamepad/joystick left and right go forward and backward through images. Other buttons are configurable under BUTTON_BINDINGS in this file.  The script will print the button being pressed to stdout if you need to know the number scheme for your gamepad/joystick, and want to remap the buttons for your gamepad (very likely).

The keyboard can be used as well. The keys can be remapped in this file under KEY_BINDINGS. A complete list of all pygame key events can be found at http://www.pygame.org/docs/ref/key.html 

Default key bindings are: LEFT ARROW goes to previous image. RIGHT ARROW goes to next image. SPACE BAR selects. The MINUS key zooms out.  The EQUALS (unshifted plus) key zooms in. The ESCAPE key exits and closes the window.

The output file is simply a csv-format file (with header) listing all file paths for the selected images. The file is appended as each selection is made.
 
The score will be displayed in an animation, this can be shut off by setting animate to False
 
Finally, if the default zoom level (33% or 0.33) is not appropriate for your monitor, you can change that setting in this file as well.

usage: image_viewer.py <input dir> <output file>
"""
# CHANGE LOG:
# 06-18-2013 MK initial build
# 08-29-2013 TC clean up and standardize code
# 07-11-2014 TC additional code clean up and documentation
# 07-23-2014 TC refactor code

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

# KEY_BINDINGS
selectKey = pygame.K_SPACE
nextKey = pygame.K_RIGHT
prevKey = pygame.K_LEFT
exitKey = pygame.K_ESCAPE
zoomInKey = pygame.K_MINUS
zoomOutKey = pygame.K_EQUALS

# BUTTON_BINDINGS (joy/pad left and right are next and prev, respectively)
selectButton = 2
zoomInButton = 1
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
	
	#initialize variables
	scale = defaultScale
	i = 0
	screen = reset_screen((200,200)) #to initialize the pygame screen
	fullImage = pygame.image.load(files[i]).convert()
	
	while True: #pygame loop
		title = '%s of %s : %s : %.2f%%' % (i+1,numImages,files[i],scale*100)
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
					selectImage(outfile,files,i)
					animateText(fullImage,title,scale,'Selected')
					fullImage,i = nextImage(files,i)
				if e.key == nextKey: #advance
					fullImage,i = nextImage(files,i)
				if e.key == prevKey: #previous
					fullImage,i = prevImage(files,i)
					
			if e.type == pygame.JOYBUTTONDOWN:
				print("Joystick button % s pressed." % e.dict['button'])
				if e.dict['button'] == selectButton and i < len(files)-1: #save and advance
					selectImage(outfile,files,i)
					animateText(fullImage,title,scale,'Selected')
					fullImage,i = nextImage(files,i)
				if e.dict['button'] == zoomInButton: #zoom in
					scale = scale * 1.5
				if e.dict['button'] == zoomButton: #zoom out
					scale = scale / 1.5

			if e.type == pygame.JOYAXISMOTION:
				#axis: X = 0
				print("Joystick axis %s" % e.dict['axis'])
				print("Joystick value %s" % e.dict['value'])
				value = int(round(e.dict['value']))
				if e.dict['axis'] == 0:
					if value > 0 and i < len(files)-1:
						fullImage,i = nextImage(files,i)
					elif value < 0 and i > 0:
						fullImage,i = prevImage(files,i)
				print i
				
		showImage(fullImage,'%s of %s : %s : %.2f%%' % (i+1,numImages,files[i],scale*100),scale)
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

def selectImage(outfile,files,i):
	print 'selectImage -> %s' % files[i]
	writeResult(outfile,files[i])

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
	
def writeResult(outfile,result):
	with open(outfile,'a+b') as f: 
		#open with a+ mode, read at beginning, write at the end
		fieldnames = ['Image']
		writer = csv.writer(f, dialect='excel')
		lineCount = 0
		for lineCount,l in enumerate(f):
			pass
		if lineCount == 0: #if the file length is zero lines, write the header
			writer.writerow(fieldnames)
		writer.writerow([result]) 

def nextImage(files,i):
	print 'nextImage   -> %s' % files[i]
	i += 1
	if i > len(files) - 1: 
		i = len(files) - 1
	fullImage = pygame.image.load(files[i]).convert()
	return fullImage,i
	
def prevImage(files,i):
	print 'prevImage   -> %s' % files[i]
	i -= 1
	if i < 0: 
		i = 0
	fullImage = pygame.image.load(files[i]).convert()
	return fullImage,i
			
def scaleTuple(tup,scale):
	return tuple([int(round(scale*i)) for i in tup])

def reset_screen(res) :
	screen = pygame.display.set_mode(res)
	pygame.display.set_caption("pyview")
	return screen

def getImageFiles(dir,exts):
	files = []
	for file in os.listdir(dir):
		if os.path.splitext(file)[1] in exts:
			print file
			files.append(os.path.join(dir,file))
	return files

def identifyGamepad():
	if pygame.joystick.get_count() > 0:
		print 'found %s joystick(s).' % pygame.joystick.get_count()
		pygame.joystick.Joystick(0).init()
	else:
		print 'No joysticks found!'

if __name__ == '__main__':
	if len(sys.argv) != 3:
		print 'usage: %s <input dir> <output file>' % os.path.basename(sys.argv[0])
		exit()
	else:
		main(sys.argv[1],sys.argv[2])
