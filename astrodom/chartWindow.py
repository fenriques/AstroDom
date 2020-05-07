import sys
import pyqtgraph as pg
import datetime
import time
import numpy as np
import logging

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

    def closeEvent(self, event):
        event.accept()

    def plot(self, imageListModel):
        self.imageListModel = imageListModel
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

        frame = []
        filters = []
        alt = []
        az = []
        fwhm = []
        eccentricity = []
        noise = []
        snrweight = []
        datetimestr = []
        timestampObj = []
        colors = []
        g1 = []
        g2 = []
        g3 = []
        g4 = []
        g5 = []
        g6 = []
        g7 = []
        g8 = []
        g9 = []
        g10 = []
        g11 = []
        g12 = []
        g13 = []
        g14 = []
        g15 = []

        for row in range(imageListModel.rowCount()):
            indexFilters = imageListModel.index(row, 5)
            indexAlt = imageListModel.index(row, 14)
            indexAz = imageListModel.index(row, 15)
            indexDatetimestr = imageListModel.index(row, 16)
            indexFwhm = imageListModel.index(row, 25)
            indexEccentricity = imageListModel.index(row, 26)
            indexSnrweight = imageListModel.index(row, 27)
            indexNoise = imageListModel.index(row, 28)

            filters.append((str(imageListModel.data(indexFilters))))
            alt.append((float(imageListModel.data(indexAlt))))
            az.append((float(imageListModel.data(indexAz))))
            datetimestr.append((str(imageListModel.data(indexDatetimestr))))
            fwhm.append((float(imageListModel.data(indexFwhm))))
            eccentricity.append((float(imageListModel.data(indexEccentricity))))
            snrweight.append((float(imageListModel.data(indexSnrweight))))
            noise.append((float(imageListModel.data(indexNoise))))

            # pg only works with timestamps
            date_time_obj = datetime.datetime.strptime(
                datetimestr[row], "%Y-%m-%dT%H:%M:%S"
            )
            timestampObj.append(datetime.datetime.timestamp(date_time_obj))

            # colors

            if filters[row] in self.app.confFilters["L"]:
                colors.append(pg.mkBrush(244, 244, 244, 255))
            elif filters[row] in self.app.confFilters["R"]:
                colors.append(pg.mkBrush(255, 0, 0, 255))
            elif filters[row] in self.app.confFilters["B"]:
                colors.append(pg.mkBrush(0, 0, 255, 255))
            elif filters[row] in self.app.confFilters["G"]:
                colors.append(pg.mkBrush(0, 140, 55, 255))
            elif filters[row] in self.app.confFilters["Ha"]:
                colors.append(pg.mkBrush(190, 255, 0, 255))
            elif filters[row] in self.app.confFilters["Oiii"]:
                colors.append(pg.mkBrush(150, 200, 255, 255))
            elif filters[row] in self.app.confFilters["Sii"]:
                colors.append(pg.mkBrush(255, 120, 190, 255))
            else:
                colors.append(pg.mkBrush(120, 120, 120, 255))

            # create data sets
            g1.append({"pos": (alt[row], az[row]), "brush": colors[row]})
            g2.append({"pos": (az[row], alt[row]), "brush": colors[row]})
            g3.append({"pos": (timestampObj[row], alt[row]), "brush": colors[row]})
            g4.append({"pos": (alt[row], fwhm[row]), "brush": colors[row]})
            g5.append({"pos": (az[row], fwhm[row]), "brush": colors[row]})
            g6.append({"pos": (timestampObj[row], fwhm[row]), "brush": colors[row]})
            g7.append({"pos": (alt[row], eccentricity[row]), "brush": colors[row]})
            g8.append({"pos": (az[row], eccentricity[row]), "brush": colors[row]})
            g9.append(
                {"pos": (timestampObj[row], eccentricity[row]), "brush": colors[row]}
            )
            g10.append({"pos": (alt[row], noise[row]), "brush": colors[row]})
            g11.append({"pos": (az[row], noise[row]), "brush": colors[row]})
            g12.append({"pos": (timestampObj[row], noise[row]), "brush": colors[row]})
            g13.append({"pos": (alt[row], snrweight[row]), "brush": colors[row]})
            g14.append({"pos": (az[row], snrweight[row]), "brush": colors[row]})
            g15.append(
                {"pos": (timestampObj[row], snrweight[row]), "brush": colors[row]}
            )

        pg.setConfigOption("background", "k")
        pg.setConfigOption("foreground", "w")
        pg.setConfigOption("antialias", True)
        pg.setConfigOptions(imageAxisOrder="row-major")

        # Graph1: Alt-Az
        self.ui.graphWidget1.setLabel("left", "Az (deg)", color="white", size=30)
        self.ui.graphWidget1.setLabel("bottom", "Alt (deg)", color="white", size=30)
        self.ui.graphWidget1.showGrid(x=True, y=True)

        scatter1 = pg.ScatterPlotItem(brush=pg.mkBrush(width=5, color="w"), symbol="o")
        self.ui.graphWidget1.addItem(scatter1)
        scatter1.setData(g1)
        self.lrAlt = pg.LinearRegionItem([100, 200])
        self.lrAlt.setZValue(-10)
        self.ui.graphWidget1.addItem(self.lrAlt)

        # Graph2: AZ-Alt
        self.ui.graphWidget2.setLabel("left", "Alt (deg)", color="white", size=30)
        self.ui.graphWidget2.setLabel("bottom", "Az (deg)", color="white", size=30)
        self.ui.graphWidget2.showGrid(x=True, y=True)

        scatter2 = pg.ScatterPlotItem(brush=pg.mkBrush(width=5, color="w"), symbol="o")
        self.ui.graphWidget2.addItem(scatter2)
        scatter2.setData(g2)
        self.lrAz = pg.LinearRegionItem([100, 200])
        self.lrAz.setZValue(-10)
        self.ui.graphWidget2.addItem(self.lrAz)

        # Graph3: Time-Alt
        self.ui.graphWidget3.setLabel("left", "Alt (deg)", color="white", size=30)
        self.ui.graphWidget3.showGrid(x=True, y=True)

        axis3 = DateAxisItem(orientation="bottom")
        axis3.attachToPlotItem(self.ui.graphWidget3.getPlotItem())
        axis3.setLabel("Time", units="h")

        scatter3 = pg.ScatterPlotItem(brush=pg.mkBrush(width=5, color="w"), symbol="o")
        self.ui.graphWidget3.addItem(scatter3)
        scatter3.setData(g3)
        self.lrDate = pg.LinearRegionItem([min(timestampObj), max(timestampObj)])
        self.lrDate.setZValue(-10)
        self.ui.graphWidget3.addItem(self.lrDate)

        # Graph4: Alt-FWHM
        self.ui.graphWidget4.setLabel("bottom", "Alt (deg)", color="white", size=30)
        self.ui.graphWidget4.setLabel("left", "FWHM", color="white", size=30)
        self.ui.graphWidget4.showGrid(x=True, y=True)

        scatter4 = pg.ScatterPlotItem(brush=pg.mkBrush(width=5, color="w"), symbol="o")
        self.ui.graphWidget4.addItem(scatter4)
        scatter4.setData(g4)

        # Graph5: Az-FWHM
        self.ui.graphWidget5.setLabel("bottom", "Az (deg)", color="white", size=30)
        self.ui.graphWidget5.setLabel("left", "FWHM", color="white", size=30)
        self.ui.graphWidget5.showGrid(x=True, y=True)

        scatter5 = pg.ScatterPlotItem(brush=pg.mkBrush(width=5, color="w"), symbol="o")
        self.ui.graphWidget5.addItem(scatter5)
        scatter5.setData(g5)

        # Graph6: Time-FWHM
        self.ui.graphWidget6.setLabel("left", "FWHM", color="white", size=30)
        self.ui.graphWidget6.showGrid(x=True, y=True)

        axis6 = DateAxisItem(orientation="bottom")
        axis6.attachToPlotItem(self.ui.graphWidget6.getPlotItem())
        axis6.setLabel("Time", units="h")

        scatter6 = pg.ScatterPlotItem(brush=pg.mkBrush(width=5, color="w"), symbol="o")
        self.ui.graphWidget6.addItem(scatter6)
        scatter6.setData(g6)

        # Graph7: Alt-Eccentricity
        self.ui.graphWidget7.setLabel("bottom", "Alt (deg)", color="white", size=30)
        self.ui.graphWidget7.setLabel("left", "Eccentricity", color="white", size=30)
        self.ui.graphWidget7.showGrid(x=True, y=True)

        scatter7 = pg.ScatterPlotItem(brush=pg.mkBrush(width=5, color="w"), symbol="o")
        self.ui.graphWidget7.addItem(scatter7)
        scatter7.setData(g7)

        # Graph8: Az-Eccentricity
        self.ui.graphWidget8.setLabel("bottom", "Az (deg)", color="white", size=30)
        self.ui.graphWidget8.setLabel("left", "Eccentricity", color="white", size=30)
        self.ui.graphWidget8.showGrid(x=True, y=True)

        scatter8 = pg.ScatterPlotItem(brush=pg.mkBrush(width=5, color="w"), symbol="o")
        self.ui.graphWidget8.addItem(scatter8)
        scatter8.setData(g8)

        # Graph9: Time-Eccentricity
        self.ui.graphWidget9.setLabel("left", "Eccentricity", color="white", size=30)
        self.ui.graphWidget9.showGrid(x=True, y=True)

        axis9 = DateAxisItem(orientation="bottom")
        axis9.attachToPlotItem(self.ui.graphWidget9.getPlotItem())
        axis9.setLabel("Time", units="h")

        scatter9 = pg.ScatterPlotItem(brush=pg.mkBrush(width=5, color="w"), symbol="o")
        self.ui.graphWidget9.addItem(scatter9)
        scatter9.setData(g9)

        # Graph10: Alt-Noise
        self.ui.graphWidget10.setLabel("bottom", "Alt (deg)", color="white", size=30)
        self.ui.graphWidget10.setLabel("left", "Noise", color="white", size=30)
        self.ui.graphWidget10.showGrid(x=True, y=True)

        scatter10 = pg.ScatterPlotItem(brush=pg.mkBrush(width=5, color="w"), symbol="o")
        self.ui.graphWidget10.addItem(scatter10)
        scatter10.setData(g10)

        # Graph11: Az-Noise
        self.ui.graphWidget11.setLabel("bottom", "Az (deg)", color="white", size=30)
        self.ui.graphWidget11.setLabel("left", "Noise", color="white", size=30)
        self.ui.graphWidget11.showGrid(x=True, y=True)

        scatter11 = pg.ScatterPlotItem(brush=pg.mkBrush(width=5, color="w"), symbol="o")
        self.ui.graphWidget11.addItem(scatter11)
        scatter11.setData(g11)

        # Graph12: Time-Noise
        self.ui.graphWidget12.setLabel("left", "Noise", color="white", size=30)
        self.ui.graphWidget12.showGrid(x=True, y=True)

        axis12 = DateAxisItem(orientation="bottom")
        axis12.attachToPlotItem(self.ui.graphWidget12.getPlotItem())
        axis12.setLabel("Time", units="h")

        scatter12 = pg.ScatterPlotItem(brush=pg.mkBrush(width=5, color="w"), symbol="o")
        self.ui.graphWidget12.addItem(scatter12)
        scatter12.setData(g12)

        # Graph13: Alt-SNRWeight
        self.ui.graphWidget13.setLabel("bottom", "Alt (deg)", color="white", size=30)
        self.ui.graphWidget13.setLabel("left", "SNRWeight", color="white", size=30)
        self.ui.graphWidget13.showGrid(x=True, y=True)

        scatter13 = pg.ScatterPlotItem(brush=pg.mkBrush(width=5, color="w"), symbol="o")
        self.ui.graphWidget13.addItem(scatter13)
        scatter13.setData(g13)

        # Graph14: Az-SNRWeight
        self.ui.graphWidget14.setLabel("bottom", "Az (deg)", color="white", size=30)
        self.ui.graphWidget14.setLabel("left", "SNRWeight", color="white", size=30)
        self.ui.graphWidget14.showGrid(x=True, y=True)

        scatter14 = pg.ScatterPlotItem(brush=pg.mkBrush(width=5, color="w"), symbol="o")
        self.ui.graphWidget14.addItem(scatter14)
        scatter14.setData(g14)

        # Graph15: Time-SNRWeight
        self.ui.graphWidget15.setLabel("left", "SNRWeight", color="white", size=30)
        self.ui.graphWidget15.showGrid(x=True, y=True)

        axis15 = DateAxisItem(orientation="bottom")
        axis15.attachToPlotItem(self.ui.graphWidget15.getPlotItem())
        axis15.setLabel("Time", units="h")

        scatter15 = pg.ScatterPlotItem(brush=pg.mkBrush(width=5, color="w"), symbol="o")
        self.ui.graphWidget15.addItem(scatter15)
        scatter15.setData(g15)

        self.lrAlt.sigRegionChanged.connect(self.updatePlotAlt)
        self.ui.graphWidget4.sigXRangeChanged.connect(self.updateRegionAlt)
        self.ui.graphWidget7.sigXRangeChanged.connect(self.updateRegionAlt)
        self.ui.graphWidget10.sigXRangeChanged.connect(self.updateRegionAlt)
        self.ui.graphWidget13.sigXRangeChanged.connect(self.updateRegionAlt)

        self.lrAz.sigRegionChanged.connect(self.updatePlotAz)
        self.ui.graphWidget5.sigXRangeChanged.connect(self.updateRegionAz)
        self.ui.graphWidget8.sigXRangeChanged.connect(self.updateRegionAz)
        self.ui.graphWidget11.sigXRangeChanged.connect(self.updateRegionAz)
        self.ui.graphWidget14.sigXRangeChanged.connect(self.updateRegionAz)

        self.lrDate.sigRegionChanged.connect(self.updatePlotDate)
        self.ui.graphWidget6.sigXRangeChanged.connect(self.updateRegionDate)
        self.ui.graphWidget9.sigXRangeChanged.connect(self.updateRegionDate)
        self.ui.graphWidget12.sigXRangeChanged.connect(self.updateRegionDate)
        self.ui.graphWidget15.sigXRangeChanged.connect(self.updateRegionDate)

    def updatePlotAlt(self):
        self.ui.graphWidget4.setXRange(*self.lrAlt.getRegion(), padding=0)
        self.ui.graphWidget7.setXRange(*self.lrAlt.getRegion(), padding=0)
        self.ui.graphWidget10.setXRange(*self.lrAlt.getRegion(), padding=0)
        self.ui.graphWidget13.setXRange(*self.lrAlt.getRegion(), padding=0)

    def updateRegionAlt(self, region):
        self.lrAlt.setRegion(self.ui.graphWidget4.getViewBox().viewRange()[0])

    def updatePlotAz(self):
        self.ui.graphWidget5.setXRange(*self.lrAz.getRegion(), padding=0)
        self.ui.graphWidget8.setXRange(*self.lrAz.getRegion(), padding=0)
        self.ui.graphWidget11.setXRange(*self.lrAz.getRegion(), padding=0)
        self.ui.graphWidget14.setXRange(*self.lrAz.getRegion(), padding=0)

    def updateRegionAz(self, region):
        self.lrAz.setRegion(self.ui.graphWidget5.getViewBox().viewRange()[0])

    def updatePlotDate(self):
        self.ui.graphWidget6.setXRange(*self.lrDate.getRegion(), padding=0)
        self.ui.graphWidget9.setXRange(*self.lrDate.getRegion(), padding=0)
        self.ui.graphWidget12.setXRange(*self.lrDate.getRegion(), padding=0)
        self.ui.graphWidget15.setXRange(*self.lrDate.getRegion(), padding=0)

    def updateRegionDate(self):
        self.lrDate.setRegion(self.ui.graphWidget6.getViewBox().viewRange()[0])
