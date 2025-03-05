# -----------------------------------------------------------
# AstrDom:
#
# (C) 2020 Ferrante Enriques, ferrante.enriques@gmail.com
# Released under GNU Public License (GPL)
# -----------------------------------------------------------

import ntpath

from astropy import units as u
from astropy.coordinates import Angle, Longitude, Latitude

from datetime import datetime
from PyQt6 import QtCore, QtGui
from PyQt6 import QtWidgets

from PyQt6.QtGui import QColor
from astrodom.settings import *
from astrodom.loadSettings import *  


#from dateutil.relativedelta import relativedelta

"""
The table view containing the image list. It reads
the database and set it as a source model. Then
the model's view is handled through a proxy model.
So main objects in this class are:
- The source model:  imageSourceModel (SqlTableModel)
- The proxy model: imageListModel (instance of SortFilterProxyModel)
- The table view: tableViewImages
Keep in mind that some methods are defined in the parent
MainW class
"""
# Here  all delegate classes for column formatting

class FileDelegate(QtWidgets.QStyledItemDelegate):

    def displayText(self, value, locale):
        self.value = ntpath.basename(value)
        return super(FileDelegate, self).displayText(self.value, locale)


class FilterDelegate(QtWidgets.QStyledItemDelegate):
    def displayText(self, value, locale):
        self.value = value
        return super(FilterDelegate, self).displayText(self.value, locale)


    def initStyleOption(self, option, index):
        super(FilterDelegate, self).initStyleOption(option, index)
        if self.value in ["Luminance", "luminance", "Lum", "lum", "L", "l"]:
            option.backgroundBrush = QtGui.QBrush(
                QColor(244, 244, 244, 35))
        elif self.value in ["Red", "R", "r", "red"]:
            option.backgroundBrush = QtGui.QBrush(QColor(255, 0, 0, 35))
        elif self.value in ["Blue", "B", "b", "blue"]:
            option.backgroundBrush = QtGui.QBrush(QColor(55, 55, 255, 35))
        elif self.value in ["Green", "G", "g", "green"]:
            option.backgroundBrush = QtGui.QBrush(QColor(0, 140, 55, 35))
        elif self.value in ["Ha", "ha", "Halpha", "halpha", "H_alpha", "h_alpha", "H_Alpha", "h_Alpha"]:
            option.backgroundBrush = QtGui.QBrush(QColor(190, 255, 0, 35))
        elif self.value in ["OIII", "Oiii", "oiii", "O3"]:
            option.backgroundBrush = QtGui.QBrush(
                QColor(150, 200, 255, 35))
        elif self.value in ["SII", "Sii", "sii"]:
            option.backgroundBrush = QtGui.QBrush(
                    QColor(255, 120, 190, 35))
    

class FrameDelegate(QtWidgets.QStyledItemDelegate):
    def displayText(self, value, locale):
        self.value = value
        return super(FrameDelegate, self).displayText(self.value, locale)

    def initStyleOption(self, option, index):
        super(FrameDelegate, self).initStyleOption(option, index)
        if self.value in ["Light", "LIGHT", "Light Frame"]:
            option.backgroundBrush = QtGui.QBrush(
                QColor(120, 120, 244, 55))
        elif self.value in ["Dark", "Dark Frame"]:
            option.backgroundBrush = QtGui.QBrush(QColor(80, 80, 80, 55))
        elif self.value in ["Flat", "Flat Frame"]:
            option.backgroundBrush = QtGui.QBrush(QColor(80, 80,  160, 55))
        elif self.value in ["DarkFlat", "Dark Flat"]:
            option.backgroundBrush = QtGui.QBrush(
                QColor(80, 80, 80, 55))
        elif self.value in  ["Bias", "Bias Frame"]:
            option.backgroundBrush = QtGui.QBrush(
                QColor(55, 55, 55, 55))

class FWHMDelegate(QtWidgets.QStyledItemDelegate):

    def displayText(self, value, locale):
        self.value = value
        try:
            self.value = f"{float(value):.2f}"
        except ValueError:
            pass
        return super(FWHMDelegate, self).displayText(self.value, locale)

    def initStyleOption(self, option, index):
        super(FWHMDelegate, self).initStyleOption(option, index)
        if self.value and float(self.value) > self.limit:
            option.palette.setColor(QtGui.QPalette.ColorRole.Text, QtGui.QColor("red"))

    def setLimit(self, limit):
        self.limit = limit

class EccentricityDelegate(QtWidgets.QStyledItemDelegate):

    def displayText(self, value, locale):
        self.value = value
        try:
            self.value = f"{float(value):.2f}"
        except ValueError:
            pass
        return super(EccentricityDelegate, self).displayText(self.value, locale)

    def initStyleOption(self, option, index):
        super(EccentricityDelegate, self).initStyleOption(option, index)
        if self.value and float(self.value) > self.limit:
            option.palette.setColor(QtGui.QPalette.ColorRole.Text, QtGui.QColor("red"))

    def setLimit(self, limit):
        self.limit = limit

