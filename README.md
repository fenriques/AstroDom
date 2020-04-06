# AstroDom
Astro(nomy) Dom(ine) is a catalogue for deep sky images. It scans the directories where images (FITS format only) are 
stored and reads information from FITS headers. 
Additional parameter like FWHM, Eccentricity, Noise can be added from Pixinsight CSV exports.
The catalogue can be used to keep track of your imaging sessions and to benchmark your images.

# Features
- Scans recursively filesystem directories for FITS files.
- Add image parameters from Pixinsight's SubFrameSelector process: FWHM, Eccentricity, SNRWeight, Noise.
- List, filter, search all the images in the database. It shows mean values and standard deviation for most important parameters. See image below:

![Image of AstroDom](https://github.com/fenriques/AstroDom/blob/master/docs/ADImages.png)

