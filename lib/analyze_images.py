from ij.measure import ResultsTable
from ij.io import DirectoryChooser
from ij.gui import GenericDialog
from ij import IJ
from ij.measure import Measurements

import sys
import os
import datetime

def getTimeStamp():
	return datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")

if len(sys.argv) > 4:
	print '\nWrong number of arguments.'
	print 'usage: runAnalyzeImages.bat input_dir output_dir scale_factor\n'
	sys.exit()
else:
	inputDir = ''
	outputDir = ''
	scale = 1
	if len(sys.argv) > 1:
		inputDir = sys.argv[1]
	if len(sys.argv) > 2:
		outputDir = sys.argv[2]
	if len(sys.argv) > 3:
		scale = float(sys.argv[3])

if not os.path.exists(inputDir) or inputDir == '':
	print 'Input directory %s does not exist.' % inputDir
	inputDir = DirectoryChooser('Choose input directory').getDirectory()
	if inputDir is None:
		print 'No input directory. Exiting.'
		sys.exit()

if not os.path.exists(outputDir) or outputDir == '':
	print 'Output directory %s does not exist.' % outputDir
	outputDir = DirectoryChooser('Choose output directory').getDirectory()
	if outputDir is None:
		print 'No output directory. Exiting.'
		sys.exit()

smoothRadius = 5
print "%s" % scale

# get scale factor from a dialog
gd = GenericDialog('Settings')
gd.addNumericField('Scale:', scale, 3)
gd.addNumericField('Unscaled smooth radius (px):', smoothRadius, 3)
gd.showDialog()
if gd.wasCanceled():
	print 'No scale entered. Exiting.'
	sys.exit()
scale = float(gd.getNextNumber())

smoothRadius = int(round(smoothRadius*scale))
outFileName = "results_%s.csv" % getTimeStamp()
rt = ResultsTable()

imageFileList = []

rt = ResultsTable()

smoothRadius = int(round(5*scale))

for file in os.listdir(inputDir):
	if file.endswith(".jpg"):
		imageFileList.append(os.path.join(inputDir,file))

imageFileList.sort()

print 'scale factor: %s' % scale
print 'smoothRadius: %s px\n' % smoothRadius
print 'total images: %s\n' % len(imageFileList)

for imagePath in imageFileList:
	print 'Processing %s ...' % imagePath
	# open the image
	imp = IJ.openImage(imagePath)
	title = imp.getTitle()
	basename = os.path.splitext(title)[0]
	w = imp.getWidth()
	scaleW = int(round(w * scale))
	imp.setProcessor(imp.getProcessor().resize(scaleW))
	rgb = imp.duplicate()

	# get a grayscale copy and find tissue
	grayImp = imp.duplicate()
	IJ.run(grayImp,"Gaussian Blur...", "radius=%s" % smoothRadius)
	IJ.run(grayImp,"Enhance Contrast...", "saturated=0.4")
	IJ.run(grayImp,"8-bit","")
	IJ.setAutoThreshold(grayImp,"Huang")
	IJ.run(grayImp, "Convert to Mask", "")
	IJ.run(grayImp, "Create Selection", "")
	tissueRoi = grayImp.getRoi()

	# deconvolve the stains
	IJ.runPlugIn(imp,"cd_dab", "") # replaces imp with the DAB channel
	imp.setRoi(tissueRoi)

	# measure the tissue
	stats = imp.getStatistics(Measurements.MEAN | Measurements.MEDIAN | Measurements.AREA | Measurements.MIN_MAX | Measurements.STD_DEV)
	tissueAreaPx = stats.area
	mean = 255 - stats.mean       #invert
	median = 255 - stats.median   #invert
	max = 255 - stats.min
	min = 255 - stats.max
	stdDev = stats.stdDev

	#show
	#grayImp.show()
	#imp.show()
	#rgb.show()

	#annotate
	IJ.setForegroundColor(0,0,255)
	rgb.setRoi(tissueRoi)
	IJ.run(rgb,'Draw','')
	IJ.run(rgb, "Select All", "")

	# save annotation
	annotationPath = os.path.join(outputDir,'%s_overlay.jpg' % basename)
	print "  Saving overlay: %s ..." % annotationPath
	IJ.saveAs(rgb, "Jpeg", annotationPath)

	#clean up
	grayImp.close()
	imp.close()
	rgb.close()

	#populate results table
	rt.incrementCounter()
	rt.addValue("dir",inputDir)
	rt.addValue("fileName",title)
	rt.addValue("path",os.path.join(os.path.abspath(inputDir),title))
	rt.addValue("scale",scale)
	rt.addValue("tissueAreaPx",tissueAreaPx)
	rt.addValue("mean",mean)
	rt.addValue("median",median)
	rt.addValue("min",min)
	rt.addValue("max",max)
	rt.addValue("stdDev",stdDev)
	#rt.show("Results")

	#save results table
	outputPath = os.path.join(outputDir,outFileName)
	print "  Saving/updating results: %s ..." % outputPath
	print "\n"
	rt.saveAs(outputPath)

print 'done.'
sys.exit()
