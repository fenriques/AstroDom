

import os
import numpy as np
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from photutils.detection import DAOStarFinder
from photutils.psf import fit_2dgaussian, fit_fwhm
from photutils.aperture import CircularAperture
from astropy.io import fits
from astropy.stats import sigma_clipped_stats,gaussian_sigma_to_fwhm
from astropy.modeling import models, fitting
from astropy.coordinates import Angle,SkyCoord, EarthLocation, AltAz
from astropy.time import Time
import astropy.units as u
from datetime import datetime
from PyQt6.QtCore import pyqtSignal,QThread
from astrodom.settings import *
from astrodom.loadSettings import *  
from PyQt6.QtSql import QSqlQuery


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
    "FILE": {'fits_key': '', 'display_name': 'File Name'}
    
}

filterMapping = {"L": ["Luminance", "luminance", "Lum", "lum", "L", "l"], 
           "R": ["Red", "R", "r", "red"], 
           "B": ["Blue", "B", "b", "blue"], 
           "G": ["Green", "G", "g", "green"], 
           "Ha": ["Ha", "ha", "Halpha", "halpha", "H_alpha", "h_alpha", "H_Alpha", "h_Alpha"], 
           "Sii": ["SII", "Sii", "sii", "s2"], 
           "Oiii": ["OIII", "Oiii", "oiii", "O3"], 
           "LPR": ["Lpr", "LPR", "lpr"]}

