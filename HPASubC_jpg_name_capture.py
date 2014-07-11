# Software to parse any organ .jpg image names from ProteinAtlas IDs
# Created 5-22-13 by Marc Halushka and Toby Cornish.
# All rights reserved. No warranties are given or implied.

import urllib
from bs4 import BeautifulSoup
import urlparse
import mechanize
import csv
import sys

# User generated .txt file of ENSG IDs must be supplied
fileIN = open("data/INPUT_FILE_NAME.txt", "r")   # USER ACTION Input file name and location must be changed to appropriate.
atlasline = fileIN.readline()

results = [] # declare this here so that it is scoped outside of the while block
while atlasline:     #starts loop
#makes sequential URLs from file of IDs
  atlasline = atlasline.strip()
  url = 'http://www.proteinatlas.org/'+atlasline +'/tissue/heart+muscle'  # USER ACTION The last part of the url needs to be changed as described in the READ ME.  
  protein = "http://www.proteinatlas.org"
  print "\n"
  print atlasline
  print url

#parses out the .jpeg images from each page
  br = mechanize.Browser()
  br.open(url)
  soup = BeautifulSoup(urllib.urlopen(url).read())
  linkSpan = soup.findAll("table", {"class" : "border dark"})
  for table in linkSpan:
    rows = table.findAll('tr')
    for tr in rows:
      cols = tr.findAll('a')
      for a in cols:
        imageUrl = protein+a.renderContents().strip('<img height="300"').strip('" width="300"/>').strip('src="')
        results.append([atlasline,url,imageUrl]) # add this image result to results
 
  atlasline = fileIN.readline()   #finishes loop

fileIN.close()
 
with open("data/OUTPUT_FILE_NAME.csv" , "wb") as f: # USER ACTION The name of the .csv output file to be changed to appropriate.
  fieldnames = ["proteinID","proteinURL","image"]
  output = csv.writer(f, dialect='excel')
  output.writerow(fieldnames)
  for result in results: # still has the results b/c it was declared outside the while block
    output.writerow(result)
    
   
print "Complete"

