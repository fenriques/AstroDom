# Import FITS File
AstroDom grabs information from FITS file metadata (in the header section of the file) using this tool. Before using this tool check  that everything in  [Configuration and Settings](settings.md) set up correctly.
**Choose Dir** opens a pop up where you can choose the root directory where AstroDom start searching for FITS (both .FIT and .FITS extension) recursively. 
![Choose a directory](importFits1.png)
There's no limit to the number of file that can be imported but it's a good advice to find a limit (like a single night session, a sequence or a target).
When the directory is opened, clicking Load Files populates the main windows with all FITS data. 
![Loading FITS data](importFits2.png)

Both the log frame and the data table will highlight issues, the log will be more descriptive in the message.
To correct these problems try to:
- Review  keywords and default values as explained in [Settings](settings.md), see image below.
- Edit single cell values and press 'enter'
- Delete unwanted rows by selecting the row and pressing button 'Delete Row'
- Only for target name, enter a value in 'Override Target Name on Insert': this will set the inserted name for all records. It is useful if you want to correct some sequences where you set for example 'Horse Head' instead of 'Horse Head Nebula' or 'IC434'. If you save different name for the same target it will be then difficult to find all targets when searching in Image List.

![Fits data imported in the table ](importFits3.png)
![Errors in some keywords](importFits4.png)



