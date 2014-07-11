HPASubC
=======

HPASubC: a suite of tools for user sub-classification of tissue images from the Human Protein Atlas

HPA SubC Software Package v1.0

----------------------------------
This is a Read Me / Compendium for the Human Protein Atlas (HPA) Subclassification (SubC) Python Software package.  This collection of Python Scripts were conceived of and programmed by Marc Halushka and Toby Cornish at Johns Hopkins University School of Medicine. This is free software in the public space. This suite of scripts has not been made in conjunction with the HPA, thus the HPA is in no way responsible for any data obtained through these methods. No warranties are given or implied.

----------------------------------
All scripts were written in Python 2.7.5 and are known to work in the IDLE shell.

1. HPASubC_jpg_name_capture.py
2. HPASubC_image_download.py
3. HPASubC_image_viewer.py
4. HPASubC_image_scorer.py
5. HPASubC_protein_name_grab.py
6. HPASubC_cell_info.py
7. HPASubC_entrez_data.py


----------------------------------
Required Python libraries:
BeautifulSoup
csv
math
mechanize
os
pygame
re
SGMLParser
sys
urllib
urllib2
ulrparse

----------------------------------
HPASubC_jpg_name_capture.py

This script will parse the HPA website URLs and deliver a list of .jpg images corresponding to whatever list of genes are to be searched.  This file requires a .txt input file of ENSG IDs. These can be obtained from normal_tissue.csv.zip found here: http://www.proteinatlas.org/about/download. Note that this file is over 1,300,000 rows and may not be opened directly and fully in Excel.  It can be opened in a text editor such as the free Notepad ++. However, the remove duplicates feature in Excel is a useful way to generate a collapsed and clean ENSG ID list.  The Biomart tool at Ensemble will identify gene names and parsing of this ENSG list can be performed here, if desired.

Requires: A .txt file containing a single column of ENSG IDs in the format of: ENSG00000198727 without a header.

Outputs: A .csv file with three columns - protein ID, protein URL and image URL.  This output file is used for HPASubC_image_download.py.

Use: The user needs to correct the input location and name from "data/INPUT_FILE_NAME.txt" (line 13) to their own needs and correct the output name "data/OUTPUT_FILE_NAME.csv" (line 43) to their own needs.  This can be done in a text editor such as Notepad ++.  Line 20 needs to be changed to the organ of interest using the following options:

tissue/liver
tissue/gallbladder
tissue/pancreas
tissue/oral+mucosa
tissue/salivary+gland
tissue/esophagus
tissue/stomach
tissue/duodenum
tissue/small+intestine
tissue/appendix
tissue/colon
tissue/rectum
tissue/kidney
tissue/urinary+bladder
tissue/testis
tissue/epididymis
tissue/prostate
tissue/seminal+vesicle
tissue/breast
tissue/vagina
tissue/cervix%2C+uterine
tissue/uterus
tissue/fallopian+tube
tissue/ovary
tissue/placenta
tissue/adipose+tissue
tissue/skin
tissue/skeletal+muscle
tissue/smooth+muscle
tissue/soft+tissue
tissue/bone+marrow
tissue/lymph+node
tissue/tonsil
tissue/spleen
tissue/cerebral+cortex
tissue/hippocampus
tissue/lateral+ventricle
tissue/cerebellum
tissue/thyroid+gland
tissue/parathyroid+gland
tissue/adrenal+gland
tissue/nasopharynx
tissue/bronchus
tissue/lung
tissue/heart+muscle
cancer/tissue/colorectal+cancer
cancer/tissue/breast+cancer
cancer/tissue/prostate+cancer
cancer/tissue/ovarian+cancer
cancer/tissue/cervical+cancer
cancer/tissue/endometrial+cancer
cancer/tissue/carcinoid
cancer/tissue/head+and+neck+cancer
cancer/tissue/thyroid+cancer
cancer/tissue/glioma
cancer/tissue/lymphoma
cancer/tissue/lung+cancer
cancer/tissue/melanoma
cancer/tissue/skin+cancer
cancer/tissue/testis+cancer
cancer/tissue/urothelial+cancer
cancer/tissue/renal+cancer
cancer/tissue/stomach+cancer
cancer/tissue/pancreatic+cancer
cancer/tissue/liver+cancer


----------------------------------
HPASubC_image_download.py

This script will download the HPA images from a .csv file obtained by the output file from HPASubC_jpg_name_capture.py.

