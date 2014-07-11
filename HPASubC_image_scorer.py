# HPASubC_image_scorer
# Assigns values to TMA images
# v002	7/22/2013	first working version -- mh/tc 
# buttons are 0, 1, 2, 3, 4, 5
# 2 zooms in (digital) and up arrow returns to normal zoom
# optimized for an image size of 1200 pixels.
# 0 = Assigned value 1 (usually negative)
# 1 = Assigned value 2
# 2 = Assigned value 3
# 3 = Assigned value 4
# 4 = Assigned value 5
# 5 = Assigned value 6
# Should be run from the folder containing the images
# All rights reserved. No warranties are given or implied.

import os
import sys
import pygame
import math
import csv

def main():
	pygame.init()
	i = 0
	outFile = "OUTPUT_FILE.csv"  # USER ACTION Output file name and location must be changed to appropriate.
	
	files = getJpegs('.')
	(image,screen) = displayImage(files,i)
	
	fieldnames = ["Endo Image", "score"]
	with open(outFile, "wb") as f:
		output = csv.writer(f, dialect='excel')
		output.writerow(fieldnames)
	
	while True:
		font = pygame.font.Font(None, 36)
		for e in pygame.event.get() :
			if e.type == pygame.QUIT :
				sys.exit()
			if e.type == pygame.KEYDOWN :
				if e.key == pygame.K_ESCAPE :
					sys.exit()
				if e.key == pygame.K_MINUS :
					image = scaleImage(image,0.5)
					screen = resetScreen(image)
				if e.key == pygame.K_EQUALS :
					image = scaleImage(image,2)
					screen = resetScreen(image)
				if e.key == pygame.K_SPACE or e.key == pygame.K_0: #either 0 or space = 0
					showScore(screen,image,0)
					writeScore(outFile,files[i],0)
					i += 1
					(image,screen) = displayImage(files,i)
				if e.key == pygame.K_1 :
					showScore(screen,image,1)
					writeScore(outFile,files[i],1)
					i += 1
					(image,screen) = displayImage(files,i)
				if e.key == pygame.K_2 :
					showScore(screen,image,2)
					writeScore(outFile,files[i],2)
					i += 1
					(image,screen) = displayImage(files,i)
				if e.key == pygame.K_3 :
					showScore(screen,image,3)
					writeScore(outFile,files[i],3)
					i += 1
					(image,screen) = displayImage(files,i)
				if e.key == pygame.K_4 :
					showScore(screen,image,4)
					writeScore(outFile,files[i],4)
					i += 1
					(image,screen) = displayImage(files,i)
				if e.key == pygame.K_5 :
					showScore(screen,image,5)
					writeScore(outFile,files[i],5)
					i += 1
					(image,screen) = displayImage(files,i)
										
		screen.blit(image, (0,0))

		text = font.render(files[i], 1, (255, 0, 0))
		textpos = text.get_rect()
		textpos.centerx = screen.get_rect().centerx
		screen.blit(text, textpos)

		pygame.display.flip()
		pygame.time.delay(25)

def resetScreen(image) :
	screen = pygame.display.set_mode((image.get_width(), image.get_height()))
	pygame.display.set_caption("imageviewer")
	return screen

def displayImage(files,i):
	if i < len(files):
		image = pygame.image.load(files[i])
		screen = resetScreen(image)
		image = image.convert() # not sure what this does, but if not done things slow down
		return (image,screen)
	else:
		print 'Done.'
		sys.exit()
	
def scaleImage(image,scale):
	w = int(round(image.get_width()*scale))
	h = int(round(image.get_height()*scale))
	image = pygame.transform.scale(image, (w,h))
	return image				
	
def getJpegs(dir):
	files = []
	for file in os.listdir(dir):
		if os.path.splitext(file)[1] == '.jpg':
			print file
			files.append(file)
	return files

def writeScore(outFile,file,score):
	results = [file,score]
	with open(outFile, "ab") as f:
		output = csv.writer(f, dialect='excel')
		output.writerow(results)
	
def showScore(screen,image,score):
	print score
	for size in range(36,800,13): # animate the text
		screen.blit(image, (0,0))
		font = pygame.font.Font(None, size)
		text = font.render(str(score), 1, (255, 0, 0))
		textpos = text.get_rect()
		textpos.centerx = image.get_rect().centerx
		textpos.centery = image.get_rect().centery
		screen.blit(text, textpos)
		pygame.display.flip()
		pygame.time.delay(1)
	
if __name__ == "__main__":
	main()	
