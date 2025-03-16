

import os, sqlite3, ephem, warnings
import numpy as np
import astropy.units as u
from matplotlib.colors import LogNorm
from photutils.detection import DAOStarFinder
from photutils.psf import  fit_fwhm
from astropy.io import fits
from astropy.stats import sigma_clipped_stats
from astropy.coordinates import Angle, AltAz, EarthLocation, SkyCoord
from astropy.time import Time
from astropy.table import QTable
from datetime import datetime
from PyQt6.QtCore import pyqtSignal,QThread
from astrodom.loadSettings import *  

# AstroDom internal keywords used to parse the FITS files and display the data in the main window
# The keywords are mapped to the FITS header keywords but there are also calculated values (eg FWHM, Moon Phase)
ad_keywords = {
    "OBJECT": {'fits_key': ["OBJECT", "OBJ", "TARGET"], 'display_name': 'Target'},
    "DATE-OBS": {'fits_key': ["DATE-OBS"], 'display_name': 'Date'},
    "FILTER": {'fits_key': ["FILTER"], 'display_name': 'Filter'},
    "EXPOSURE": {'fits_key': ["EXPOSURE","EXPTIME"], 'display_name': 'Exposure'},
    "CCD-TEMP": {'fits_key': ["CCD-TEMP"], 'display_name': 'Temperature'},
    "IMAGETYP": {'fits_key': ["IMAGETYP","FRAME"], 'display_name': 'Frame'},
    "XBINNING": {'fits_key': ["XBINNING"], 'display_name': 'Bin X'},
    "OBJECT-RA": {'fits_key': ["OBJECT-RA","OBJCTRA"], 'display_name': 'RA'},
    "OBJECT-DEC": {'fits_key': ["OBJECT-DEC","OBJCTDEC"], 'display_name': 'DEC'},
    "OBJECT-ALT": {'fits_key': ["OBJECT-ALT","OBJCTALT"], 'display_name': 'ALT'},
    "OBJECT-AZ": {'fits_key': ["OBJECT-AZ","OBJCTAZ"], 'display_name': 'AZ'},
    "GAIN": {'fits_key': ["GAIN"], 'display_name': 'Gain'},
    "OFFSET": {'fits_key': ["OFFSET"], 'display_name': 'Offset'},
    "FWHM": {'fits_key': '', 'display_name': 'FWHM'},
    "ECCENTRICITY": {'fits_key':'', 'display_name': 'Eccentricity'},
    "MEAN": {'fits_key':'', 'display_name': 'Mean'},
    "MEDIAN": {'fits_key':'', 'display_name': 'Median'},
    "STD": {'fits_key':'', 'display_name': 'SNR'},
    "SIZE": {'fits_key': "", 'display_name': 'Size'},
    "FILE": {'fits_key': '', 'display_name': 'File Name'},
    "SITELAT": {'fits_key': ["SITELAT","LAT-OBS"], 'display_name': 'Site Lat'},
    "SITELONG": {'fits_key': ["SITELONG","LONG-OBS"], 'display_name': 'Site Long'},
    "MOON_PHASE": {'fits_key': '', 'display_name': 'Moon Phase'},
    "MOON_SEPARATION": {'fits_key': '', 'display_name': 'Moon Separation'}
    }
# Mapping of the filter names to the FITS header values because 
# the filters are not always the same in the FITS header (depends on the imaging software)
filterMapping = {"L": ["Luminance", "luminance", "Lum", "lum", "L", "l"], 
           "R": ["Red", "R", "r", "red"], 
           "B": ["Blue", "B", "b", "blue"], 
           "G": ["Green", "G", "g", "green"], 
           "Ha": ["Ha", "ha", "Halpha", "halpha", "H_alpha", "h_alpha", "H_Alpha", "h_Alpha"], 
           "Sii": ["SII", "Sii", "sii", "s2"], 
           "Oiii": ["OIII", "Oiii", "oiii", "O3"], 
           "LPR": ["Lpr", "LPR", "lpr"]}

# When in a thread, the warnings displayed in the console could crash the application
# So are suppressed in the thread 
warnings.filterwarnings("ignore")