Requires: A .csv file of HPA URLs in the format of: http://www.proteinatlas.org/images/11185/29968_B_5_6.jpg without a header.  

To get the prior file into this format, columns A, B and C were deleted and "_medium" was removed in Excel, for simplicity.  This can also be performed in R, Python, PERL or another language.  Note that images appear as medium and full-sized in HPA. Depending on one's monitor size, the medium size may be sufficient and would not require downloading the full sized image, which is generally larger than most large standard sized CRT monitors.

Outputs: A folder of downloaded .jpg images. 

User Note: This process takes a long time and is prone to fail if the internet connection is unstable. The recommendation is to subset the entire file and download images in small increments.

---------------------------------
HPASubC_image_viewer.py

This script will open all of the image files within a folder and allow them to be quickly scanned for any staining pattern of interest.  Images should be .jpgs and sized (optimized) to fit the viewing area of the monitor to be used. A program such as FastStone Photo Resizer can be used for this activity in advance of using this script.  This script requires a USB Sony PlayStation style joystick. (Finally a legitimate reason to have a video game controller on your desk).  The right and left arrow buttons allow one to scroll through the images.  Pressing button "3" (right side button on right side of controller) picks the image and saves it's url to a .csv file.

Requires: A folder of downloaded .jpg images.  Note: We use this HPASubC_image_viewer.py script directly in the image folder.

Outputs: A .csv file of all flagged images from the folder is the style of: "1040_2304_B_4_6.jpg"

User Note: We generally put 3,000 images in one folder and scan them in these smaller blocks.  After identifying all interesting images, we collate the output .csv files into a single file.  We use MS Excel and the CONCATENATE command to convert 11513_29348_B_4_6.jpg into http://www.proteinatlas.org/images/11513/29348_B_4_6.jpg.  Note the first _ character becomes a / character in the final version. This can be also probably be done in R, Perl or Python.  This file is then sent back through HPASubC_image_download.py to download the subset of interesting images into a new folder.

---------------------------------
HPASubC_image_scorer.py

This script allows one to assign a scoring value to each previously identified image.  The software has values 0-6, but can easily be expanded to incorporate more or fewer scoring values.  This can be used to reconfirm the image investigated on the quick first pass has the subcellular localization pattern of interest.  If it does have the correct pattern, the buttons can be used to assign values such as strong, medium, weak or any other parameter.  We recommend making a key in a .txt file to refer to when doing the scoring.

Requires: A folder of downloaded .jpg images. Note: We use this HPASubC_image_scorer.py script directly in the image folder.

Outputs: A .csv file with two columns: Endo Image and score that will look like: 10005_33907_B_4_6.jpg	2.

We use Excel and VLOOKUP commands to repopulate this file with ENSG ID values from early .csv files.  This can be done in R, Perl, Python or other languages.

---------------------------------
HPASubC_protein_name_grab.py

This is an optional script that returns the Gene ID (Symbol) based on the ENSG ID.

Requires: A .txt file list of ENGS IDs without a header in the style of: ENSG00000168685

Outputs: A .csv file containing two columns.  Column one is the ENSGID.  Column 2 contains the Gene ID. This is the format: ENSG00000102755	FLT1

This information can be combined with the data obtained above.

---------------------------------
HPASubC_cell_info.py

This is an optional script that will download parsed information from HPA regarding the reported expression pattern of each protein across the entirety of the TMAs.

Requires: A .txt file list of ENGS IDs without a header in the style of: ENSG00000168685

Outputs:  A .csv file containing two columns.  Column one is the ENSGID.  Column 2 contains cell type data reporting either "Staining in X out of Y" or "Expressed in "X out of Y"  HPA has two different terminologies. This data can be added to a final report regarding the specificity/ubiquitousness of a protein. 

This information can be combined with the data obtained above.

---------------------------------
HPASubC_entrez_data.py

This is an optional script that will download parse information from HPA regarding the reported Entrez data that can provide initial information about each gene/protein identified.

Requires:  A .txt file list of ENGS IDs without a header in the style of: ENSG00000168685

Outputs: A .csv file containin two columns.  Column 1 is the ENSGID.  Column 2 contains the Entrez data.  This is the format:
ENSG00000163840	DTX3L functions as an E3 ubiquitin ligase (Takeyama et al., 2003 [PubMed 12670957]).[supplied by OMIM, Nov 2009]

This information can be combined with the data obtained above.





