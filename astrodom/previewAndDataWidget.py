import numpy as np
import logging
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableView, QHeaderView,QSizePolicy
from PyQt6.QtCore import QAbstractTableModel, Qt
from astropy.io import fits
from astropy.visualization import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT
from matplotlib.figure import Figure
from matplotlib import colors, cm, pyplot as plt

logging.getLogger('matplotlib.font_manager').setLevel(logging.WARNING)

# This class is the model for the FITS keywords table.
class KeywordsModel(QAbstractTableModel):
    def __init__(self, header, parent=None):
        super(KeywordsModel, self).__init__(parent)
        self.header = header
        self.keys = list(header.keys())
        self.values = list(header.values())

    def rowCount(self, parent=None):
        return len(self.keys)

    def columnCount(self, parent=None):
        return 2

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole:
            return None
        if index.column() == 0:
            return self.keys[index.row()]
        elif index.column() == 1:
            return self.values[index.row()]

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            if section == 0:
                return "Keyword"
            elif section == 1:
                return "Value"
        return None
    
# Important to understand the flow in this class. The class is instantiated in the main window
# and the itemsAtSelectedRow is set  when the user clicks a row in the table.
# When a new row is clicked, the setItemsAtSelectedRow method is called and the plot method of this class
# is called. 
# The zoom events are tracked by the onPress and onRelease methods and dimensions stored in class variables.
# So that when a new row is clicked, the plot method can use the stored dimensions to plot the image with the
# same zoom level as the previous image.
class PreviewAndDataWidget(QWidget):
    def __init__(self, previewWidth=320, parent=None):
        super().__init__(parent)
        self.resetZoom = True
        self.x_start = 0
        self.x_end = 0
        self.y_start = 0
        self.y_end = 0
        self.previewWidth = previewWidth
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        #Add the image preview canvas
        self.canvas = FigureCanvas(Figure(figsize=(self.width() / 100, self.width() / 100)))
        self.ax = self.canvas.figure.subplots()
        self.canvas.figure.patch.set_facecolor('gray')
        self.ax.set_facecolor('black')
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.resetZoom = True
        self.connectZoomEvent()
        
        layout.addWidget(self.canvas)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.canvas.updateGeometry()
        # Image preview controls
        self.toolbar = NavigationToolbar2QT(self.canvas, self)
        self.toolbar.zoom()
        self.toolbar.hide()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        # Add the keyowords table to the layout 
        self.tableView = QTableView(self)
        layout.addWidget(self.tableView)

    # Called by the main window when a blink item is selected
    def setBlinkItem(self, fits_path):
        self.fits_path = fits_path
        logging.debug(f"Setting blink item: {self.fits_path}")
        self.plotImage()

    # Called by the main window when a new row is clicked
    def setItemsAtSelectedRow(self, itemsAtSelectedRow):

        self.itemsAtSelectedRow = itemsAtSelectedRow
        self.fits_path = self.itemsAtSelectedRow[25]

        self.plotImage()
        self.printKeywords()

    def printKeywords(self):
        try:
            with fits.open(self.fits_path) as hdul:
                header = hdul[0].header
                keywordsModel = KeywordsModel(header)
                self.tableView.setModel(keywordsModel)
                self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        except Exception as e:  
            logging.error(f"Cannot open fits file: {e}")
            return

    # Plot the preview image
    def plotImage(self):

        self.ax.clear()

        with fits.open(self.fits_path) as hdul:
            if len(hdul) > 0 and hdul[0].data is not None:
                image_data = hdul[0].data

                # Get the real image dimensions, without any zoom
                self.height, self.width = image_data.shape
                logging.debug(f"Image width: {self.width}, Image height: {self.height}")

                # Scale the image to fit the canvas size twice
                # Or another way to see it, a small canvas  can have a lower resolution image
                # The scale factor will be used as the sampling reading of the image
                self.imageScaleFactor = max(int(self.width / (self.previewWidth * 2)), 1)
                logging.debug(f"Scale factor: {self.imageScaleFactor}")

                if self.x_end == 0:
                    #This case is on first load or when the image zoom is reset
                    self.image = image_data[0:self.height:self.imageScaleFactor, 0:self.width:self.imageScaleFactor]
                else:
                    #This case is when the user zooms in the image
                    self.image = image_data[self.y_start:self.y_end:self.zoomScaleFactor, self.x_start:self.x_end:self.zoomScaleFactor]

                norm = ImageNormalize(self.image, interval=ZScaleInterval(contrast=0.05), stretch=AsinhStretch())      

                try:
                    self.ax.imshow(self.image, cmap=cm.gray, norm=norm,origin='lower')
                    self.ax.set_xticks([])
                    self.ax.set_yticks([])
                except Exception as e:
                    logging.error(f"Error in plotting image: {e}")

                self.canvas.draw()

            else:
                logging.error("No data in the FITS file")
                self.image = np.zeros((1, 1))  # Return a default image if no data is present
  
    def onPress(self, event):
        # Zoom events are only tracked when the toolbar mode is 'zoom rect'
        if self.toolbar.mode == 'zoom rect':
            # Press is the starting point of the zoom rectangle
            self.press = (event.xdata, event.ydata)
        
    def onRelease(self, event):
        # Zoom events are only tracked when the toolbar mode is 'zoom rect'
        if self.toolbar.mode == 'zoom rect':
            # Release is the ending point of the zoom rectangle
            self.release = (event.xdata, event.ydata)

            if self.press and self.release:
                # If the rectangle is big enough, zoom in the image
                if abs(self.release[1] - self.press[1]) > 10 and abs(self.release[0] - self.press[0]) > 10 :
                    self.x_start = int(min(self.press[0], self.release[0]) * self.imageScaleFactor)
                    self.x_end = int(max(self.press[0], self.release[0]) * self.imageScaleFactor)
                    self.y_start = int(min(self.press[1], self.release[1]) * self.imageScaleFactor)
                    self.y_end = int(max(self.press[1], self.release[1]) * self.imageScaleFactor)

                    self.resetZoom = False
                    self.zoomScaleFactor = max(int(abs(self.x_end  - self.x_start) / (self.previewWidth*2)), 1)

                else:      
                    # If the rectangle is too small, reset the zoom, this is the case of a double click
                    # to reset the zoom.          
                    self.resetZoom = True
                    self.zoomScaleFactor = self.imageScaleFactor
                    self.x_end=self.width
                    self.y_end=self.height
                    self.x_start=0          
                    self.y_start=0
                    self.plotImage()

                logging.debug(f"Zoom scale factor: {self.zoomScaleFactor}")
                logging.debug(f"New coordinates: x_start={self.x_start}, x_end={self.x_end}, y_start={self.y_start}, y_end={self.y_end}")

    def connectZoomEvent(self):
        self.canvas.mpl_connect('button_press_event', self.onPress)
        self.canvas.mpl_connect('button_release_event', self.onRelease)


