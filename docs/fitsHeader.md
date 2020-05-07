# FITS Header Tab
Astrodom reads image information parsing the metadata stored in FITS files header section.
But not all astro imaging softwares (like INDI/Ekos, MaximDL, SGP) use the same set of keywords and also Astrodom  needs its own set.
This tool allows you to inspect FITS file metadata and helps to set up the right profile (in [Settings](settings.md)) for matching keywords and importing FITS in Astrodom.

## Operation
Open a FITS file on your computer usings 'Choose File'. The main window will then show all the keywords and values that are stored in the header section of the FITS file.
The log frame at the bottom of the page shows which keyword is missing (in red) and which is matched correctly (green).
After matching all possible keywords name, there could be some information still missing: for example your software could not provide 'gain' information in the headers. You can fix this by setting a default value for 'GAIN' in the Settings tab.
In the log, keywords that are set by default values are shown in blue.  
![FITS File Headers](fitsHeader.png?raw=true)

## Conclusion
Before trying to import FITS file you should check with this tool that all keywords are ok through matching or default values. 


 
