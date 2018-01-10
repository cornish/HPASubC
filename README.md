HPASubC, v1.2.0 01/10/2018
==============
The Human Protein Atlas (HPA) Subcellular Classification (SubC) software package is a collection of python scripts by Marc Halushka and Toby Cornish at Johns Hopkins University School of Medicine, Baltimore, MD. This is free software in the public space. This suite of scripts has not been made in conjunction with the HPA, thus the HPA is in no way responsible for any data obtained through these methods. No warranties are given or implied.


License:
--------------
Gnu Public License v3, see text of the full license in project.


Script files:
--------------
1. download_images_from_gene_list.py
2. image_viewer.py
3. image_scorer.py


Dependencies:
--------------
- Python 2 (tested with [Python 2.7](https://www.python.org/downloads/))
- [Requests](https://pypi.python.org/pypi/requests)
- [Pygame](http://www.pygame.org/)
- [pyexiv2](https://launchpad.net/pyexiv2)


Dependencies: Tips for Windows
--------------
Here are some tips for installing the dependencies on Windows:
- After installing Python, make sure the python directory containing python.exe is on the Windows search path; if not, add it to the path; see http://stackoverflow.com/questions/6318156/adding-python-path-on-windows-7 or similar.
- For Pygame and pyexiv2, we recommend using the windows installers at http://www.lfd.uci.edu/~gohlke/pythonlibs/ because both depend on native binaries
- Requests can be installed using the usual methods in python, including ez_setup.py, easy_install.exe (from setuptools), and pip.exe
- Adding the Scripts directory (in your python installation directory, usually C:\Python27\Scripts or similar) to your path will make it more convenient to use pip.exe or easy_install.exe for installing python modules


HPASubC Installation
--------------
Please visit the respective websites to install the above dependencies.  HPASubC does not require installation. It can be placed in a folder on your path or can be run using an absolute path from the command line.


download_images_from_gene_list.py
--------------
####Usage:

`download_images_from_gene_list.py input_file output_file tissue output_dir`

For a list of gene ids and a tissue type, this script will parse the HPA results, extract all image URLs, and output a list of .jpg image urls.  This file requires a .txt input file of ENSG IDs and outputs a .csv file. HPA ENSG IDs can be obtained here: http://www.proteinatlas.org/about/download.

This script will download the full-sized HPA images from the .csv file generated by get_image_urls_from_gene_list.py

####Parameters:

**input_file**: A txt file list of ENGS IDs without a header in the style of:
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


image_viewer.py
--------------
####Usage:

`image_viewer.py input_dir output_file`

This script will open all of the image files within a folder and allow them to be quickly scanned for any staining pattern of interest.  Any image file that can be opened by PyGame can be used, but the extension will need to be added to the imageExtensions list to be recognized. By default, only JPEGs are recognized. Either the keyboard or a PyGame-compatible USB gamepad/joystick can be used (finally, a legitimate reason to have a video game controller on your desk at work).

The HPA image download script in this suite embeds metadata (ensg_id, antibody, etc.) as json in the image file's Exif.UserComment tag. This script uses that Exif data to populate the corresponding columns in the output_file.  If the metadata is not in the image, those columns will be blank.

The gamepad/joystick left and right directions go forward and backward through images, respectively. Other buttons are configurable under BUTTON_BINDINGS in the script file itself.  The script will print the button number being pressed to stdout if you need to know the number scheme for your gamepad/joystick, and want to remap the buttons for your gamepad (very likely as button id's vary from controller to controller).

The keyboard can be used as well. The keys can be remapped in the script file under KEY_BINDINGS. A complete list of all pygame key events can be found at http://www.pygame.org/docs/ref/key.html

Default key bindings are: LEFT ARROW goes to previous image. RIGHT ARROW goes to next image. SPACE BAR selects. The MINUS key zooms out.  The EQUALS (unshifted plus) key zooms in. The ESCAPE key exits and closes the window.

The output file is simply a csv-format file (with header) listing all file paths for the selected images. The file is appended as each selection is made.

The score will be displayed in an animation, this can be shut off by setting animate to False

####Parameters:

**input_dir**: A folder of pygame-compatible images (JPEGs by default)

**output_file**: The output file is a CSV file (with header) listing one row for each that was selected by the user. The file is appended as each image is selected. Columns are:
- image_file: the name of the image file downloaded
- ensg_id: the Ensembl gene id
- tissue: the tissue represented in the image
- antibody: the id of the antibody in the image
- image_url: the HPA url the image was downloaded from


image_scorer.py
--------------
####Usage:

`image_scorer.py input_dir output_file`

This script allows one to assign a score or other arbitrary value to each image in a directory.  It supports arbitrary key bindings defined in the scoreKeys dict.  By default, SPACE and 0 are defined as '0', and '1','2','3','4', and '5' are the scores 1 to 5, respectively. Arbitrary strings such as 'cancer' or 'normal' could also be bound to keys.

This scoring script is designed to be flexible and useful for other purposes, however the primary purpose in this suite is to confirm the image investigated on the quick first pass has the subcellular localization pattern of interest.  If it does have the correct pattern, the keys can be used to assign values such as strong, medium, weak or any other parameter.

The HPA image download script in this suite embeds metadata (ensg_id, antibody, etc.) as json in the image file's Exif.UserComment tag. This script uses that Exif data to populate the corresponding columns in the output_file.  If the metadata is not in the image, those columns will be blank.

We generally put 3,000 images in one folder and scan them in these smaller blocks.  After identifying all interesting images, we collate the output the CSV files into a single file.  We use MS Excel and the CONCATENATE command to convert 11513_29348_B_4_6.jpg into http://www.proteinatlas.org/images/11513/29348_B_4_6.jpg.  Note the first _ character becomes a / character in the final version. This can be also probably be done in R, Perl or Python.  This file is then sent back through HPASubC_image_download.py to download the subset of interesting images into a new folder.

####Parameters:

**input_dir**: A folder of pygame-compatible images (JPEGs by default) A folder of downloaded .jpg images. Note: We use this HPASubC_image_scorer.py script directly in the image folder.

**output_file**: A CSV file with 6 columns:
- image_file: the name of the image file downloaded
- ensg_id: the Ensembl gene id
- tissue: the tissue represented in the image
- antibody: the id of the antibody in the image
- score: the user-assigned score
- image_url: the HPA url the image was downloaded from

APPENDIX A: Known tissues for HPA (see HPA site for updates)
--------------
- Liver and pancreas
  - Liver
  - Gallbladder
  - Pancreas
- Digestive tract (GI  -tract)
  - Oral mucosa
  - Salivary gland
  - Esophagus
  - Stomach
  - Duodenum
  - Small Intestine
  - Appendix
  - Colon
  - Rectum
- Urinary tract (Kidney and bladder)
  - Kidney
  - Urinary bladder
- Male reproductive system (Male tissues)
  - Testis
  - Epididymis
  - Prostate
  - Seminal vesicle
- Breast and female reproductive system
  - Breast
  - Vagina
  - Cervix, uterine
  - Uterus
  - Fallopian tube
  - Ovary
  - Placenta
- Blood and immune system (Hematopoietic)
  - Bone marrow
  - Lymph node
  - Tonsil
  - Spleen
- Central nervous system (Brain)
  - Cerebral cortex
  - Hippocampus
  - Lateral ventricle
  - Cerebellum
- Endocrine glands
  - Thyroid gland
  - Parathyroid gland
  - Adrenal gland
- Respiratory system (Lung)
  - Nasopharynx
  - Bronchus
  - Lung
- Cardiovascular system
  - Heart muscle
- Skin and soft tissues
  - Skin
  - Skeletal muscle
  - Smooth muscle
  - Soft tissue

APPENDIX B: Known cancer tissues for HPA
--------------
- Colorectal cancer
- Breast cancer
- Prostate cancer
- Ovarian cancer
- Cervical cancer
- Endometrial cancer
- Carcinoid
- Head and neck cancer
- Thyroid cancer
- Glioma
- Lymphoma
- Lung cancer
- Melanoma
- Skin cancer
- Testis cancer
- Urothelial cancer
- Renal cancer
- Stomach cancer
- Pancreatic cancer
- Liver cancer
