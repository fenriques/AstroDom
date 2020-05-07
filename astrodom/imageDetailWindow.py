from PyQt5 import QtSql
from PyQt5.QtWidgets import QDialog, QDataWidgetMapper
import sys
import logging
import matplotlib.pyplot as plt

from astropy.io import fits
from astropy.visualization import *
from matplotlib.colors import LogNorm
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
from matplotlib.figure import Figure

from .gui.imageDetailWindowGui import *

"""
When an image is double clicked on the image list
view, a mapper is used to show all informations about
that image.
Mapping a model implies that here the model can be 
edited / saved.
Matplot lib is used to show a not so well stretched 
preview of the image.
"""


class ImageDetailWindow(QDialog):
    logger = logging.getLogger(__name__)

    def __init__(self, imageListModel):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowTitle("Image Detail")
        self.imageListModel = imageListModel

    def plot(self, modelIndex):
        self.mapper = QDataWidgetMapper(self)
        self.mapper.setModel(self.imageListModel)
        self.mapper.addMapping(self.ui.lineEditFile, 1)
        self.mapper.addMapping(self.ui.lineEditHash, 2)
        self.mapper.addMapping(self.ui.lineEditTarget, 3)
        self.mapper.addMapping(self.ui.lineEditFrame, 4)
        self.mapper.addMapping(self.ui.lineEditFilter, 5)
        self.mapper.addMapping(self.ui.lineEditExposure, 6)
        self.mapper.addMapping(self.ui.lineEditTemp, 7)
        self.mapper.addMapping(self.ui.lineEditXbinning, 8)
        self.mapper.addMapping(self.ui.lineEditYbinning, 9)
        self.mapper.addMapping(self.ui.lineEditSiteLat, 10)
        self.mapper.addMapping(self.ui.lineEditSiteLong, 11)
        self.mapper.addMapping(self.ui.lineEditRa, 12)
        self.mapper.addMapping(self.ui.lineEditDec, 13)
        self.mapper.addMapping(self.ui.lineEditAlt, 14)
        self.mapper.addMapping(self.ui.lineEditAz, 15)
        self.mapper.addMapping(self.ui.lineEditDate, 16)
        self.mapper.addMapping(self.ui.lineEditGain, 17)
        self.mapper.addMapping(self.ui.lineEditOffset, 18)
        self.mapper.addMapping(self.ui.lineEditSubframeScale, 19)
        self.mapper.addMapping(self.ui.lineEditCameraGain, 20)
        self.mapper.addMapping(self.ui.lineEditCameraResolution, 21)
        self.mapper.addMapping(self.ui.lineEditScaleUnit, 22)
        self.mapper.addMapping(self.ui.lineEditDataUnit, 23)
        self.mapper.addMapping(self.ui.lineEditCsvFile, 24)
        self.mapper.addMapping(self.ui.lineEditFwhm, 25)
        self.mapper.addMapping(self.ui.lineEditEccentricity, 26)
        self.mapper.addMapping(self.ui.lineEditSnrWeight, 27)
        self.mapper.addMapping(self.ui.lineEditNoise, 28)
        self.mapper.setCurrentIndex(modelIndex.row())
        cr = self.imageListModel.index(modelIndex.row(), 1)
        t = self.imageListModel.data(cr, QtCore.Qt.DisplayRole)
        self.mplwidget = MatplotlibWidget(self.ui.MplWidget)
        self.mplwidget.setFileName(t)
        self.mplwidget.plot()
        self.show()


class MatplotlibWidget(Canvas):
    logger = logging.getLogger(__name__)

    def __init__(
        self, parent=None, title="Title", width=5, height=5, dpi=100, hold=True
    ):
        super(MatplotlibWidget, self).__init__(Figure())

        self.setParent(parent)
        self.figure = Figure(figsize=(width, height), dpi=dpi)
        self.figure.patch.set_facecolor("xkcd:black")

        self.canvas = Canvas(self.figure)

    def plot(self):
        self.figure.clear()

        self.axes = self.figure.add_subplot(1, 1, 1)
        self.figure.tight_layout()
        self.axes.axis("off")

        try:
            image = fits.getdata(self.fileName, ext=0)
            im = self.axes.imshow(image, cmap="gray", norm=LogNorm())
        except Exception as e:
            self.logger.error(e)
        self.canvas.draw()

    def setFileName(self, fileName):
        self.fileName = fileName
