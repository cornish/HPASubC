#!/usr/bin/env python

"""image_scorer.py: uses pygame to view jpg images in a folder, and associate a score with the image.  The image path to a selected image adn the score are recorded in a row in the output csv file.

Default key bindings are: LEFT ARROW goes to previous image. RIGHT ARROW goes to next image. SPACE BAR selects. The MINUS key zooms out.  The EQUALS (unshifted plus) key zooms in. The ESCAPE key exits and closes the window. SPACE and 0 are defined as '0', and '1','2','3','4', and '5' are the scores 1 to 5, respectively. The keys can be remapped in this file under KEY_BINDINGS. The script supports arbitrary key bindings defined in the scoreKeys dict. For example, arbitrary strings such as 'cancer' or 'normal' could also be bound to keys instead of numeric scores. 

A complete list of all pygame key events can be found at ttp://www.pygame.org/docs/ref/key.html 

The output file is a CSV file (with header) listing the file path for the selected images and the score assigned. The file is appended as each image as scored.

The score will be displayed in an animation, this can be shut off by setting animate to False

Finally, if the default zoom level (33% or 0.33) is not appropriate for your monitor, you can change that setting in this file as well.

usage: image_scorer.py <input dir> <output file>
"""
# CHANGE LOG:
# 06-18-2013 MK initial build
# 08-29-2013 TC clean up and standardize code
# 07-11-2014 TC additional code clean up and documentation
# 07-24-2014 TC refactor code

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
nextKey = pygame.K_RIGHT
prevKey = pygame.K_LEFT
exitKey = pygame.K_ESCAPE
zoomInKey = pygame.K_MINUS
zoomOutKey = pygame.K_EQUALS
#change the values in this dict to associate a key with a score
#multiple keys can be associated with a score and "score" could be changed to another string value such as a diagnosis or feature
scoreKeys = { 	pygame.K_0 : '0',
								pygame.K_SPACE : '0',
								pygame.K_1 : '1',
								pygame.K_2 : '2',
								pygame.K_3 : '3',
								pygame.K_4 : '4',
								pygame.K_5 : '5'
						}
						
# GLOBALS
defaultScale = 0.33
imageExtensions = ['.jpg','.JPG',]
animate = True

def main(indir,outfile):
	#initialize pygame
	pygame.init()
	
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
		font = pygame.font.Font(None, 36)
		for e in pygame.event.get() :
			if e.type == pygame.QUIT :
				sys.exit()
			if e.type == pygame.KEYDOWN :
				if e.key == exitKey :
					sys.exit()
				if e.key == zoomInKey: #zoom out
					scale = scale / 1.5
				if e.key == zoomOutKey: #zoom in
					scale = scale * 1.5
				if e.key in scoreKeys.keys():
					score = scoreKeys[e.key]
					print score
					screen = pygame.display.get_surface()
					animateText(fullImage,title,scale,score)
					writeResult(outfile,[files[i],score])
					fullImage,i = nextImage(files,i)

		showImage(fullImage,title,scale)
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
		fieldnames = ['Image','score']
		writer = csv.writer(f, dialect='excel')
		lineCount = 0
		for lineCount,l in enumerate(f):
			pass
		if lineCount == 0: #if the file length is zero lines, write the header
			writer.writerow(fieldnames)
		writer.writerow(result) 
		
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

def reset_screen(res):
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
	
	
if __name__ == '__main__':
	if len(sys.argv) != 3:
		print 'usage: %s <input dir> <output file>' % os.path.basename(sys.argv[0])
		exit()
	else:
		main(sys.argv[1],sys.argv[2])
