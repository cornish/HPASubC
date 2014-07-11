# method to peruse images quickly using a joystick and keep a file of ones having certain
# qualities.  Written by Toby Cornish and tweaked by Marc Halushka 5.31.13
# buttons are left to go back, right to go forward and 3 to save to list and go forward
# 2 zooms in (digital) and up arrow returns to normal zoom
# optimized for an image size of 1200 pixels.
# output file name goes in two places
# should be run from within the same folder as the images

import os
import sys
import pygame
import math
import csv


def reset_screen(res) :
    screen = pygame.display.set_mode(res)
    pygame.display.set_caption("pyview")
    return screen

fields = open("OUTPUT_FILE_HERE.csv" , "w") # USER ACTION Output file name and location must be changed to appropriate.
fieldnames = ["ICD Image"]
output = csv.writer(fields, dialect='excel')
output.writerow(fieldnames)
fields.close()


imgfile = ""

pygame.init()
pygame.joystick.init()

print 'found %s joystick(s).' % pygame.joystick.get_count()

pygame.joystick.Joystick(0).init()

rec=0

files = []

for file in os.listdir('.'):
    if os.path.splitext(file)[1] == '.jpg':
        print file
        files.append(file)

i = 0

S = pygame.image.load(files[i])
screen = reset_screen((S.get_width(), S.get_height()))
S = S.convert() # Need screen init

while True :
    # Display some text
    
    font = pygame.font.Font(None, 36)
    text = font.render(files[i], 1, (255, 0, 0))
    textpos = text.get_rect()
    textpos.centerx = S.get_rect().centerx
    S.blit(text, textpos)
    for e in pygame.event.get() :
        if e.type == pygame.QUIT :
            sys.exit()
        if e.type == pygame.KEYDOWN :
            if e.key == pygame.K_ESCAPE :
                sys.exit()
            if e.key == pygame.K_MINUS :
                S = pygame.transform.scale(S, (S.get_width()/2, S.get_height()/2))
                screen = reset_screen((S.get_width(), S.get_height())) #for scaling image
            if e.key == pygame.K_EQUALS :
                S = pygame.transform.scale(S, (S.get_width()*2, S.get_height()*2))
                screen = reset_screen((S.get_width(), S.get_height()))
        if e.type == pygame.JOYBUTTONDOWN:
            print("Joystick button % s pressed." % e.dict['button'])
            if e.dict['button'] == 2 and i < len(files)-1:     #button 3 on controller to save and advance
                            results = files[i]
                            i = i + 1
                            print "Picked!"
                            print results
                            with open("OUTPUT_FILE_HERE.csv" , "ab") as f: # USER ACTION Output file name and location must be changed to appropriate as above.
                             output = csv.writer(f, dialect='excel')
                             output.writerow([results]) 
                            S = pygame.image.load(files[i])
                            screen = reset_screen((S.get_width(), S.get_height()))
            if e.dict['button'] == 1:
             S = pygame.transform.scale(S, (S.get_width()*2, S.get_height()*2))
             screen = reset_screen((S.get_width(), S.get_height()))  
                            
        
        if e.type == pygame.JOYAXISMOTION:
                # axis: X = 0
            print("Joystick axis %s" % e.dict['axis'])
            print("Joystick value %s" % e.dict['value'])
            value = int(round(e.dict['value']))
            if e.dict['axis'] == 0:
                if value > 0 and i < len(files)-1:
                    i = i + 1
                elif value < 0 and i > 0:
                    i = i - 1
            print i
            S = pygame.image.load(files[i])
            screen = reset_screen((S.get_width(), S.get_height()))
           
                
    screen.blit(S, (0,0))
    textpos = text.get_rect()
    textpos.centerx = S.get_rect().centerx
    S.blit(text, textpos)

    pygame.display.flip()
    pygame.time.delay(25)
