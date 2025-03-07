
import numpy as np,logging
import matplotlib.pyplot as plt
import astropy.units as u

from matplotlib.colors import LogNorm
from photutils.detection import DAOStarFinder
from photutils.psf import fit_2dgaussian, fit_fwhm
from photutils.aperture import CircularAperture
from astropy.io import fits
from astropy.stats import sigma_clipped_stats,gaussian_sigma_to_fwhm
from astropy.modeling import models, fitting
from PyQt6.QtWidgets import QApplication, QDialog, QLabel, QVBoxLayout, QGridLayout, QHBoxLayout, QLineEdit, QComboBox, QTableView, QWidget, QPushButton
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QAbstractTableModel, Qt
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT, FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from astropy.table import QTable
from pandas import DataFrame
from PyQt6.QtWidgets import QSpacerItem, QSizePolicy
from PyQt6.QtWidgets import QGroupBox

from astrodom.settings import *
from astrodom.loadSettings import *  
import os

# Stars data are displayed in a QTableView
class QTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data

    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
        return len(self._data.columns)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(self._data.columns[section])
            if orientation == Qt.Orientation.Vertical:
                return str(self._data.index[section])
        return None
    
class StarAnalysis(QDialog):
    def __init__(self, parent = None, fits_path = None):
        super().__init__(parent)

        self.rsc_path = importlib_resources.files("astrodom").joinpath('rsc')

        # Path to the FITS file to analyze: could be a file selected in the filesystem or
        # a file selected clicking on the dashboard 
        self.fits_path = fits_path 
        self.nStars = 30 # Choose randomSources (faster processing)
        self.threshold = 20 #threshold for star detection, 20 seems to work well
        self.pixelScale = 0.73 # pixel scale in arcsec/pixel
        self.bit = 16 # bit depth of the sensor, used to cut saturated stars
        self.bin = 1 # binning factor
        self.radius = 7 # radius of the aperture for the star measurement
        self.saturationLimit = 95 # saturation limit in percent of the peak value

        # Crop the image by cropFactor of its width and height (faster processing)
        try:
            file_size = os.path.getsize(self.fits_path) / (1024 * 1024)
            self.cropFactor =int(file_size // 50)
        except Exception as e:  
            logging.error(f"Error getting file size: {e}")
            self.cropFactor = 2 

        file_name = os.path.basename(self.fits_path)
        
        self.setWindowTitle("Star analysis - "+file_name) 
        self.setGeometry(100, 100, 1200, 800)

        main_layout = QVBoxLayout(self)
        control_panel = QWidget(self)

        # Add QLineEdit and QComboBox widgets to the control panel
        self.cropFactorComboBox = QComboBox(self)
        crop_factor_label = QLabel("Crop Factor", self)
        self.cropFactorComboBox.addItems(['1', '2', '3', '4'])
        self.cropFactorComboBox.setCurrentText(str(self.cropFactor))

        nStarsLabel = QLabel("# Stars", self)
        self.nStarsEdit = QLineEdit(self)
        self.nStarsEdit.setText(str(self.nStars))

        thresholdLabel = QLabel("Threshold", self)
        self.thresholdEdit = QLineEdit(self)
        self.thresholdEdit.setText(str(self.threshold))

        self.bitComboBox = QComboBox(self)
        bitLabel = QLabel("Image Bit Depth", self)
        self.bitComboBox.addItems(['8', '12', '14', '16'])
        self.bitComboBox.setCurrentText(str(self.bit))

        self.binComboBox = QComboBox(self)
        binLabel = QLabel("Binning", self)
        self.binComboBox.addItems(['1', '2', '3', '4'])
        self.binComboBox.setCurrentText(str(self.bin))

        self.radiusComboBox = QComboBox(self)
        cradiusLabel = QLabel("Radius", self)
        self.radiusComboBox.addItems(['5', '7', '9', '11'])
        self.radiusComboBox.setCurrentText(str(self.radius))
        
        self.applyButton = QPushButton("Analyze Image", self)
        self.applyButton.clicked.connect(self.on_apply_clicked) 
        self.applyButton.setIcon(QIcon(str(self.rsc_path.joinpath( 'icons', 'star.png'))))

        self.saturationLimitComboBox = QComboBox(self)
        saturation_limit_label = QLabel("Saturation Limit %", self)
        self.saturationLimitComboBox.addItems(['100', '98', '95', '90', '85', '80'])
        self.saturationLimitComboBox.setCurrentText(str(self.saturationLimit))

        control_grid_layout = QGridLayout()

        control_grid_layout.addWidget(crop_factor_label, 0, 0)
        control_grid_layout.addWidget(self.cropFactorComboBox, 0, 1)
        control_grid_layout.addWidget(nStarsLabel, 0, 2)
        control_grid_layout.addWidget(self.nStarsEdit, 0, 3)
        control_grid_layout.addWidget(thresholdLabel, 0, 4)
        control_grid_layout.addWidget(self.thresholdEdit, 0, 5)
        control_grid_layout.addWidget(bitLabel, 1, 0)
        control_grid_layout.addWidget(self.bitComboBox, 1, 1)
        control_grid_layout.addWidget(binLabel, 1, 2)
        control_grid_layout.addWidget(self.binComboBox, 1, 3)
        control_grid_layout.addWidget(cradiusLabel, 1, 4)
        control_grid_layout.addWidget(self.radiusComboBox, 1, 5)
        control_grid_layout.addWidget(saturation_limit_label, 2, 0)
        control_grid_layout.addWidget(self.saturationLimitComboBox, 2, 1)
        control_grid_layout.addWidget(self.applyButton, 1, 6)
        control_grid_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum), 0,8, 2, 1)
        control_panel.setLayout(control_grid_layout)

        # Group box for control panel
        control_group_box = QGroupBox("Star Detection Parameters", self)
        control_group_box.setLayout(control_grid_layout)

        # Add the group box to the main layout
        main_layout.addWidget(control_group_box)

        # Add a widget to show the current file name and average values
        file_info_layout = QHBoxLayout()
        self.averageFwhmLabel = QLabel("<b>Average FWHM: N/A</b>", self)
        self.averageRoundnessLabel = QLabel("<b>Average Roundness: N/A</b>", self)
        
        file_info_layout.addWidget(self.averageFwhmLabel)
        file_info_layout.addWidget(self.averageRoundnessLabel)
        
        main_layout.addLayout(file_info_layout)

        # Bottom layout
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(10)

        # Add QTableView to the left side
        self.starTableView = QTableView(self)
        bottom_layout.addWidget(self.starTableView, 1)

        # Add two matplotlib canvases to the right side
        canvas_widget = QWidget(self)
        canvas_layout = QVBoxLayout(canvas_widget)
        canvas_layout.setContentsMargins(0, 0, 0, 0)
        canvas_layout.setSpacing(10)

        self.imageCanvas = FigureCanvas(Figure(figsize=(5, 3)))
        self.starCanvas = FigureCanvas(Figure(figsize=(5, 3)))
        self.toolbar = NavigationToolbar2QT(self.imageCanvas, self)
        canvas_layout.addWidget(self.toolbar)
        canvas_layout.addWidget(self.imageCanvas)
        canvas_layout.addWidget(self.starCanvas)

        bottom_layout.addWidget(canvas_widget, 1)

        # Add control panel and bottom layout to the main layout
        main_layout.addWidget(control_panel)
        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)

    # When the "Analyze Image" button is clicked, read the star detection parameters
    # and call the measure_stars method
    def on_apply_clicked(self):
        
        self.cropFactor = int(self.cropFactorComboBox.currentText())
        self.nStars = int(self.nStarsEdit.text())
        self.threshold = int(self.thresholdEdit.text())
        self.bit = int(self.bitComboBox.currentText())
        self.bin = int(self.binComboBox.currentText())
        self.radius = int(self.radiusComboBox.currentText())*self.bin
        self.saturationLimit = int(self.saturationLimitComboBox.currentText())

        # Clear the star table view and both figure canvases
        self.starTableView.setModel(None)
        self.imageCanvas.figure.clear()
        self.starCanvas.figure.clear()
        self.starTableView.viewport().update()
        self.imageCanvas.draw()
        self.starCanvas.draw()

        self.data_stars = self.measure_stars(self.fits_path)
        logging.info(self.data_stars)

        df = DataFrame(np.array(self.sources))
        df = df[['id', 'xcentroid', 'ycentroid', 'sharpness', 'roundness2', 'peak', 'peak_median_ratio']].round(2)
        
        model = QTableModel(df)
        
        self.starTableView.setModel(model)
        self.starTableView.clicked.connect(self.on_table_row_clicked)

    # Get the row index when a row in the table is clicked
    # and call the plot_star method
    def on_table_row_clicked(self, index):
        model_id = index.row()
        self.plot_star(model_id)

    # Plot the star 3D profile when a row in the table is clicked
    def plot_star(self, model_id):

        self.starCanvas.figure.clear()
        source = self.sources[model_id]
        
        x = source['xcentroid']
        y = source['ycentroid']

        # Remove the point from the plot
        if len(self.ax1.lines) > 0:
            self.ax1.lines[0].remove()
        self.ax1.plot(x, y, color='green', marker='x', linestyle='dashed', linewidth=6, markersize=12)
        self.imageCanvas.draw()
        
        # Crop the image around the star
        cutout = self.image_data[int(y-self.radius):int(y+self.radius), int(x-self.radius):int(x+self.radius)]

        # Create a meshgrid for the surface plot
        x_grid, y_grid = np.meshgrid(np.arange(cutout.shape[1]), np.arange(cutout.shape[0]))

        # Plot the star on self.starCanvas as a 3D surface plot
        ax2 = self.starCanvas.figure.add_subplot(111, projection='3d')
        ax2.clear()
        ax2.plot_surface(x_grid, y_grid, cutout, cmap='viridis')
        ax2.set_title(f'Star at ({x:.2f}, {y:.2f})')
        self.starCanvas.draw()
    
    # The main function that selects and measures the relevant value of stars in the FITS file
    def measure_stars(self,fits_file):
    
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
            logging.error("Standard deviation is zero, invalid operation encountered.")
            return
        logging.info(f"Mean: {mean:.2f}, Median: {median:.2f}, Std: {std:.2f}")
        
        # Detect stars using photutils.DAOStarFinder
        try:
            daofind = DAOStarFinder(fwhm = 3.0, threshold = self.threshold*std)
            sources = daofind(self.image_data - median)
            logging.info(f"Number of stars detected by DAO: {len(sources)}")
        except Exception as e:
            logging.error(f"Error detecting stars: {e}")
            return

        # Cutting saturated stars and roundness < 0.5
        sources = sources[(sources['peak'] < (2**self.bit)*self.saturationLimit/100)] 
        sources = sources[(np.abs(sources['roundness2']) < 0.5)] 
        logging.info(f"Number of non clipped stars (< {self.saturationLimit}% peak): {len(sources)}")
        
        # Order the stars by peak/median ratio so by how much they are above the background
        sources['peak_median_ratio'] = sources['peak'] / median
        sources.sort('peak_median_ratio', reverse=True)
        logging.info(f"Number of non clipped  stars above background*10: {len(sources)}")

        if len(sources) == 0:
            logging.error("No stars detected")
            return  
        
        # Reduce the number of stars (faster processing)
        if len(sources) > self.nStars:
            sources = sources[:self.nStars]
        self.sources = sources

        # Calculate and print the average peak value
        average_peak = np.mean(sources['peak'])
        logging.info(f"Average Peak: {average_peak:.2f}")

        logging.info(f"Mean: {mean:.2f}, Median: {median:.2f}, Std: {std:.2f}")
        logging.info(f"Number of sources detected: {len(sources)}")
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
                    logging.debug(f"Cutout centered on the star at position: {x,y} ")

                    starCutOut = self.image_data[int(y-self.radius):int(y+self.radius), int(x-self.radius):int(x+self.radius)]
                    try:
                        starCutOutMean, starCutOutMedian, starCutOutStd = sigma_clipped_stats(starCutOut, sigma = 3.0)
                    except Exception as e:  
                        logging.warning(f"Error calculating cutout stats: {e}")
                        continue    
                    
                    logging.debug(f"Star Cutout Mean: {starCutOutMean:.2f}, Star Cutout Median: {starCutOutMedian:.2f}, Star Cutout Std: {starCutOutStd:.2f}")
                    
                    # A larger cutout is a square region around the same star, but larger
                    largerCutOut = self.image_data[int(y-10*self.radius):int(y+10*self.radius), int(x-10*self.radius):int(x+10*self.radius)]
                    try:
                        largerCutOutMean, largerCutOutMedian, largerCutOutStd = sigma_clipped_stats(largerCutOut, sigma = 3.0)
                    except Exception as e:
                        logging.warning(f"Error calculating larger cutout stats: {e}")
                        continue    
                
                    logging.debug(f"Larger Cutout Mean: {largerCutOutMean:.2f}, Larger Cutout Median: {largerCutOutMedian:.2f}, Larger Cutout Std: {largerCutOutStd:.2f}")

                    # If the median value of the larger region around the star is not above
                    # (twice) the background of the image, we have a representative region that
                    # is not affected by other sources like a nebula or a galaxy.
                    if largerCutOutMedian < 2 * median:

                        # Use photutils to fit the star with a 2D Gaussian
                        fwhml = fit_fwhm(starCutOut - median, fit_shape=(7, 7))
                        fwhmfit.append( fwhml)

                        results_table.add_row((source['xcentroid'], source['ycentroid'], source['peak'], fwhml, source['roundness2'], source['peak_median_ratio']))
                        #print(f"Star at position x: {x}, y: {y} has a FWHM of {fwhml:.2f} and a peak of {float(source['peak']):.2f}")

                    else:
                        logging.warning(f"Star rejected because of high background, probably a star in a nebula or galaxy : {largerCutOutMedian}, vs : {median} ")
                else:
                    logging.warning(f"Star at position x: {x}, y: {y} is too close to the edge")
            except Exception as e:
                logging.warning(f"Error fitting 2D Gaussian at position x: {x}, y: {y}")
                logging.warning(f"Cutout values: {starCutOut}")
                logging.warning(f"Exception: {e}")


        
        # Plot the image with detected stars on self.imageCanvas
        self.imageCanvas.figure.clear()
        self.ax1 = self.imageCanvas.figure.add_subplot(111)
        self.ax1.imshow(self.image_data, cmap='Greys', origin='lower', norm=LogNorm(), interpolation='nearest')
        self.ax1.set_title('Detected Stars')

        cpositions = np.transpose((results_table['xcentroid'], results_table['ycentroid']))
        apertures = CircularAperture(cpositions, r = 7)
        apertures.plot(color='red', lw=2.5, alpha=0.5, ax=self.ax1)
        
        for i, cposition in enumerate(cpositions):
            self.ax1.text(cposition[0], cposition[1], f'{results_table["fwhm"][i]:.2f}', color='red', fontsize=9, ha='right', va='top')
            self.ax1.text(cposition[0], cposition[1], f'{results_table["peak"][i]:.2f}', color='blue', fontsize=9, ha='left', va='bottom')
 
        self.imageCanvas.draw()
        
        # FWHM average
        average_fwhm = np.mean(fwhmfit)
        logging.info(f"Average FWHM: {average_fwhm:.2f}")

        # Eccentricity in DAOStarFinder is the ratio of the minor and major axes of the star
        roundness2_avg = np.mean(abs(results_table['roundness']))
        logging.info(f"Average Roundness: {roundness2_avg:.2f}")

        if average_fwhm and roundness2_avg:
            self.averageFwhmLabel.setText(f"<b>Average FWHM: {average_fwhm:.2f}</b>")
            self.averageRoundnessLabel.setText(f"<b>Average Roundness: {roundness2_avg:.2f}</b>")

        return np.array([ round(average_fwhm, 2), round(roundness2_avg, 2)])
