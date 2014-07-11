# Software to download the images from Protein Atlas as taken from the
# previously made .csv file of image names in HPASubC_jpg_name_capture.py
# Created on 5-23-13 by Marc Halushka and Toby Cornish
# All rights reserved. No warranties are given or implied.

import urllib

#call up jpg from list
f = open("data/YOUR_NAME_HERE.csv","r") # USER ACTION Input file name and location must be changed to appropriate.
url = f.readline()
while url:

    print url
    # clean up the URL to make a saveable jpg name
    url1 = url.strip('http://www.proteinatlas.org/images/')
    url2 = url1.replace('/', '_')

    resp = urllib.urlopen(url)
    image_data = resp.read()
    # Open output file in binary mode, write, and close.
    fout = open("data/"+url2.rstrip(),'wb')
    fout.write(image_data)
    fout.close()

    url = f.readline()

f.close()
print "all done"
