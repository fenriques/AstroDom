# AstroDom
Astro(nomy) Dom(ine) is a catalogue tool for deep sky images. It scans the directories where images (FITS format only) are 
stored and reads information from FITS headers. 
Additional parameter like FWHM, Eccentricity, Noise can be added from Pixinsight CSV exports.
The catalogue can be used to keep track of your imaging sessions and to benchmark your images.
With the Charts tool you can discover important information from your data, e.g.:
- How much Alt affects FWHM
- Which night had the best seeing conditions
- Where in the sky (Alt, Az) the guiding is best / worse.
- etc

# Features
- Scans recursively filesystem directories searching for FITS files.
- Add image parameters from Pixinsight's SubFrameSelector process: FWHM, Eccentricity, SNRWeight, Noise.
- List, filter, search all the images in the database. It shows mean values and standard deviation for most important parameters. See image 1 below.
- Outputs charts with several information. See image 2 below.

# Screenshot
Main window with search criteria and results:

![image 1](/docs/test.gif?raw=true)

Charts plotted for a subset of images (colors map different filters):
![image 2](/docs/ADcharts.png?raw=true)

