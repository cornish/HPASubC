HPASubC, v1.2.x 04/19/2018
==============
The Human Protein Atlas (HPA) Subcellular Classification (SubC) software package is a collection of python scripts by Marc Halushka at Johns Hopkins University and Toby C. Cornish at the University of Colorado. This suite of scripts has not been made in conjunction with the HPA, thus the HPA is in no way responsible for any data obtained through these methods. No warranties are given or implied.

Citing:
--------------
In addition to citing this GitHub repository (https://github.com/cornish/HPASubC), please cite the following paper:

Cornish TC, Chakravarti A, Kapoor A, Halushka MK. HPASubC: A suite of tools for user subclassification of human protein atlas tissue images. *J Pathol Inform* 2015;6:36.


Development Roadmap:
--------------
The 1.2.x release of HPASubC is essentially a patch/partial re-write of the existing project that has removed HPASubC's dependency on screen scraping the HPA website. Image metadata is now sourced via a RESTful API that serves a copy of the HPA data from a private server. This version is compatible with HPA v18 and should continue to work even when v19 is released. Version 1.2.4 and up should support both python 2.7 and python 3.

The long term plan for HPASubC is integrate a GUI frontend into the project (version 2) and to maintain compatibility with updates to the HPA project.


License:
--------------
Gnu Public License v3, see text of the full license in project.


Script files:
--------------
1. download_images_from_gene_list.py
2. get_all_genes_as_list.py
3. image_viewer.py
4. image_scorer.py


Dependencies:
--------------
- Python 2 or Python 3 (tested with [Python 2.7](https://www.python.org/downloads/) and [Python 3.6](https://www.python.org/downloads/))
- [requests](https://pypi.python.org/pypi/requests)
- [pygame](http://www.pygame.org/)
- [piexif](https://pypi.python.org/pypi/piexif)
- [future](https://pypi.python.org/pypi/future)


Dependencies: Tips for Windows
--------------
Here are some tips for installing the dependencies on Windows:
- After installing Python, make sure the python directory containing python.exe is on the Windows search path; if not, add it to the path; see http://stackoverflow.com/questions/6318156/adding-python-path-on-windows-7 or similar.
- Pygame, piexif, requests, and future can be installed using the usual PyPi methods in python, including ez_setup.py, easy_install.exe (from setuptools), and pip.exe
- Adding the Scripts directory (in your python installation directory, usually C:\Python27\Scripts or similar) to your path will make it more convenient to use pip.exe or easy_install.exe for installing python modules


HPASubC Installation
--------------
Please visit the respective websites to install the above dependencies.  HPASubC does not require installation. It can be placed in a folder on your path or can be run using an absolute path from the command line.


download_images_from_gene_list.py
--------------
### Usage:

`download_images_from_gene_list.py input_file output_file tissue output_dir [workers]`

For a list of gene ids and a tissue type, this script will get the list of images and image metadata for HPA images, download the full-sized HPA images, and output a file listing information about the retrieved images.  This file requires a .txt input file of ENSG IDs and outputs a .csv file. HPA ENSG IDs can be obtained here: http://www.proteinatlas.org/about/download. Large downloads can take a LONG time.

### Parameters:

**input_file**: A txt file list of ENSG IDs (one per line) without a header in the style of:  
ENSG00000000003  
ENSG00000000005  
ENSG00000000419  

**output_file**: A CSV file with 6 columns:
- image_file: the name of the image file downloaded
- ensg_id: the Ensembl gene id
- tissue: the tissue represented in the image
- antibody: the id of the antibody in the image
- protein_url: the HPA url for the ensg_id
- image_url: the HPA url the image was downloaded from

**tissue**: A valid tissue type recognized by the HPA website. A list of known tissue types are given in Appendix A (for normals) and Appendix B (for cancers) of this file. If there are spaces in the tissue name, enclose the whole name in double quotes, for example: "Heart muscle".  Capitalization is not necessary.

**output_dir**: A folder to contain the downloaded JPEG images.  It will be created if it does not exist.

**workers**: The number of threads to use for downloading images. Optional. Defaults to 3. For large downloads, 50 might be more appropriate.  Please avoid using an excessive number of workers (100 or more).


get_all_genes_as_list.py
--------------
### Usage:

`get_all_genes_as_list.py`

This is a convenience script that will retrieve all the ENSG IDs that are in the HPA and save them to a text file named "all_ensg_ids.txt"  The file is suitable for use as input for the image download script above.

### Parameters:

None  

**output_file**: A text file with a single column of ENSG IDs

ENSG00000134490  
ENSG00000108854  
ENSG00000101558  
...  
ENSG00000257923  


image_viewer.py
--------------
### Usage:

`image_viewer.py input_dir output_file`

This script will open all of the image files within a folder and allow them to be quickly scanned for any staining pattern of interest.  Any image file that can be opened by PyGame can be used, but the extension will need to be added to the imageExtensions list to be recognized. By default, only JPEGs are recognized. Either the keyboard or a PyGame-compatible USB gamepad/joystick can be used (finally, a legitimate reason to have a video game controller on your desk at work).

The HPA image download script in this suite embeds metadata (ensg_id, antibody, etc.) as json in the image file's Exif.UserComment tag. This script uses that Exif data to populate the corresponding columns in the output_file.  If the metadata is not in the image, those columns will be blank.

The gamepad/joystick left and right directions go forward and backward through images, respectively. Other buttons are configurable under BUTTON_BINDINGS in the script file itself.  The script will print the button number being pressed to stdout if you need to know the number scheme for your gamepad/joystick, and want to remap the buttons for your gamepad (very likely as button id's vary from controller to controller).

The keyboard can be used as well. The keys can be remapped in the script file under KEY_BINDINGS. A complete list of all pygame key events can be found at http://www.pygame.org/docs/ref/key.html

Default key bindings are: LEFT ARROW goes to previous image. RIGHT ARROW goes to next image. SPACE BAR selects. The MINUS key zooms out.  The EQUALS (unshifted plus) key zooms in. The ESCAPE key exits and closes the window.

The output file is simply a csv-format file (with header) listing all file paths for the selected images. The file is appended as each selection is made.

The score will be displayed in an animation, this can be shut off by setting animate to False

### Parameters:

**input_dir**: A folder of pygame-compatible images (JPEGs by default)

**output_file**: The output file is a CSV file (with header) listing one row for each that was selected by the user. The file is appended as each image is selected. Columns are:
- image_file: the name of the image file downloaded
- ensg_id: the Ensembl gene id
- tissue: the tissue represented in the image
- antibody: the id of the antibody in the image
- image_url: the HPA url the image was downloaded from


image_scorer.py
--------------
### Usage:

`image_scorer.py input_dir output_file`

This script allows one to assign a score or other arbitrary value to each image in a directory.  It supports arbitrary key bindings defined in the scoreKeys dict.  By default, SPACE and 0 are defined as '0', and '1','2','3','4', and '5' are the scores 1 to 5, respectively. Arbitrary strings such as 'cancer' or 'normal' could also be bound to keys.

This scoring script is designed to be flexible and useful for other purposes, however the primary purpose in this suite is to confirm the image investigated on the quick first pass has the subcellular localization pattern of interest.  If it does have the correct pattern, the keys can be used to assign values such as strong, medium, weak or any other parameter.

The HPA image download script in this suite embeds metadata (ensg_id, antibody, etc.) as json in the image file's Exif.UserComment tag. This script uses that Exif data to populate the corresponding columns in the output_file.  If the metadata is not in the image, those columns will be blank.

We generally put 3,000 images in one folder and scan them in these smaller blocks.  After identifying all interesting images, we collate the output the CSV files into a single file.  We use MS Excel and the CONCATENATE command to convert 11513_29348_B_4_6.jpg into http://www.proteinatlas.org/images/11513/29348_B_4_6.jpg.  Note the first _ character becomes a / character in the final version. This can be also probably be done in R, Perl or Python.  This file is then sent back through HPASubC_image_download.py to download the subset of interesting images into a new folder.

#### Parameters:

**input_dir**: A folder of pygame-compatible images (JPEGs by default) A folder of downloaded .jpg images. Note: We use this HPASubC_image_scorer.py script directly in the image folder.

**output_file**: A CSV file with 6 columns:
- image_file: the name of the image file downloaded
- ensg_id: the Ensembl gene id
- tissue: the tissue represented in the image
- antibody: the id of the antibody in the image
- score: the user-assigned score
- image_url: the HPA url the image was downloaded from


APPENDIX A: Known tissues for HPA v18
--------------
appendix  
pancreas  
lung  
prostate  
epididymis  
placenta  
parathyroid gland  
stomach 1  
stomach 2  
small intestine  
gallbladder  
urinary bladder  
testis  
ovary  
tonsil  
rectum  
duodenum  
colon  
liver  
kidney  
fallopian tube  
lymph node  
oral mucosa  
seminal vesicle  
salivary gland  
vagina  
breast  
thyroid gland  
skeletal muscle  
soft tissue 1  
soft tissue 2  
esophagus  
bronchus  
endometrium 1  
endometrium 2  
bone marrow  
adrenal gland  
heart muscle  
smooth muscle  
skin 2  
skin 1  
nasopharynx  
cervix, uterine  
spleen  
cerebral cortex  
hippocampus  
caudate  
cerebellum  


APPENDIX B: Known cancer tissues for HPA v18
--------------
testis cancer  
urothelial cancer  
renal cancer  
stomach cancer  
pancreatic cancer  
liver cancer  
colorectal cancer  
breast cancer  
prostate cancer  
ovarian cancer  
cervical cancer  
endometrial cancer  
carcinoid  
head and neck cancer  
thyroid cancer  
glioma  
lymphoma  
lung cancer  
melanoma  
skin cancer  
