# Software to identify the gene name from ProteinAtlas IDs.
# Created 6-7-13 by Marc Halushka (with major help from Toby Cornish who will not
# claim any of this awful coding as his own). Based on proteinatlas.py
# This takes a .txt file of ENGS IDs and ouputs gene names and description

import urllib
from bs4 import BeautifulSoup
import urlparse
import mechanize
import csv
import sys

fileIN = open("data/INPUT_FILE_NAME_HERE.txt", "r")  # Input file name
atlasline = fileIN.readline()

results = [] # declare this here so that it is scoped outside of the while block
while atlasline:     #starts loop
#makes sequential URLs from file of IDs
  atlasline = atlasline.strip()
  url = 'http://www.proteinatlas.org/search/'+atlasline
  protein = "http://www.proteinatlas.org"
  print "\n"
  print atlasline
  print url

#parses out the Gene Name from each page
  br = mechanize.Browser()
  br.open(url)
  soup = BeautifulSoup(urllib.urlopen(url).read())
  linkSpan = soup.findAll("tbody", {"class" : "hover"})
  for tbody in linkSpan:
    rows = tbody.findAll('td')
    for tr in rows:
      cols = tr.findAll ('a')
      for a in cols:
        nameID = a.renderContents()
  print nameID
  results.append([atlasline,nameID])  # add this image result to results
  atlasline = fileIN.readline()   #finishes loop

fileIN.close()
 
with open("data/OUTPUT_FILE_HERE.csv" , "wb") as f: #create output file to write to here
  fieldnames = ["ENSGID","Gene ID"]
  output = csv.writer(f, dialect='excel')
  output.writerow(fieldnames)
  for result in results: # still has the results b/c it was declared outside the while block
    output.writerow(result)
    
   
print "Complete"

