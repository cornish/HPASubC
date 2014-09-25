from ij.measure import ResultsTable
from ij.process import ImageProcessor
from ij import IJ
from ij.measure import Measurements

import sys
import os
import datetime

for arg in sys.argv: print arg

def getTimeStamp():
	return datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")

if len(sys.argv) < 4:
	print '\nWrong number of arguments.'
	print 'usage: runAnalyzeImages.bat input_dir output_dir scale_factor\n'
	sys.exit()

inputDir = sys.argv[1]
outputDir = sys.argv[2]
scale = float(sys.argv[3])

outFileName = "results_%s.csv" % getTimeStamp()

imageFileList = []

rt = ResultsTable()

smoothRadius = int(round(5*scale))

for file in os.listdir(inputDir):
	if file.endswith(".jpg"):
		imageFileList.append(os.path.join(inputDir,file))

imageFileList.sort()

for imagePath in imageFileList:
	print 'Processing %s ...' % imagePath
	# open the image
	imp = IJ.openImage(imagePath)
	title = imp.getTitle()
	w = imp.getWidth()
	scaleW = int(round(w * scale))
	imp.setProcessor(imp.getProcessor().resize(scaleW))
	#imp.show()

	# get a grayscale copy
	grayImp = imp.duplicate()
	grayImp.setProcessor(grayImp.getProcessor().convertToByteProcessor())
	#grayImp.show()

	# find tissue
	IJ.run(grayImp,"Median...", "radius=%s" % smoothRadius)
	grayImp.getProcessor().setThreshold(0, 240, ImageProcessor.NO_LUT_UPDATE)
	IJ.run(grayImp, "Convert to Mask", "")
	grayImp.updateAndDraw()
	IJ.run(grayImp, "Create Selection", "")
	tissueRoi = grayImp.getRoi()
	grayImp.close()

	# deconvolution the stains
	IJ.runPlugIn(imp,"cd_dab", "") # replaces imp with the DAB channel
	#imp.getProcessor().invert()
	#imp.updateAndDraw()
	imp.setRoi(tissueRoi)

	# measure the tissue
	stats = imp.getStatistics(Measurements.MEAN | Measurements.MEDIAN | Measurements.AREA)
	areaPx = stats.area
	mean = 255 - stats.mean       #invert
	median = 255 - stats.median   #invert

	#clean up
	imp.close()

	#populate results table
	rt.incrementCounter()
	rt.addValue("dir",inputDir)
	rt.addValue("fileName",title)
	rt.addValue("path",os.path.join(os.path.abspath(inputDir),title))
	rt.addValue("scale",scale)
	rt.addValue("areaPx",areaPx)
	rt.addValue("mean",mean)
	rt.addValue("median",median)
	#rt.show("Results")

	#save results table
	outputPath = os.path.join(outputDir,outFileName)
	print "Saving/updating %s ..." % outputPath
	print "\n"
	rt.saveAs(outputPath)

print 'done.'
