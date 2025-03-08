import os
import numpy as np
import logging
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableView, QHeaderView
from PyQt6.QtCore import QAbstractTableModel, Qt
from astropy.io import fits
from astropy.visualization import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT
from matplotlib.figure import Figure
from matplotlib import colors, cm, pyplot as plt

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

class PreviewAndDataWidget(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.resetZoom = True

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        #Add the image preview canvas
        self.canvas = FigureCanvas(Figure(figsize=(self.width() / 100, 3)))
        self.ax = self.canvas.figure.subplots()
        self.canvas.figure.patch.set_facecolor('gray')
        self.ax.set_facecolor('black')
        self.resetZoom = True
        self.connectZoomEvent()
        
        # Image preview controls
        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        # Add the keyowords table to the layout 
        self.tableView = QTableView(self)
        layout.addWidget(self.tableView)



    def setItemsAtSelectedRow(self, itemsAtSelectedRow):
        self.itemsAtSelectedRow = itemsAtSelectedRow
        self.fits_path = self.itemsAtSelectedRow[25]

        file_name = os.path.basename(self.fits_path)

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

                height, width = image_data.shape
                logging.debug(f"Image width: {width}, Image height: {height}")

                # Scale the image to fit the canvas size twice
                imageScaleFactor = max(int(width / (320*2)), 1)
                logging.debug(f"Scale factor: {imageScaleFactor}")

                # A new image is retaining the zoom level from the previous image
                if self.resetZoom == False and hasattr(self, 'zoom_rect'):
                    xlim, ylim = self.zoom_rect
                    logging.debug(f"Zoom rect: {xlim}, {ylim}")

                    # the zoomed image needs its own scale factor
                    self.zoomScaleFactor = max(int((xlim[1] - xlim[0])*imageScaleFactor / (320*2)), 1)
                    logging.debug(f"Zoom scale factor: {self.zoomScaleFactor}")

                    # The original image is read again so the rectangle has to be scaled back to its original size 
                    x_start, x_end = int(xlim[0]*imageScaleFactor), int(xlim[1]*imageScaleFactor)
                    y_start, y_end = int(ylim[0]*imageScaleFactor), int(ylim[1]*imageScaleFactor)
                    x_start = max(x_start, 0)
                    x_end = max(x_end, 0)
                    y_start = max(y_start, 0)
                    y_end = max(y_end, 0)
                    logging.debug(f"Zoom rect scaled: {x_start}, {x_end}, {y_start}, {y_end}")
                    try:
                        self.image = image_data[y_start:y_end:self.zoomScaleFactor, x_start:x_end:self.zoomScaleFactor]
                    except Exception as e:
                        logging.error(f"Error in zooming: {e}")
                        
                else:
                    self.image = image_data[::imageScaleFactor, ::imageScaleFactor]
               
                norm = ImageNormalize(self.image, interval=ZScaleInterval(contrast=0.05), stretch=AsinhStretch())      

                try:
                    self.ax.imshow(self.image, cmap=cm.gray, norm=norm,origin='lower')
                except Exception as e:
  
                    logging.error(f"Error in plotting image: {e}")
                    self.ax.text(0.5, 0.5, 'No data', color='white', ha='center', va='center')

                self.canvas.draw()

            else:
                logging.error("No data in the FITS file")
                self.image = np.zeros((1, 1))  # Return a default image if no data is present
  

    def onZoom(self, event):
        if event.name == 'button_release_event' :
            self.resetZoom =False
            self.zoom_rect = self.ax.get_xlim(), self.ax.get_ylim()
            logging.debug(f"Zoom rect onZoom: {self.zoom_rect}")

    def connectZoomEvent(self):
        self.canvas.mpl_connect('button_release_event', self.onZoom)

        self.canvas.mpl_connect('button_press_event', self.onDoubleClick)

    def onDoubleClick(self, event):
        if event.dblclick:
            self.resetZoom = True
            self.plotImage()