# Class to read the FITS files and sync the database through the sync and autosync buttons in the main window.
# The class runs in a thread so no direct outpit is allowed: only signals to update the GUI (data, log messages)
# The run method is the entry point that is called when the thread is started
# The syncFolder method is used to read all the fits files starting from the base directory. Sends a list to syncFiles.
# The syncFiles method is called by syncFolder (sync button->run) or directly (autosync button->run) to parse the FITS files
# SyncFiles iterates over the FITS files and over the AstroDom internal keywords
# The bResync bool is used to force re parsing all files (true) or only new ones (false) 
# Based on bResync files can be deleted from db delete_files_from_db  and likewise  
# get_filesFromDb has images already in db so that are skipped when parsing)
# There are then utility methods:  
# save_to_db saves the data to the database
# The calculate_moon_phase and calculate_moon_separation methods are used to calculate the moon phase and separation
# The measure_stars method is used to measure the stars in the image
# The delete_files_from_db method is used to delete the files from the database when a resync is forced
# The stop method is used to stop the thread based on self.runs flag

class SyncImages(QThread):
    threadLogger = pyqtSignal(str,str)
    taskCompleted = pyqtSignal()
    nFileSync = pyqtSignal(int)
    nFileTot = pyqtSignal(int)
    
    def __init__(self,  project_id, base_dir,bResync,bAutoSync,files_path=None,parent=None):

        super().__init__(parent)

        self.project_id = project_id
        self.base_directory = base_dir
        self.bResync = bResync
        self.bAutoSync = bAutoSync
        self.files_path = files_path
        self.parent = parent

        self.runs = True
        #this is used to store the filenames of the images in the database so that are skipped when parsing
        self.filesAlreadyInDb = []
        self.file_counter = 0

    def run(self):
        self.filesAlreadyInDb = self.get_filesFromDb(self.project_id)

        if self.files_path is not None:
            self.syncFiles(self.files_path)
        elif self.bAutoSync == False :
            self.files_path = []
            self.syncFolder()
            self.stop()

    def stop(self):
        self.runs = False
    
    def syncFolder(self)  :

        self.threadLogger.emit(f"Start syncing project n: {self.project_id}", "debug")
        self.threadLogger.emit(f"Base folder: {self.base_directory}", "debug")
        self.threadLogger.emit(f"Resync: {self.bResync}", "debug")

        # If a resync is requested, all the files have to be parsed again
        # So the first step is to delete all the project files that are in the database
        if self.bResync == True:
            self.delete_files_from_db(self.project_id)

        # Search for FITS files starting from the base directory
        for root, dirs, parseFiles in os.walk(self.base_directory):

            for parseFile in parseFiles:
                if parseFile.lower().endswith(('.fits', '.fit')):
                    parseFile_path = os.path.join(root, parseFile)
                    self.files_path.append(parseFile_path)
        
        self.nFileTot.emit(len(self.files_path))

        self.syncFiles(self.files_path)

        self.threadLogger.emit(f"New files inserted in the database: {self.file_counter}", "info")

        # Syncing means also that files that are not in the folder anymore (deleted by user?) are removed from the db
        # If a resync is forced, the files are already removed from the db
        if len(self.filesAlreadyInDb)  > 0 and self.bResync == False:
            self.threadLogger.emit(f"These are files not found in the database anymore: {self.filesAlreadyInDb}", "debug")    
            
            # Remove the files that are not in the folder anymore
            db_path = str(self.parent.rsc_path.joinpath(DBNAME))
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            for file in self.filesAlreadyInDb:
                cursor.execute("DELETE FROM images WHERE file = ?", (file,))
                self.threadLogger.emit(f"File removed from database: {file}","warning")
            conn.commit()
            conn.close()
        
        self.threadLogger.emit(f"Task completed in sync thread", "debug")

        self.taskCompleted.emit()

        return

    def syncFiles(self,files_path):
        nParsed = 0

        # Loop over the FITS files found        
        for file_path in self.files_path:     
            file = os.path.basename(file_path)
            self.threadLogger.emit(f"Parsing file: {file}", "info")

            # Skip parsing if the file is already in the database
            if self.bResync == False and file_path in self.filesAlreadyInDb:
                self.filesAlreadyInDb.remove(file_path)
                self.threadLogger.emit(f"File was already parsed, so skipping: {file}", "warning")
                continue
            
            if not self.runs:
                self.threadLogger.emit("Sync stop requested by user","warning")
                return   

            fits_data = []
            fits_data_dict = {}
            
            # Open the single FITS file and extract the header
            try:
                hdul = fits.open(file_path)
                header = hdul[0].header
            except Exception as e:
                self.threadLogger.emit(f"Error opening FITS file: {e}", "error")
                continue
            finally:
                hdul.close()

                # The loop is over the AstroDom internal keywords
                for ad_keyword, ad_value in ad_keywords.items():

                    # If an ad_keyword is found in the header it is processed.
                    # Else it derived from calculation (eg FWHM) or set to None  
                    keyword_intersection = set(ad_value['fits_key']) & set(header.keys())
                    if keyword_intersection:
                        value = header[next(iter(keyword_intersection))]
                        self.threadLogger.emit(f"FITS header keyword: {ad_keyword} = {value} ", "debug")  
                        
                        #DATE-OBS 
                        if ad_keyword == "DATE-OBS" and value:
                            try:
                                date = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%f').strftime('%Y-%m-%dT%H:%M:%S')
                            except ValueError:
                                try:
                                    date = datetime.strptime(value.split('.')[0], '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S')

                                except ValueError:
                                    try:
                                        date = datetime.strptime(value, '%Y-%m-%d').strftime('%Y-%m-%dT00:00:00')
                                    except ValueError:
                                        date = '1970-01-01T00:00:00'
                            
                            ephem_date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')

                            fits_data.append(("DATE-OBS", date))
                        
                        # OBJECT, IMAGETYP  are text values
                        if ad_keyword in ["OBJECT","IMAGETYP"]  and value:
                            fits_data.append((ad_keyword, str(value)))
                                
                        # EXPOSURE, IMAGETYP, XBINNING, GAIN, OFFSET, SIZE are int values
                        if ad_keyword in ["EXPOSURE", "XBINNING", "GAIN", "OFFSET"]  and value:
                            fits_data.append((ad_keyword, int(value)))

                        # CCD-TEMP, FWHM, ECCENTRICITY, arefloat values
                        if ad_keyword in ["CCD-TEMP", "FWHM", "ECCENTRICITY"] and value:
                            fits_data.append((ad_keyword, round(float(value), 2)))  

                        # FILTER values
                        if ad_keyword in ["FILTER"]  and value:
                            for filter_key, filter_values in filterMapping.items():
                                if value in filter_values:
                                    fits_data.append(("FILTER", filter_key))    

                        # OBJECT-RA, OBJECT-DEC,OBJECT-ALT, OBJECT-AZ, are decimal converted values
                        if ad_keyword in ["OBJECT-RA","OBJTRA"]  and value:
                            fits_data.append((ad_keyword, round(Angle(value, unit='hourangle').degree, 4)))
                            ephem_target_ra = Angle(value, unit='hourangle').degree
                        if ad_keyword in ["OBJECT-DEC", "OBJCTDEC"] and value:
                            fits_data.append((ad_keyword, round(Angle(value, unit='deg').degree, 4)))
                            ephem_target_dec = Angle(value, unit='deg').degree
                        if ad_keyword == "OBJECT-ALT" and value:
                            fits_data.append((ad_keyword, round(Angle(value, unit='deg').degree, 4)))
                        if ad_keyword == "OBJECT-AZ" and value:
                            fits_data.append((ad_keyword, round(Angle(value, unit='deg').degree, 4)))

                        # Site Lat and Long
                        if ad_keyword in ["SITELAT","LAT-OBS"] : 
                            fits_data.append((ad_keyword, round(Angle(value, unit='deg').degree, 4)))
                            ephem_site_lat = Angle(value, unit='deg').degree
                        if ad_keyword in ["SITELONG","LONG-OBS"] : 
                            fits_data.append((ad_keyword, round(Angle(value, unit='deg').degree, 4)))
                            ephem_site_long = Angle(value, unit='deg').degree

                    # this else is for the case where the ad_keyword is not found in the header of the FITS file
                    # (eg, NINA doesn't have ALT/ AZ)
                    else:
                        self.threadLogger.emit(f"{ad_keyword}:", "debug")

                        # This will compute ALT and AZ from RA and DEC, DATE-OBS and LONG-OBS, LAT-OBS
                        if ad_keyword == "OBJECT-ALT" or ad_keyword == "OBJECT-AZ" :
                            self.threadLogger.emit(f"ALT/AZ calculation based on other keywords", "info")

                            # The following 3 objects (EarthLocation, Skycoord and Time) are utitities used to calculate the ALT and AZ of the target if they are not in the FITS header
                            # Create EarthLocation object for the observer's location
                            try:
                                lat1 = header["SITELAT"]
                                lon1 = header["SITELONG"]
                                location = EarthLocation(lat=lat1*u.deg, lon=lon1*u.deg)
                                self.threadLogger.emit(f"Using keywords SITELAT {lat1}, SITELONG {lon1}  ", "debug")
                            except Exception as e:
                                self.threadLogger.emit(f"Error creating EarthLocation object: {e}", "debug")
                                try:                               
                                    lat2 = header["LAT-OBS"]
                                    lon2 = header["LONG-OBS"]
                                    self.threadLogger.emit(f"Using alternative keywords LAT-OBS {lat2}, LONG-OBS {lon2}", "debug")
                                    location = EarthLocation(lat=lat2*u.deg, lon=lon2*u.deg)
                                except Exception as e:  
                                    self.threadLogger.emit(f"Error creating EarthLocation object: {e}", "error")
                                    location = EarthLocation(lat=0*u.deg, lon=0*u.deg)  
                            
                            self.threadLogger.emit(f"Earth Location: {location}", "info")

                            # Create SkyCoord object for the target
                            try:
                                ra1 = header["OBJECT-RA"]
                                dec1 = header["OBJECT-DEC"]
                                self.threadLogger.emit(f"Using keywords OBJECT-RA {ra1}, OBJECT-DEC {dec1}  ", "debug")
                                target = SkyCoord(ra1, dec1, unit=(u.hourangle, u.deg))

                            except Exception as e:
                                self.threadLogger.emit(f"Error creating SkyCoord object: {e}", "debug")
                                try:
                                    ra2 = header["OBJCTRA"]
                                    dec2 = header["OBJCTDEC"]
                                    self.threadLogger.emit(f"Using alternative OBJCTRA {ra2}, OBJCTDEC {dec2} ", "debug")
                                    target = SkyCoord(ra2, dec2, unit=(u.hourangle, u.deg))
                                except Exception as e:  
                                    self.threadLogger.emit(f"Error creating SkyCoord object: {e}", "error")
                                    target = SkyCoord(0*u.deg, 0*u.deg)

                                self.threadLogger.emit(f"Target RA: {target.ra.deg} deg, DEC: {target.dec.deg} deg", "info") 
                                
                            try:
                                observation_time = Time(header["DATE-OBS"])
                                self.threadLogger.emit(f"Using keyword DATE-OBS {header["DATE-OBS"],}", "debug")
                            except Exception as e:
                                self.threadLogger.emit(f"Error creating Time object: {e}", "debug")
                                self.threadLogger.emit(f"Using alternative keyword DATE {header["DATE"],}", "debug")
                                try:
                                    observation_time = Time(header["DATE"], format='fits')
                                except Exception as e:
                                    self.threadLogger.emit(f"Error creating Time object: {e}", "error")
                                    observation_time = Time.now()   

                            self.threadLogger.emit(f"Observation time: {observation_time}", "info")

                            # Create AltAz frame for the transformation
                            try:
                                altaz_frame = AltAz(obstime=observation_time, location=location)
                            except Exception as e:
                                self.threadLogger.emit(f"Error creating ALT/AZ: {e}", "error")
                                altaz_frame = AltAz(obstime=Time.now(), location=EarthLocation(lat=0*u.deg, lon=0*u.deg))
                            

                            # Transform the target coordinates to AltAz
                            altaz = target.transform_to(altaz_frame)

                            # Extract ALT and AZ
                            altitude = altaz.alt.degree
                            azimuth = altaz.az.degree
                            fits_data.append(("OBJECT-ALT", round(Angle(altitude, unit='deg').degree, 4)))
                            self.threadLogger.emit(f"OBJECT-ALT: {altitude}", "info")
                            fits_data.append(("OBJECT-AZ", round(Angle(azimuth, unit='deg').degree, 4)))
                            self.threadLogger.emit(f"OBJECT-AZ: {azimuth}", "info")


                    # Other Ad_keyowrds are not meant to be in the FITS header so they are derived from calculation
                    if ad_keyword == "FILE" :
                        fits_data.append(("FILE", file_path))
                        self.threadLogger.emit(f"FILE: {file_path}", "debug")
                    if ad_keyword == "SIZE" :
                        fits_data.append(("SIZE", round(os.path.getsize(file_path) / (1024 * 1024), 2)))
                        self.threadLogger.emit(f"SIZE: {round(os.path.getsize(file_path) / (1024 * 1024), 2)}", "debug")
                    if ad_keyword == "PROJECT_ID" :
                        fits_data.append(("PROJECT_ID", self.project_id))
                        self.threadLogger.emit(f"PROJECT_ID: {self.project_id}", "debug")


                    # Measure stars for FWHM, ECCENTRICITY, MEAN, MEDIAN, STD
                    # only needs file path
                    if ad_keyword == "FWHM" :
                        try:
                            starMeasurement = self.measure_stars(file_path)
                            if starMeasurement is None:
                                starMeasurement = [0.0, 0.0, 0.0, 0.0, 0.0]
                        except Exception as e:
                            self.threadLogger.emit(f"Error measuring stars: {e}", "error")
                            starMeasurement = [0.0, 0.0, 0.0, 0.0, 0.0]
        
                        fits_data.append(("FWHM", starMeasurement[0]))
                        fits_data.append(("ECCENTRICITY", starMeasurement[1]))
                        fits_data.append(("MEAN", starMeasurement[2]))
                        fits_data.append(("MEDIAN", starMeasurement[3]))
                        fits_data.append(("STD", starMeasurement[4]))


                    if ad_keyword == "MOON_PHASE" :
                        try:
                            moon_phase = self.calculate_moon_phase(ephem_date, ephem_site_lat, ephem_site_long) 
                            
                        except Exception as e:
                            self.threadLogger.emit(f"Error calculating moon phase: {e}", "error")
                            moon_phase = 0.0
                        self.threadLogger.emit(f"Moon phase: {moon_phase}", "info")
                        fits_data.append(("MOON_PHASE", (moon_phase)))  

                    if ad_keyword == "MOON_SEPARATION" :
                        try:
                            moon_separation = self.calculate_moon_separation(ephem_date, ephem_target_ra, ephem_target_dec, ephem_site_lat, ephem_site_long)
                        except Exception as e:
                            self.threadLogger.emit(f"Error calculating moon separation: {e}", "error")
                            moon_separation = 0.0
                        fits_data.append(("MOON_SEPARATION", moon_separation))
                        self.threadLogger.emit(f"Moon separation: {moon_separation}", "info")

                fits_data_dict = dict(fits_data)

                # Save the data to the database
                self.save_to_db(fits_data_dict)
            self.threadLogger.emit("File parsed: " + file_path,"debug")
            nParsed += 1
            self.nFileSync.emit(nParsed)
        
        return 
    
    # this function is used to get the filenames of the images in the database so that are skipped when parsing
    # files in the folders and the remainders are removed from the db if they are not in the folder
    def get_filesFromDb(self,project_id):
        db_path = str(self.parent.rsc_path.joinpath( DBNAME))
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT file FROM images WHERE PROJECT_ID = ?", (project_id,))

        files_in_db = cursor.fetchall()
        ids = [file[0] for file in files_in_db]
        conn.close()
        return ids

    def save_to_db(self,fits_data):

        self.file_counter += 1
        db_path = str(self.parent.rsc_path.joinpath( DBNAME))
        conn = sqlite3.connect(db_path)
        self.threadLogger.emit("Connected to database","debug")
            
        cursor = conn.cursor()
        try:
            cursor.execute('''
            INSERT INTO images (
            OBJECT, DATE_OBS, FILTER, EXPOSURE, CCD_TEMP, IMAGETYP, XBINNING, OBJECT_RA, OBJECT_DEC, OBJECT_ALT, 
            OBJECT_AZ, GAIN, OFFSET, FWHM, ECCENTRICITY, FILE, SIZE, MEAN, MEDIAN, STD, SITELAT, SITELONG, MOON_PHASE, MOON_SEPARATION, PROJECT_ID
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
            fits_data.get('OBJECT', ''),
            fits_data.get('DATE-OBS', '1970-01-01T00:00:00'),
            fits_data.get('FILTER', ''),
            fits_data.get('EXPOSURE', 0),
            fits_data.get('CCD-TEMP', 0.0),
            fits_data.get('IMAGETYP', ''),
            fits_data.get('XBINNING', 1),
            fits_data.get('OBJECT-RA', ''),
            fits_data.get('OBJECT-DEC', ''),
            fits_data.get('OBJECT-ALT', ''),
            fits_data.get('OBJECT-AZ', ''),
            fits_data.get('GAIN', 0),
            fits_data.get('OFFSET', 0),
            fits_data.get('FWHM', 0.0),
            fits_data.get('ECCENTRICITY', 0.0),
            fits_data.get('FILE', ''),
            fits_data.get('SIZE', 0.0),
            fits_data.get('MEAN', 0.0),
            fits_data.get('MEDIAN', 0.0),
            fits_data.get('STD', 0.0),
            fits_data.get('SITELAT', 0.0),
            fits_data.get('SITELONG', 0.0),
            fits_data.get('MOON_PHASE',0.0),
            fits_data.get('MOON_SEPARATION', 0.0),
            fits_data.get('PROJECT_ID', self.project_id)
            ))
            conn.commit()

        except sqlite3.Error as e:
            self.threadLogger.emit(f"Error: {e} for file {fits_data['FILE']}", "error")

        conn.close()
        self.threadLogger.emit(f"Saved to db: {fits_data['FILE']}","debug")
    
    # To be used when a resync is forced ( bResync == True)
    def delete_files_from_db(self, project_id):
        db_path = str(self.parent.rsc_path.joinpath(DBNAME))
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM images WHERE PROJECT_ID = ?", (project_id,))
        conn.commit()
        conn.close()
        self.threadLogger.emit(f"All files for project {project_id} deleted from database", "info")

    # Ephem is used to calculate the moon phase and separation, works better than Astropy
    def calculate_moon_separation(self, date, target_ra, target_dec, site_lat, site_long):

        observer = ephem.Observer()
        observer.lon = str(site_long)
        observer.lat = str(site_lat)
        observer.date = ephem.Date(date)

        moon = ephem.Moon(observer)
        
        target = ephem.FixedBody()
        target._ra = target_ra
        target._dec = target_dec
        target.compute(observer)
        
        separation = ephem.separation(moon, target)
        separation_degrees = np.degrees(separation)
        
        return round(separation_degrees, 2)

    def calculate_moon_phase(self, date, site_lat, site_long):
        
        try:
            # Create an observer 
            observer = ephem.Observer()
            observer.lon = str(site_long)
            observer.lat = str(site_lat)
            observer.date = ephem.Date(date)  # Set the observation date
            moon = ephem.Moon(observer)
            
            phase_illumination = round(moon.moon_phase * 100, 2)

        except Exception as e:
            self.threadLogger.emit(f"Error calculating moon phase: {e}", "error")
            phase_illumination = 0.0

        return phase_illumination
    
    # Measure fwhm.eccentricity (roundess) and snr (std) from sources in the image
    # The same function is used in the Star Analysis widget (duplicated code, to be fixed in a next release)
    # A fitting function is used to calculate the FWHM, eccentricity of the stars
    # SNR is calculated as the standard deviation of the background over the median background
    def measure_stars(self,fits_file):

        # Important: the parameters are read from Star Analysis widget if available
        # else they are set to default values
        if self.parent and hasattr(self.parent, 'starAnalysisDialog'):
            starAnalysisDialog = self.parent.starAnalysisDialog
        else:
            starAnalysisDialog = None

        self.nStars = starAnalysisDialog.nStars if starAnalysisDialog and starAnalysisDialog.nStars else 30
        self.threadLogger.emit(f"nStars: {self.nStars}","debug")

        self.cropFactor = starAnalysisDialog.cropFactor if starAnalysisDialog and starAnalysisDialog.cropFactor else 2
        self.threadLogger.emit(f"cropFactor: {self.cropFactor}","debug")

        self.threshold = starAnalysisDialog.threshold if starAnalysisDialog and starAnalysisDialog.threshold else 20
        self.threadLogger.emit(f"threshold: {self.threshold}","debug")

        self.bit = starAnalysisDialog.bit if starAnalysisDialog and starAnalysisDialog.bit else 16
        self.threadLogger.emit(f"bit: {self.bit}","debug")

        self.bin  = starAnalysisDialog.bin if starAnalysisDialog and starAnalysisDialog.bin else 1
        self.threadLogger.emit(f"bin: {self.bin}","debug")

        self.radius = starAnalysisDialog.radius if starAnalysisDialog and starAnalysisDialog.radius else 7
        self.threadLogger.emit(f"radius: {self.radius}","debug")

        self.saturationLimit = starAnalysisDialog.saturationLimit if starAnalysisDialog and starAnalysisDialog.radius else 95
        self.threadLogger.emit(f"saturationLimit: {self.saturationLimit}","debug")


        fwhmfit = []

        # Load the FITS file
        hdu_list = fits.open(fits_file)
        self.image_data = hdu_list[0].data
        hdu_list.close()
        
       # Crop the image by cropFactor of its width and height (faster processing)
        height, width = self.image_data.shape
        crop_height = height // self.cropFactor
        crop_width = width // self.cropFactor
        start_y = (height - crop_height) // 2
        start_x = (width - crop_width) // 2
        self.image_data = self.image_data[start_y:start_y + crop_height, start_x:start_x + crop_width]

        # Calculate basic statistics
        mean, median, std = sigma_clipped_stats(self.image_data, sigma = 3.0)
        if std == 0:
            self.threadLogger.emit("Standard deviation is zero, invalid operation encountered.","error")
            return None
        self.threadLogger.emit(f"Mean: {mean:.2f}, Median: {median:.2f}, Std: {std:.2f}", "info")
        

        # Detect stars
        try:
            daofind = DAOStarFinder(fwhm = 3.0, threshold = self.threshold*std)
            sources = daofind(self.image_data  - median)
            self.threadLogger.emit(f"Number of stars detected by DAO: {len(sources)}","debug")
        except Exception as e:
            self.threadLogger.emit(f"Error detecting stars: {e}","error")
            return None
        
        # Cutting saturated stars and roundness < 0.5
        sources = sources[(sources['peak'] < (2**self.bit)*self.saturationLimit/100)] 
        sources = sources[(np.abs(sources['roundness2']) < 0.5)] 

        self.threadLogger.emit(f"Number of non clipped stars (less than {self.saturationLimit} perc peak: {len(sources)}","debug")
        

        # Order the stars by peak/median ratio so by how much they are above the background
        sources['peak_median_ratio'] = sources['peak'] / median
        sources.sort('peak_median_ratio', reverse=True)
        self.threadLogger.emit(f"Number of non clipped  stars above background: {len(sources)}", "debug")

        if len(sources) == 0:
            self.threadLogger.emit("No stars detected, cannot calc Fwhm, eccentricity and snr", "error")
            return  None

        # Reduce the number of stars (faster processing)
        if len(sources) > self.nStars:
            sources = sources[:self.nStars]
        self.sources = sources

        # Calculate and print the average peak value
        average_peak = np.mean(sources['peak'])
        self.threadLogger.emit(f"Number of stars detected: {len(sources)}","info")
        self.threadLogger.emit(f"Average Peak: {average_peak:.2f}","debug")
        
        results_table = QTable(names=('xcentroid', 'ycentroid', 'peak', 'fwhm', 'roundness', 'peak_median_ratio'), dtype=('f4', 'f4', 'f4', 'f4', 'f4', 'f4'))

        # Iterate over the detected stars
        for source in sources:
            x = source['xcentroid']
            y = source['ycentroid']
            try:
                #this condition is to avoid stars too close to the edge
                if (x > self.radius and x < (width - self.radius) and y > self.radius and y < (height - self.radius)):
                    # Assuming you have the star's image data in `data` and the aperture in `aperture`
                    # A cutout of the star is a square region around the star
                    self.threadLogger.emit(f"Cutout centered on the star at position: {x,y} ", "debug")

                    starCutOut = self.image_data[int(y-self.radius):int(y+self.radius), int(x-self.radius):int(x+self.radius)]
                    try:
                        starCutOutMean, starCutOutMedian, starCutOutStd = sigma_clipped_stats(starCutOut, sigma = 3.0)
                    except Exception as e:  
                        self.threadLogger.emit(f"Error calculating cutout stats: {e}", "warning")
                        continue    
                    
                    self.threadLogger.emit(f"Star Cutout Mean: {starCutOutMean:.2f}, Star Cutout Median: {starCutOutMedian:.2f}, Star Cutout Std: {starCutOutStd:.2f}", "debug")
                    
                    # A larger cutout is a square region around the same star, but larger
                    largerCutOut = self.image_data[int(y-10*self.radius):int(y+10*self.radius), int(x-10*self.radius):int(x+10*self.radius)]
                    try:
                        largerCutOutMean, largerCutOutMedian, largerCutOutStd = sigma_clipped_stats(largerCutOut, sigma = 3.0)
                    except Exception as e:
                        self.threadLogger.emit(f"Error calculating larger cutout stats: {e}", "warning")
                        continue    
                
                    self.threadLogger.emit(f"Larger Cutout Mean: {largerCutOutMean:.2f}, Larger Cutout Median: {largerCutOutMedian:.2f}, Larger Cutout Std: {largerCutOutStd:.2f}", "debug")    

                    # If the median value of the larger region around the star is not above
                    # (twice) the background of the image, we have a representative region that
                    # is not affected by other sources like a nebula or a galaxy.
                    if largerCutOutMedian < 2 * median:

                        # Use photutils to fit the star with a 2D Gaussian
                        fwhml = fit_fwhm(starCutOut - median, fit_shape=(7, 7))
                        fwhmfit.append( fwhml)

                        results_table.add_row((source['xcentroid'], source['ycentroid'], source['peak'], fwhml, source['roundness2'], source['peak_median_ratio']))

                    else:
                        self.threadLogger.emit("Star rejected because of high background, probably a star in a nebula or galaxy : {largerCutOutMedian}, vs : {median} ", "warning") 
                else:
                    self.threadLogger.emit(f"Skipping star at position x {x}, y {y}:  too close to the edge","warning")   
            except Exception as e:
                self.threadLogger.emit(f"Error fitting 2D Gaussian at position x: {x}, y: {y}", "warning")
                self.threadLogger.emit(f"Cutout values: {starCutOut}", "debug")
                self.threadLogger.emit(f"Exception: {e}", "warning")


        
        # FWHM average
        average_fwhm = np.mean(fwhmfit)
        self.threadLogger.emit(f"Average FWHM: {average_fwhm:.2f}", "info")

        # Eccentricity in DAOStarFinder is the ratio of the minor and major axes of the star
        roundness2_avg = np.mean(abs(results_table['roundness']))
        self.threadLogger.emit(f"Average Roundness: {roundness2_avg:.2f}", "info")

        
        return np.array([ round(average_fwhm, 2), round(roundness2_avg, 2), round(mean, 2), round(median, 2), round(std, 2)])

