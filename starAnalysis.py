
import numpy as np,logging
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from photutils.detection import DAOStarFinder
from photutils.psf import fit_2dgaussian, fit_fwhm
from photutils.aperture import CircularAperture
from astropy.io import fits
from astropy.stats import sigma_clipped_stats,gaussian_sigma_to_fwhm
from astropy.modeling import models, fitting
import astropy.units as u
from settings import *
from loadSettings import *  
from PyQt6.QtWidgets import QApplication, QDialog, QLabel,QVBoxLayout, QGridLayout,QHBoxLayout, QLineEdit, QComboBox, QTableView, QWidget
from PyQt6.QtCore import QAbstractTableModel, Qt
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT, FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from astropy.table import QTable
from pandas import DataFrame
from PyQt6.QtWidgets import QSpacerItem, QSizePolicy
from PyQt6.QtWidgets import QGroupBox


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
    def __init__(self, parent = None, imageId = None):
        super().__init__(parent)

        #fits_path = '/home/ferrante/astrophoto/M81/1810/ngc253_5s_7150f.fits' # Path to the FITS file or directory containing FITS files
        self.fits_path = '/home/ferrante/astrophoto/M42/M_42_LIGHT_R_180s_BIN1_0C_004_20240312_204325_430_GA_0_OF_0_E.FIT' # Path to the FITS file or directory containing FITS files
        self.cropFactor = 2 # Crop the image by cropFactor of its width and height (faster processing)
        self.nStars = 30 # Choose randomSources (faster processing)
        self.threshold = 20 #threshold for star detection, 20 seems to work well
        self.pixelScale = 0.73 # pixel scale in arcsec/pixel
        self.bit = 16 # bit depth of the sensor, used to cut saturated stars
        self.bin = 1 # binning factor
        self.radius = 7*self.bin # radius of the aperture for the star measurement

    
        self.setWindowTitle("Star analysis Tool") 
        self.setGeometry(100, 100, 1200, 800)

        # Main layout
        main_layout = QVBoxLayout(self)

        # Control panel layout
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
        self.applyButton.clicked.connect(self.on_apply_clicked) # Create a grid layout for the control panel

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
        control_grid_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum), 0, 6, 2, 1)
        control_grid_layout.addWidget(self.applyButton, 2, 0, 1, 2)
        control_panel.setLayout(control_grid_layout)
        # Group box for control panel
        control_group_box = QGroupBox("Star Detection Parameters", self)
        control_group_box.setLayout(control_grid_layout)

        # Add the group box to the main layout
        main_layout.addWidget(control_group_box)
        # Bottom layout
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(10)

        # Add QTableView to the left side
        self.table_view = QTableView(self)
        bottom_layout.addWidget(self.table_view, 1)

        # Add two matplotlib canvases to the right side
        canvas_widget = QWidget(self)
        canvas_layout = QVBoxLayout(canvas_widget)
        canvas_layout.setContentsMargins(0, 0, 0, 0)
        canvas_layout.setSpacing(10)


        self.canvas1 = FigureCanvas(Figure(figsize=(5, 3)))
        self.canvas2 = FigureCanvas(Figure(figsize=(5, 3)))
        self.toolbar = NavigationToolbar2QT(self.canvas1, self)
        canvas_layout.addWidget(self.toolbar)
        canvas_layout.addWidget(self.canvas1)
        canvas_layout.addWidget(self.canvas2)

        bottom_layout.addWidget(canvas_widget, 1)

        # Add control panel and bottom layout to the main layout
        main_layout.addWidget(control_panel)
        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)

    def on_apply_clicked(self):        
        self.data_stars = self.measure_stars(self.fits_path)
        print(self.data_stars)
        print(self.sources)
        df_t = DataFrame(np.array(self.sources))
        df_t = df_t[['id', 'xcentroid', 'ycentroid', 'sharpness', 'roundness2', 'peak', 'peak_median_ratio']].round(2)
        model = QTableModel(df_t)
        self.table_view.setModel(model)
        self.table_view.clicked.connect(self.on_table_row_clicked)

    def on_table_row_clicked(self, index):
        model_id = index.row()
        self.plot_star(model_id)

    def plot_star(self, model_id):
        self.canvas2.figure.clear()
        source = self.sources[model_id]
        x = source['xcentroid']
        y = source['ycentroid']
        radius = 7  # Assuming the radius used in measure_stars
        self.ax1.plot(x, y, 'ro', markersize=4)
        self.canvas1.draw()
        # 
        # Crop the image around the star
        cutout = self.image_data[int(y-radius):int(y+radius), int(x-radius):int(x+radius)]

        # Create a meshgrid for the surface plot
        x_grid, y_grid = np.meshgrid(np.arange(cutout.shape[1]), np.arange(cutout.shape[0]))

        # Plot the star on self.canvas2 as a 3D surface plot
        ax2 = self.canvas2.figure.add_subplot(111, projection='3d')
        ax2.clear()
        ax2.plot_surface(x_grid, y_grid, cutout, cmap='viridis')
        ax2.set_title(f'Star at ({x:.2f}, {y:.2f})')
        self.canvas2.draw()

    def measure_stars(self,fits_file):
    
        cropFactor = 2 # Crop the image by cropFactor of its width and height (faster processing)
        randomSources = 30 # Choose randomSources (faster processing)
        threshold = 20 #threshold for star detection, 20 seems to work well
        pixelScale = 0.73 # pixel scale in arcsec/pixel
        bit = 16 # bit depth of the sensor, used to cut saturated stars
        bin = 1 # binning factor
        radius = 7*bin # radius of the aperture for the star measurement
        mode = "both" # "micah" or "astropy" or "both"
        plot_image = False # plot the image with the detected stars
    
        fwhm_micah = []
        ecc = []
        fwhmfit = []
        average_fwhm_micah, average_fwhm,average_ecc = 0,0,0

        # Load the FITS file
        hdu_list = fits.open(fits_file)
        self.image_data = hdu_list[0].data
        hdu_list.close()

        # Crop the image by cropFactor of its width and height (faster processing)
        height, width = self.image_data.shape
        crop_height = height // cropFactor
        crop_width = width // cropFactor
        start_y = (height - crop_height) // 2
        start_x = (width - crop_width) // 2
        self.image_data = self.image_data[start_y:start_y + crop_height, start_x:start_x + crop_width]

        # Calculate basic statistics
        mean, median, std = sigma_clipped_stats(self.image_data, sigma = 3.0)
        print(f"Mean: {mean:.2f}, Median: {median:.2f}, Std: {std:.2f}")
        # Detect stars
        daofind = DAOStarFinder(fwhm = 3.0, threshold = threshold*std)
        sources = daofind(self.image_data - median)
        print(f"Number of stars detected by DAO: {len(sources)}")

        # Cutting saturated stars
        sources = sources[sources['peak'] < (2**bit)*0.98 ]
        print(f"Number of non clipped stars (< 98% peak): {len(sources)}")
        print(sources)
        
        # Cutting weak stars (noise)
        #sources = sources[sources['peak'] > median*10.0]
        sources['peak_median_ratio'] = sources['peak'] / median
        sources.sort('peak_median_ratio', reverse=True)
        print(f"Number of non clipped  stars above background*10: {len(sources)}")
        # Exclude sources with flux/peak too high, it is likely to be in  a galaxy or in a nebula too bright
        #sources = sources[sources['peak'] / sources['flux'] > 0.1]
        print(f"Number of stars with flux/peak too high: {len(sources)}")

        if len(sources) == 0:
            logging.warning("No stars detected")
            return  
        
        # Choose randomSources (faster processing)
        np.random.seed(42)  # For reproducibility
        if len(sources) > randomSources:
            sources = sources[np.random.choice(len(sources), randomSources, replace=False)]
            #sources.sort('peak', reverse=True)
            #sources = sources[:randomSources]
        self.sources = sources
        # Calculate and print the average peak value
        average_peak = np.mean(sources['peak'])
        print(f"Average Peak: {average_peak:.2f}")

        print(f"Mean: {mean:.2f}, Median: {median:.2f}, Std: {std:.2f}")
        print(f"Number of sources detected: {len(sources)}")
        results_table = QTable(names=('xcentroid', 'ycentroid', 'peak', 'fwhm', 'peak_median_ratio'), dtype=('f4', 'f4', 'f4', 'f4', 'f4'))

        if mode == "micah" or mode == "both":
            for source in sources:
                x = source['xcentroid']
                y = source['ycentroid']
                try:
                    if (x > radius and x < (width - radius) and y > radius and y < (height - radius)):
                    # Assuming you have the star's image data in `data` and the aperture in `aperture`
                        cutout = self.image_data[int(y-radius):int(y+radius), int(x-radius):int(x+radius)]
                        cutout2 = self.image_data[int(y-10*radius):int(y+10*radius), int(x-10*radius):int(x+10*radius)]
                        cutout_mean, cutout_median, cutout_std = sigma_clipped_stats(cutout, sigma = 3.0)
                        print(x,y)
                        cutout2_mean, cutout2_median, cutout2_std = sigma_clipped_stats(cutout2, sigma = 3.0)
                        print(f"Cutout Mean: {cutout_mean:.2f}, Cutout Median: {cutout_median:.2f}, Cutout Std: {cutout_std:.2f}")
                        print(f"Cutout2 Mean: {cutout2_mean:.2f}, Cutout Median: {cutout2_median:.2f}, Cutout Std: {cutout2_std:.2f}")
                        print("------------------------")
                        if cutout2_median < 2 * median:

                            # Fit a 2D Gaussian
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
                            
                            print(f"FWHM Micah: {np.sqrt(fwhm_x * fwhm_y):.2f}")
                            fwhml = fit_fwhm(cutout-median, fit_shape=(7, 7))
                            fwhmfit.append( fwhml)

                            results_table.add_row((source['xcentroid'], source['ycentroid'], source['peak'], fwhml, source['peak_median_ratio']))

                        else:
                            print(f"Star rejected because of high background : {cutout2_median}, vs : {median} ")
                            #print(f"FWHM_x: {fwhm_x}, FWHM_y: {fwhm_y}")
                    else:
                        print(f"Star at position x: {x}, y: {y} is too close to the edge")
                except Exception as e:
                    print(f"Error fitting 2D Gaussian at position x: {x}, y: {y}")
                    print(f"Cutout values: {cutout}")
                    print(f"Exception: {e}")
        print(results_table)

        roundness1_avg = np.mean(abs(sources['roundness1']))
        roundness2_avg = np.mean(abs(sources['roundness2']))
        print(f"Average Roundness1: {roundness1_avg:.2f}")
        print(f"Average Roundness2: {roundness2_avg:.2f}")

        if mode == "astropy" or mode ==  "both":
            xypos = list(zip(sources['xcentroid'], sources['ycentroid']))

            psfphot = fit_2dgaussian(self.image_data, xypos=xypos, fix_fwhm=False, fit_shape=(7, 7))
            phot_tbl = psfphot.results
            fwhm = fit_fwhm(self.image_data, xypos=xypos, fit_shape=(7, 7))
            #print(fwhm)
        # Calculate and print the average FWHM value
        if mode == "micah" or mode == "both": 
            average_fwhm_micah = np.mean(fwhm_micah)
            print(f"Average FWHM Micah: {average_fwhm_micah:.2f}")
            average_ecc = np.mean(ecc)
            print(f"Average ecc: {average_ecc:.2f}")
        
            average_fwhmfit = np.mean(fwhmfit)
            print(f"Average FWHM fit: {average_fwhmfit:.2f}")   
        if mode == "astropy" or mode == "both": 
            average_fwhm = np.mean(fwhm)
            print(f"Average FWHM Astropy: {average_fwhm:.2f}")


        cpositions = np.transpose((results_table['xcentroid'], results_table['ycentroid']))
        apertures = CircularAperture(cpositions, r = radius)
        
        # Plot the image with detected stars on self.canvas1
        self.ax1 = self.canvas1.figure.add_subplot(111)
        self.ax1.imshow(self.image_data, cmap='Greys', origin='lower', norm=LogNorm(), interpolation='nearest')
        apertures.plot(color='red', lw=2.5, alpha=0.5, ax=self.ax1)
        for i, cposition in enumerate(cpositions):
            self.ax1.text(cposition[0], cposition[1], f'{results_table["fwhm"][i]:.2f}', color='red', fontsize=9, ha='right', va='top')
            self.ax1.text(cposition[0], cposition[1], f'{results_table["peak"][i]:.2f}', color='blue', fontsize=9, ha='left', va='bottom')
 
        self.canvas1.draw()

        return np.array([round(average_fwhm_micah, 2), round(average_fwhm, 2), round(average_ecc, 2)])
