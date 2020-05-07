


# AstroDom
Astro(nomy) Dom(ine) is a catalogue tool for deep sky images. It scans the directories where images (FITS format only) are stored and reads information from FITS headers. Additional parameter like FWHM, Eccentricity, Noise can be added from Pixinsight CSV exports. The catalogue can be used to keep track of your imaging sessions and to benchmark your images. With the Charts tool you can discover important information about your data, e.g.:

-   How much Alt affects FWHM
-   Which night had the best seeing conditions
-   Where in the sky (Alt, Az) the guiding is best / worse.
-   How many hours for each filter

AstroDom was tested with FITS files written by MaximDL (v4 and v6), Ekos/INDI, SGP but any other software is supported through custom profiles.

## Basic configuration workflow
After installation you can have a loot at a demo database of images or build your own following these steps:

1. Check that your software FITS keywords are matched with AstroDom's ([here](fitsHeader.md))   
2. Fix unmatched FITS keyword and default values ([here](settings.md))
3. Import FITS file from any directory on your PC ([here](importFits.md))
4. Optionally add information about FWHM, Eccentricity, Noise and SNR ([here](importCsv.md))

Thats'it, you can now browse through your images.

## Documentation Index
- [Installation](install.md)
- [FITS Header Parser](fitsHeader.md)
- [Configuration and Settings](settings.md)
- [PixInsight's SubFrameSelector CSV Import](importCsv.md)
- [Import FITS files](importFits.md)
- [Image List](imageList.md)
- [Charts](chart.md)
- [Image Details](imageDetails.md)

## Roadmap
### TODO:
- ImageDetails: image info (WCS, grid) and controls (pan, zoom, stretch)
- Import: Match fits file using filename (not just using hash).Mmmh no.
- Charts: Moon path in Alt/Az or Alt/Time charts (observatory issue)
- Charts: Custom x/y axis in charts
- Charts: Night vs night comparison
- Charts: Model updates graphs
- Charts: Linear fit, sigmas
- Charts: Hover info
- Fix layout: max window size, filter position and spacing
- Image list: Delete / Edit rows
- Image list: Export data as csv
- INDI listner
- Startup script for Mac and Win
- Inputs validation

### DOING:
- Threads in import
- Application log
- Support for other softwares (MaximDL, SGP)

### DONE:

**v0.2**
- Image List: filter on 'selected night'
- Fits Header: read key/val, show missing keys
- Settings: toggle column visibility in ImageList
- Import: Log messages to GUI (https://docs.python.org/3/howto/logging-cookbook.html)
- Settings: Save profile
**v0.1**
- Image List: months interval in Settings
- Select Database
- Created a demo database based on M101 feb 2020 data
- Startup script and desktop icon
- Button icons
- Fix: custom obs time start / end 
- MainWindow closes all other windows.
- Import: Refresh model after imports
- Package and PyPi upload
- Fix: ImageDetails image canvas update
- Fix: import only completed rows
- Image Details: QWidget with Thumbnail and fields
- Image Details: Fits thumb- Settings: Fits header default values
- Fix: filter on float data (eg eccentricity) only works for n > 1
- Round float values in columns
- Filter colors legend in Charts Window
- Override target name imports
- Module / Classes
- Edit / delete rows in importTab
- Set up Github repo
- Application Settings
- Data set totals, means and std dev
- Date slider / data picker
- Dataset filter on date
- Dark theme
- Filter expression
- Sort column
- Grid default
- Graph
	https://www.learnpyqt.com/courses/graphics-plotting/plotting-pyqtgraph/
- Format Date
- Alt/AZ astropy Calc
	https://docs.astropy.org/en/stable/generated/examples/coordinates/plot_obs-planning.html
- tableview, filter and search
	https://www.walletfox.com/course/qsortfilterproxymodelexample.php
	https://stackoverflow.com/questions/34252413/how-to-create-a-filter-for-qtablewidget

## Disclaimer
ASTRODOM IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.