class FitsBrowser(QThread):
    threadLogger = pyqtSignal(str,str)
    taskCompleted = pyqtSignal()
    nFileSync = pyqtSignal(int)
    nFileTot = pyqtSignal(int)
    
    def __init__(self,  project_id, base_dir,bResync,parent=None):

        super().__init__(parent)

        self.project_id = project_id
        self.base_directory = base_dir
        self.bResync = bResync
        self.parent = parent

        self.runs = True
        #this is used to store the filenames of the images in the database so that are skipped when parsing
        self.filesAlreadyInDb = []
        self.filesAlreadyInDb = []
        self.file_counter = 0
        self.files_path = [] 

    def run(self):
        self.filesAlreadyInDb = self.get_filesFromDb(self.project_id)
        self.syncFolder()
        self.stop()
       
    def stop(self):
        self.runs = False
    
    def get_files(self):
        # Search for FITS files starting from the base directory
        for root, dirs, parseFiles in os.walk(self.base_directory):

            for parseFile in parseFiles:
                if parseFile.lower().endswith(('.fits', '.fit')):
                    parseFile_path = os.path.join(root, parseFile)
                    self.files_path.append(parseFile_path)
        
        self.nFileTot.emit(len(self.files_path))
        return len(self.files_path)

    
    def syncFolder(self)  :
        
        # If a resync is requested, all the files for the project are deleted from the database
        if self.bResync == True:
            self.delete_files_from_db(self.project_id)

        nParsed = 0
        self.get_files()

        # Loop over the FITS files found        
        for file_path in self.files_path:     
            file = os.path.basename(file_path)

            # Skip parsing if the file is already in the database
            if self.bResync == False and file_path in self.filesAlreadyInDb:
                self.filesAlreadyInDb.remove(file_path)
                self.threadLogger.emit(f"File was already parsed, so skipping: {file}", "info")
                continue
            
            if not self.runs:
                self.threadLogger.emit("Sync stop requested by user","warning")
                return   

            self.threadLogger.emit(f"Parsing: { file}", "info")
            fits_data =[]
            fits_data_dict = {}
            
            # Open the single FITS file and extract the header
            with fits.open(file_path) as hdul:
                header = hdul[0].header

                # The loop is over the AstroDom internal keywords
                for ad_keyword, ad_value in ad_keywords.items():

                    # If an ad_keyword is found in the header it is processed.
                    # Else it derived from calculation (eg FWHM) or set to None  
                    keyword_intersection = set(ad_value['fits_key']) & set(header.keys())
                    if keyword_intersection:
                        value = header[next(iter(keyword_intersection))]
                        self.threadLogger.emit(f"Keyword {ad_keyword} found in header", "debug")  
                        self.threadLogger.emit(f"with value {value} ", "debug")  
                        
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
                                        date = value

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
                        if ad_keyword == "OBJECT-RA"  and value:
                            fits_data.append((ad_keyword, round(Angle(value, unit='hourangle').degree, 4)))
                        if ad_keyword == "OBJECT-DEC" and value:
                            fits_data.append((ad_keyword, round(Angle(value, unit='deg').degree, 4)))
                        if ad_keyword == "OBJECT-ALT" and value:
                            fits_data.append((ad_keyword, round(Angle(value, unit='deg').degree, 4)))
                        if ad_keyword == "OBJECT-AZ" and value:
                            fits_data.append((ad_keyword, round(Angle(value, unit='deg').degree, 4)))

                    # this else is for the case where the ad_keyword is not found in the header of the FITS file
                    # (eg, NINA doesn't have ALT/ AZ)
                    else:
                        self.threadLogger.emit(f"Keyword {ad_keyword} not found in header", "debug")

                        # This will compute ALT and AZ from RA and DEC, DATE-OBS and LONG-OBS, LAT-OBS
                        if ad_keyword == "OBJECT-ALT" or ad_keyword == "OBJECT-AZ" :
                            self.threadLogger.emit(f"{ad_keyword} calculation", "info")

                            # Create SkyCoord object for the target
                            try:
                                target = SkyCoord(header["OBJECT-RA"], header["OBJECT-DEC"], unit=(u.hourangle, u.deg))

                            except Exception as e:
                                self.threadLogger.emit(f"Error creating SkyCoord object: {e}", "info")
                                self.threadLogger.emit(f"Using alternative headers", "info")
                                target = SkyCoord(header["OBJCTRA"], header["OBJCTDEC"], unit=(u.hourangle, u.deg))
                                
                            # Create EarthLocation object for the observer's location
                            try:
                                lat1 =header["SITELAT"].split('.')[0]
                                lon1 = header["SITELONG"].split('.')[0]
                                location = EarthLocation(lat=lat1*u.deg, lon=lon1*u.deg)
                            except Exception as e:
                                self.threadLogger.emit(f"Error creating EarthLocation object: {e}", "info")
                                self.threadLogger.emit(f"Using alternative headers", "info")
                                try:                               
                                    lat2 =header["LAT-OBS"].split('.')[0]
                                    lon2 = header["LONG-OBS"].split('.')[0]
                                    location = EarthLocation(lat=lat2*u.deg, lon=lon2*u.deg)
                                except Exception as e:  
                                    self.threadLogger.emit(f"Error creating EarthLocation object: {e}", "warning")
                                    location = EarthLocation(lat=0*u.deg, lon=0*u.deg)  


                            # Create Time object for the observation time
                            try:
                                observation_time = Time(header["DATE-OBS"])
                            except Exception as e:
                                self.threadLogger.emit(f"Error creating Time object: {e}", "info")
                                self.threadLogger.emit(f"Using alternative headers", "info")
                                try:
                                    observation_time = Time(header["DATE"], format='fits')
                                except Exception as e:
                                    self.threadLogger.emit(f"Error creating Time object: {e}", "warning")
                                    observation_time = Time.now()   


                            # Create AltAz frame for the transformation
                            try:
                                altaz_frame = AltAz(obstime=observation_time, location=location)
                            except Exception as e:
                                self.threadLogger.emit(f"Error creating AltAz frame: {e}", "warning")
                                self.threadLogger.emit(f"Using alternative headers", "info")
                                altaz_frame = AltAz(obstime=Time.now(), location=EarthLocation(lat=0*u.deg, lon=0*u.deg))

                            # Transform the target coordinates to AltAz
                            altaz = target.transform_to(altaz_frame)

                            # Extract ALT and AZ
                            altitude = altaz.alt.degree
                            azimuth = altaz.az.degree
                            if ad_keyword == "OBJECT-ALT" : fits_data.append(("OBJECT-ALT", round(Angle(altitude, unit='deg').degree, 4)))
                            if ad_keyword == "OBJECT-AZ" : fits_data.append(("OBJECT-AZ", round(Angle(azimuth, unit='deg').degree, 4)))

                    # Other Ad_keyowrds are not meant to be in the FITS header so they are derived from calculation
                    fits_data.append(("FILE", file_path))
                    fits_data.append(("SIZE", round(os.path.getsize(file_path) / (1024 * 1024), 2)))
                    fits_data.append(("PROJECT_ID", self.project_id))
                        
                    # Measure stars for FWHM, ECCENTRICITY, MEAN, MEDIAN, STD
                    # only needs file path
                    if ad_keyword == "FWHM" :
                        try:
                            starMeasurement = self.measure_stars(file_path)
                            if starMeasurement is None:
                                starMeasurement = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
                        except Exception as e:
                            self.threadLogger.emit(f"Error measuring stars: {e}", "error")
                            starMeasurement = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

                        fits_data.append(("FWHM", starMeasurement[1]))
                        fits_data.append(("ECCENTRICITY", starMeasurement[2]))
                        fits_data.append(("MEAN", starMeasurement[3]))
                        fits_data.append(("MEDIAN", starMeasurement[4]))
                        fits_data.append(("STD", starMeasurement[5]))
                
                fits_data_dict = dict(fits_data)

                # Save the data to the database
                self.save_to_db(fits_data_dict)
            self.threadLogger.emit("File parsed: " + file_path,"debug")
            nParsed += 1
            self.nFileSync.emit(nParsed)

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
            OBJECT_AZ, GAIN, OFFSET, FWHM, ECCENTRICITY, FILE, SIZE, MEAN, MEDIAN, STD, PROJECT_ID
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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

    def measure_stars(self,fits_file):

        if self.parent and hasattr(self.parent, 'starAnalysis'):
            starAnalysis = self.parent.starAnalysis
        else:
            starAnalysis = None

        randomSources = starAnalysis.nStars if starAnalysis and starAnalysis.nStars else 30
        self.threadLogger.emit(f"randomSources: {randomSources}","info")

        cropFactor = starAnalysis.cropFactor if starAnalysis and starAnalysis.cropFactor else 2
        self.threadLogger.emit(f"cropFactor: {cropFactor}","info")

        threshold = starAnalysis.threshold if starAnalysis and starAnalysis.threshold else 20
        self.threadLogger.emit(f"threshold: {threshold}","info")

        bit = starAnalysis.bit if starAnalysis and starAnalysis.bit else 16
        self.threadLogger.emit(f"bit: {bit}","info")

        bin = starAnalysis.bin if starAnalysis and starAnalysis.bin else 1
        self.threadLogger.emit(f"bin: {bin}","info")

        radius = starAnalysis.radius if starAnalysis and starAnalysis.radius else 7
        self.threadLogger.emit(f"radius: {radius}","info")

        mode = "both" # "micah" or "astropy" or "both"
        plot_image = False # plot the image with the detected stars
        fwhm_micah = []
        ecc = []
        average_fwhm_micah, average_fwhm,average_ecc = 0,0,0

        # Load the FITS file
        hdu_list = fits.open(fits_file, mode='readonly')
        image_data = hdu_list[0].data
        hdu_list.close()

        # Crop the image by cropFactor of its width and height (faster processing)
        height, width = image_data.shape
        crop_height = height // cropFactor
        crop_width = width // cropFactor
        start_y = (height - crop_height) // 2
        start_x = (width - crop_width) // 2
        image_data = image_data[start_y:start_y + crop_height, start_x:start_x + crop_width]

        # Calculate basic statistics
        mean, median, std = sigma_clipped_stats(image_data, sigma = 3.0)

        # Detect stars
        try:
            daofind = DAOStarFinder(fwhm = 3.0, threshold = threshold*std)
            sources = daofind(image_data - median)
        except Exception as e:
            self.threadLogger.emit(f"Error detecting stars: {e}","error")
            return None
        self.threadLogger.emit(f"Number of stars detected by DAO: {len(sources)}","debug")

        # Cutting saturated stars
        sources = sources[sources['peak'] < (2**bit)*0.98 ]
        self.threadLogger.emit(f"Number of non clipped stars (< 98perc peak): {len(sources)}","debug")
        #print(sources)
        
        # Cutting weak stars (noise)
        sources = sources[sources['peak'] > median*10.0]
        self.threadLogger.emit(f"Number of non clipped  stars above background*10: {len(sources)}","debug")
        # Exclude sources with flux/peak too high, it is likely to be in  a galaxy or in a nebula too bright
        sources = sources[sources['peak'] / sources['flux'] > 0.0]
        self.threadLogger.emit(f"Number of stars with flux/peak too high: {len(sources)}","debug")

        if len(sources) == 0:
            self.threadLogger.emit("No detected stars suitable for measurement ","warning")
            return  
        
        # Choose randomSources (faster processing)
        np.random.seed(42)  # For reproducibility
        if len(sources) > randomSources:
            sources = sources[np.random.choice(len(sources), randomSources, replace=False)]
            #sources.sort('peak', reverse=True)
            #sources = sources[:randomSources]
        #print(sources)
        # Calculate and print the average peak value
        average_peak = np.mean(sources['peak'])
        self.threadLogger.emit(f"Number of stars detected: {len(sources)}","info")
        self.threadLogger.emit(f"Average Peak: {average_peak:.2f}","debug")
        self.threadLogger.emit(f"Mean: {mean:.2f}, Median: {median:.2f}, Std: {std:.2f}","info")
        
        if mode == "micah" or mode == "both":
            for source in sources:
                x = source['xcentroid']
                y = source['ycentroid']
                if (x > radius and x < (width - radius) and y > radius and y < (height - radius)):
                # Assuming you have the star's image data in `data` and the aperture in `aperture`
                    cutout = image_data[int(y-radius):int(y+radius), int(x-radius):int(x+radius)]

                    # Fit a 2D Gaussian
                    try:
                        p_init = models.Gaussian2D(amplitude=np.max(cutout), x_mean=radius, y_mean=radius)
                        fit_p = fitting.LevMarLSQFitter()
                        y, x = np.mgrid[:cutout.shape[0], :cutout.shape[1]]
                        p = fit_p(p_init, x, y, cutout)

                        # Calculate the FWHM
                        sigma_x = p.x_stddev.value
                        sigma_y = p.y_stddev.value
                        fwhm_x = sigma_x * gaussian_sigma_to_fwhm
                        fwhm_y = sigma_y * gaussian_sigma_to_fwhm
                        fwhm_micah.append(np.sqrt(fwhm_x * fwhm_y))
                        if fwhm_y < fwhm_x:
                            ecc.append(np.sqrt(abs(1 - fwhm_y/fwhm_x)))
                        else:
                            ecc.append(0)
                    except Exception as e:
                        self.threadLogger.emit(f"Error fitting 2D Gaussian at position x: {x}, y: {y}","warning")
                        
                        self.threadLogger.emit(f"Exception: {e}","error")

                    #print(f"FWHM_x: {fwhm_x}, FWHM_y: {fwhm_y}")
                else:
                    self.threadLogger.emit(f"Star at position x: {x}, y: {y} is too close to the edge. Skipping star","warning")


        if mode == "astropy" or mode ==  "both":
            xypos = list(zip(sources['xcentroid'], sources['ycentroid']))

            psfphot = fit_2dgaussian(image_data, xypos=xypos, fix_fwhm=False, fit_shape=(7, 7))
            phot_tbl = psfphot.results
            try:
                fwhm = fit_fwhm(image_data, xypos=xypos, fit_shape=(7, 7))
            except Exception as e:
                self.threadLogger.emit(f"Error fitting FWHM: {e}","error")
                fwhm = [0.0] * len(sources) 
            #print(fwhm)

        # Calculate and print the average FWHM value
        if mode == "micah" or mode == "both": 
            average_fwhm_micah = np.mean(fwhm_micah)
            self.threadLogger.emit(f"Average FWHM Micah: {average_fwhm_micah:.2f}","debug")
            average_ecc = np.mean(ecc)
            self.threadLogger.emit(f"Average ecc: {average_ecc:.2f}","info")
    
        if mode == "astropy" or mode == "both": 
            average_fwhm = np.mean(fwhm)
            self.threadLogger.emit(f"Average FWHM Astropy: {average_fwhm:.2f}","info")

        if plot_image:

            cpositions = np.transpose((sources['xcentroid'], sources['ycentroid']))
            apertures = CircularAperture(cpositions, r = radius)
            plt.figure()
            plt.imshow(image_data, cmap = 'Greys', origin = 'lower', norm = LogNorm(), interpolation = 'nearest')
            plt.colorbar()

            # draw apertures. apertures.plot command takes arguments (color, line-width, and opacity (alpha))
            apertures.plot(color = 'red', lw = 2.5, alpha = 0.5)
            for i, cposition in enumerate(cpositions):
                plt.text(cposition[0], cposition[1], f'{fwhm[i]:.2f}', color='red', fontsize=9, ha='right', va='top')
                plt.text(cposition[0], cposition[1], f'{sources["peak"][i]:.2f}', color='blue', fontsize=9, ha='left', va='bottom')
            plt.show()

        return np.array([round(average_fwhm_micah, 2), round(average_fwhm, 2), round(average_ecc, 2), round(mean, 2), round(median, 2), round(std, 2)])