class SNRDelegate(QtWidgets.QStyledItemDelegate):

    def displayText(self, value, locale):
        self.value = value
        try:
            self.value = f"{float(value):.2f}"
        except ValueError:
            pass
        return super(SNRDelegate, self).displayText(self.value, locale)

    def initStyleOption(self, option, index):
        super(SNRDelegate, self).initStyleOption(option, index)
        if self.value and float(self.value) < self.limit:
            option.palette.setColor(QtGui.QPalette.ColorRole.Text, QtGui.QColor("red"))

    def setLimit(self, limit):
        self.limit = limit

class AltDelegate(QtWidgets.QStyledItemDelegate):

    def displayText(self, value, locale):
        self.value = value
        if value == "":
            return super(AltDelegate, self).displayText(value, locale)
        a = Angle(value, u.deg)
        value = str(a.to_string(unit=u.degree,
                                precision=0, sep=("°", "'", "''")))
        return super(AltDelegate, self).displayText(value, locale)
    
    def initStyleOption(self, option, index):
        super(AltDelegate, self).initStyleOption(option, index)
        if self.value and float(self.value) < self.limit:
            option.palette.setColor(QtGui.QPalette.ColorRole.Text, QtGui.QColor("red"))

    def setLimit(self, limit):
        self.limit = limit

                  
class RoundDelegate(QtWidgets.QStyledItemDelegate):
    def displayText(self, value, locale):
        self.value = value
        try:
            self.value = f"{float(value):.2f}"
        except ValueError:
            pass
        return super(RoundDelegate, self).displayText(self.value, locale)

class DateDelegate(QtWidgets.QStyledItemDelegate):
    def displayText(self, value, locale):
        if value == "":
            return super(DateDelegate, self).displayText(value, locale)
        try:
            value = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S").strftime(DATE_FORMAT)
        except ValueError:
            value = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f").strftime(DATE_FORMAT)

        return super(DateDelegate, self).displayText(value, locale)

class TimeDelegate(QtWidgets.QStyledItemDelegate):
    def displayText(self, value, locale):
        if value == "":
            return super(TimeDelegate, self).displayText(value, locale)
        try:
            value = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S").strftime("%H:%M:%S")
        except ValueError:
            value = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f").strftime("%H:%M:%S")

        return super(TimeDelegate, self).displayText(value, locale)


class HmsDelegate(QtWidgets.QStyledItemDelegate):
    def displayText(self, value, locale):
        if value == "": return 
        a = Angle(value, u.deg)
        value = str(a.to_string(unit=u.hour, precision=0, sep=("h", "m", "s")))
        return super(HmsDelegate, self).displayText(value, locale)

    def initStyleOption(self, option, index):
        super(HmsDelegate, self).initStyleOption(option, index)
        option.displayAlignment = QtCore.Qt.AlignmentFlag.AlignRight

class DmsDelegate(QtWidgets.QStyledItemDelegate):
    def displayText(self, value, locale):
        if value == "": return 
        a = Angle(value, u.deg)
        value = str(a.to_string(unit=u.degree,
                                precision=0, sep=("°", "'", "''")))
        return super(DmsDelegate, self).displayText(value, locale)

    def initStyleOption(self, option, index):
        super(DmsDelegate, self).initStyleOption(option, index)
        option.displayAlignment = QtCore.Qt.AlignmentFlag.AlignRight


class LongDelegate(QtWidgets.QStyledItemDelegate):
    def displayText(self, value, locale):
        if value == "": return 
        a = Longitude(value, u.deg)
        a.wrap_angle = 180 * u.deg
        value = str(a.to_string(unit=u.degree,
                                precision=0, sep=("°", "'", "''")))
        return super(LongDelegate, self).displayText(value, locale)

    def initStyleOption(self, option, index):
        super(LongDelegate, self).initStyleOption(option, index)
        option.displayAlignment = QtCore.Qt.AlignmentFlag.AlignRight


class LatDelegate(QtWidgets.QStyledItemDelegate):
    def displayText(self, value, locale):
        if value == "": return 
        a = Latitude(value, u.deg)
        a.wrap_angle = 90 * u.deg
        value = str(a.to_string(unit=u.degree,
                                precision=0, sep=("°", "'", "''")))
        return super(LatDelegate, self).displayText(value, locale)

    def initStyleOption(self, option, index):
        super(LatDelegate, self).initStyleOption(option, index)
        option.displayAlignment = QtCore.Qt.AlignmentFlag.AlignRight
