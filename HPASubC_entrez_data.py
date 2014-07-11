# Software to identify protein related information from ProteinAtlas IDs.
# Program will search for and return the Entrez summary from HPA if it exists.
# Created 6-18-13 by Marc Halushka
# Based on HPASubC_protein_name_grab.py


import urllib
from sgmllib import SGMLParser
import csv

fileIN = open("data/INPUT_FILE.txt", "r")   #Your input file name here
atlasline = fileIN.readline()

results = [] # declare this here so that it is scoped outside of the while block
while atlasline:     #starts loop
#makes sequential URLs from file of IDs
  atlasline = atlasline.strip()
  url = 'http://www.proteinatlas.org/'+atlasline
  protein = "http://www.proteinatlas.org"
# print "\n"
  print atlasline
# parses out the tissue specificity data from each URL
  celldata = urllib.urlopen(url) 
  htmlSource = celldata.read()
  celldata.close()
  str1 = htmlSource
  str2 = "Entrez gene summary"
  joe = str1.find(str2)
  str3 = "External links"
  lois = str1.find(str3)
 # print str1.find(str2)
 # print str1.find(str3)
 # print "\n"
  liz = htmlSource[joe+60: lois-46]
  print htmlSource[joe+60: lois-46]

  results.append([atlasline,liz])  # add this data result to results
  atlasline = fileIN.readline()   #finishes loop

fileIN.close()

with open("data/OUTPUT_FILE_HERE.csv" , "wb") as f: #create output file to write to here
  fieldnames = ["ENSGID","Entrez data"]
  output = csv.writer(f, dialect='excel')
  output.writerow(fieldnames)
  for result in results: # still has the results b/c it was declared outside the while block
    output.writerow(result)
    
   
print "done with this"
