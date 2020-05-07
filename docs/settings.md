
# Settings
Here you can configure AstroDom settings using these three boxes:
- Config 
- Filter Keywords
- FITS Profiles

![Settings Tab](settings.png?raw=true)

## Config 

- **Database**: is the name of your local AstroDom storage  based on a SQLite rdbms. Db files (with .db extension) are located in /astrodom/config directory.
Entering a text in the form will create a new database; you can have as many databases as you want and this will help organizing your data. AstroDom has been tested with thousands of records. But if you see filters and searches slowing down it could be the case of segregate some data in a new database. 
Existing database can be selected click on the icon on the right of the form.

- **Debug Level**: levels are Debug, Info, Warning, Error, Critical. During normal operation recommended is 'Error'. Debug files are located in  /astrodom/logs/
- **Obs Time Hrs**: we usually image at night from dusk to dawn. A night span two different dates. So in the image list it is useful to have date filters starting from a default starting till a default ending observation hour.
- **Filter Months** : AstroDom operation is more convenient on actual / recent data; data will be filtered looking back this amount of months.
- **Save**: saves parameter for this box only. As of v0.2 it requires AstroDom to restart because I was not able to refresh database without closing the app. Will be fixed in a next version.

## FITS Profiles
To create a catalogue of images AstroDom tries to read information from the header section of FITS file. Unfortunately, astro imaging softwares do not use the same set of keywords when they write those information in the FITS headers.

Here you can instruct AstroDom how to recognize those different keywords. For example, MaximDL records gain info in the keyword 'EGAIN' while INDI/Ekos uses 'GAIN'.

Different profiles has to be used if you are importing data written by different software. Moreover, profiles with different default values can be created to keep track of different setups. 
For example: 
If you create '*MaximDL @observatory*' and '*MaximDL @home'* profiles, site locations do not need to be hand written each time.   '*Ekos/INDI on observatory setup*' and '*Ekos/INDI on mobile setup*' allows to store custom information for each setup, for example binning.

'Hide' checkbox toggles keyword visibility in [Image List](imageList.md).
 
- **Choose Profile**: Selecting an existing profile loads all keywords and values for that profile. Setting a different name in 'Profile Name' allows to create a new profile.

- **FITS Keyoword**: Simply match the name used by your astro imaging software in the corresponding form. If you don' know which keywords is used by your software, AstroDom [FITS Header Parser](fitsHeader.md) can help you.
- **Default Value**: sometimes the values of FITS keyword are missing, for example during a sequence you forgot to set the DSO target name. Or your astro imaging software do not store some values, for example 'OFFSET', you can then set a default for these missing values. AstroDom  FITS keywords are all mandatory so you either have to match your software keywords or provide default values: no empty value are allowed when importing.   
- **Coord Format**: to match the right format of coordinates choose 'hour angle' if your software displays coordinates as '01 33 55', choose 'decimal' in it shows coordinates as '78.964'.
- **Profile Name**: it holds the name for the selected profile. If you change the name a new profile will be created. 
- **Save**: saves parameter for this box only. As of v0.2 it requires AstroDom to restart because I was not able to refresh database without closing the app. Will be fixed in a next version.


## Filter Keywords
- **Luminance, Red, Green, Blue, Halpha, Oiii, Sii**: Data displayed in Charts has different colors for each filter but astroimaging softwares can assign different names to these filters; so it is useful to group together names that refer to the same filter. For example 'Lum', 'Luminance' and 'luminance' refers to the same filter and we want to display as such in Charts.  
For each filter enter a list of names separated by a comma.
'LPR' refers to 'cover' or 'black' filter, it can be used for Darks hopefully not for Lights.
Filters not matching any of these keywords will be displayed in gray.

- **Save**: takes effect without restarting AstroDom.
 
