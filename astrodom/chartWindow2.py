import sys
import pyqtgraph as pg
import datetime
import time
import numpy as np
import logging
import pandas as pd

from PyQt5.QtWidgets import QDialog
from .gui.chartWindowGui import *
from .pg_time_axis import DateAxisItem

"""
Charts are plotted using pyqtgrpah library.
Data are read directly from the image list 
model (imageListModel) so charts plot exactly 
what is shown in the image list table view.
Improvements needed:
- Filter colors should be moved in Settings
so that users can customize them.
- A factory to build plots, they are now 
build directly.
"""


class ChartWindow(QDialog):
    logger = logging.getLogger(__name__)

    def __init__(self, app):
        super().__init__()
        self.ui = Ui_Dialog2()
        self.ui.setupUi(self)
        self.setWindowTitle("Charts")
        self.app = app
        self.ui.pushButtonPlotChart.clicked.connect(self.plotData)

    def closeEvent(self, event):
        self.app.settings.setValue("sizeChartW", self.size())
        self.app.settings.setValue("posChartW", self.pos())
        try:
            self.close()
        except Exception as e:
            self.logger.debug(f"Closing not existing window {e}")
        event.accept()

    def plot(self, imageListModel):
        self.imageListModel = imageListModel
        try:
            self.resize(self.app.settings.value("sizeChartW"))
            self.move(self.app.settings.value("posChartW"))
        except Exception as e:
            self.logger.error(f"{e}")

        self.show()
        self.ui.labelColorL.setStyleSheet("color:rgb(244, 244, 244);font-weight:bold")
        self.ui.labelColorR.setStyleSheet("color:rgb(255,0,0);font-weight:bold")
        self.ui.labelColorG.setStyleSheet("color:rgb(0, 140, 55);font-weight:bold")
        self.ui.labelColorB.setStyleSheet("color:rgb(0,0,255);font-weight:bold")
        self.ui.labelColorHa.setStyleSheet("color:rgb(190, 255, 0);font-weight:bold")
        self.ui.labelColorOiii.setStyleSheet(
            "color:rgb(150, 200, 255);font-weight:bold"
        )
        self.ui.labelColorSii.setStyleSheet("color:rgb(255, 120, 190);font-weight:bold")
        self.ui.labelColorN.setStyleSheet("color:rgb(120,120,120);font-weight:bold")


        plist = []
        rowCount = self.imageListModel.rowCount()
        colCount = self.imageListModel.columnCount()
        for rc in range(rowCount):
            row = []
            for cc in range(colCount):
                item = self.imageListModel.data(
                    self.imageListModel.index(rc, cc))
                row.insert(cc, item)
            row.insert(cc+1, "")
            plist.append(row)
        
        headers = list(self.app.conf.keys())

        self.df = pd.DataFrame(plist, columns=headers)
        #self.df = self.df[["alt", "az"]]
        self.df.index.name='pos'
        self.df['date'] = pd.to_datetime(self.df['date']).astype(int) / 10**9
        pg.setConfigOption("background", "k")
        pg.setConfigOption("foreground", "w")
        pg.setConfigOption("antialias", True)
        pg.setConfigOptions(imageAxisOrder="row-major")
        
    def plotData(self):
        
        self.ui.graphWidget1.clear()
        x=self.ui.comboBoxX.currentText()
        y=self.ui.comboBoxY.currentText()
        self.ui.graphWidget1.setLabel("left", y, color="white", size=30)
        self.ui.graphWidget1.showGrid(x = True, y = True)
        
        axis3 = DateAxisItem(orientation="bottom")
        if x == 'date':
            axis3.attachToPlotItem(self.ui.graphWidget1.getPlotItem())
            axis3.setLabel("Time", units="h")
        else:
            axis3.detachFromPlotItem()
            self.ui.graphWidget1.setLabel("bottom", x, color="white", size=30)
            
        scatter1 = pg.ScatterPlotItem(brush=pg.mkBrush(width=5, color="w"), symbol="o")
        self.ui.graphWidget1.addItem(scatter1)
        scatter1.setData(self.df[x], self.df[y],brush=pg.mkBrush(width=5, color="w"))
        pen = pg.mkPen(color=(255, 0, 0))
        self.ui.graphWidget1.addLine(x=None, y=self.df[y].mean(), pen=pg.mkPen('w', width=1))
