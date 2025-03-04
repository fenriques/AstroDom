import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableView, QHeaderView
from PyQt6.QtCore import QAbstractTableModel, Qt
from astropy.io import fits
from astropy.visualization import *
import fitsio
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.colors import LogNorm
from matplotlib import colors, cm, pyplot as plt

class FitsHeaderModel(QAbstractTableModel):
    def __init__(self, header, parent=None):
        super(FitsHeaderModel, self).__init__(parent)
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

class FitsHeaderWidget(QWidget):
    def __init__(self, parent = None, fits_path = None):
        super().__init__(parent)
        if not fits_path:
            return None
        self.fits_path = '/home/ferrante/astrophoto/astrodom_test/Emilio/Helix/2024-11-12_21-38-03_-10.00_180.00s_150.fits'
        file_name = os.path.basename(self.fits_path)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)
        self.canvas = FigureCanvas(Figure(figsize=(self.width() / 100, 3)))
        layout.addWidget(self.canvas)

        self.ax = self.canvas.figure.subplots()
        image = self.loadAlternateRowsAndColumns()

        self.canvas.figure.patch.set_facecolor('black')
        self.ax.set_facecolor('black')
        norm = ImageNormalize(image, interval=ZScaleInterval(contrast=0.05), stretch=AsinhStretch())      
        self.ax.imshow(image, cmap=cm.gray, norm=norm, origin="lower")

        self.canvas.mpl_connect("button_press_event", self.on_press)
        self.canvas.mpl_connect("button_release_event", self.on_release)
        self.canvas.mpl_connect("button_press_event", self.on_double_click)
        self.rect = None

        self.tableView = QTableView(self)

        layout.addWidget(self.tableView)

        self.loadFitsHeader()

    def loadFitsHeader(self):
        with fits.open(self.fits_path) as hdul:
            header = hdul[0].header
            model = FitsHeaderModel(header)
            self.tableView.setModel(model)
            self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)


    def loadAlternateRowsAndColumns(self):
        # Load alternate rows and columns from the FITS image
        with fitsio.FITS(self.fits_path) as fits:
            if len(fits) > 0 and fits[0].has_data():
                image_data = fits[0].read()
                image = image_data[::4, ::4]  # Read alternate rows and columns
                return image
            else:
                return np.zeros((1, 1))  # Return a default image if no data is present
        
    def on_press(self, event):
        if event.inaxes != self.ax:
            return
        self.rect = plt.Rectangle((event.xdata, event.ydata), 0, 0, linewidth=1, edgecolor='r', facecolor='none')
        self.ax.add_patch(self.rect)
        self.canvas.draw()

    def on_release(self, event):
        if event.inaxes != self.ax or self.rect is None:
            return
        x0, y0 = self.rect.get_xy()
        x1, y1 = event.xdata, event.ydata
        self.rect.set_width(x1 - x0)
        self.rect.set_height(y1 - y0)
        self.canvas.draw()
        self.zoom(x0, y0, x1, y1)


    def zoom(self, x0, y0, x1, y1):
        x0, x1 = sorted([int(x0), int(x1)])
        y0, y1 = sorted([int(y0), int(y1)])
        image = self.loadAlternateRowsAndColumns()
        zoomed_image = image[y0:y1, x0:x1]
        self.ax.clear()
        norm = ImageNormalize(zoomed_image, interval=ZScaleInterval(contrast=0.05), stretch=AsinhStretch())
        self.ax.imshow(zoomed_image, cmap=cm.gray, norm=norm, origin="lower")
        self.canvas.draw()
    
    def reset_zoom(self):
        image = self.loadAlternateRowsAndColumns()
        self.ax.clear()
        norm = ImageNormalize(image, interval=ZScaleInterval(contrast=0.05), stretch=AsinhStretch())
        self.ax.imshow(image, cmap=cm.gray, norm=norm, origin="lower")
        self.canvas.draw()

    def on_double_click(self, event):
        if event.dblclick:
            self.reset_zoom()

