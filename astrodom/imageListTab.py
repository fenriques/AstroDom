# -----------------------------------------------------------
# AstrDom:
#
# (C) 2020 Ferrante Enriques, ferrante.enriques@gmail.com
# Released under GNU Public License (GPL)
# -----------------------------------------------------------

import sys
import os
import ntpath
import logging

from astropy import units as u
from astropy.coordinates import Angle, Longitude, Latitude

from datetime import datetime
from PyQt5 import QtSql
from PyQt5 import QtCore, QtGui
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QByteArray

from dateutil.relativedelta import relativedelta

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


class ImageListTab:

    logger = logging.getLogger(__name__)

    def __init__(self, mainW, app):
        super().__init__()
        self.mainW = mainW
        self.app = app

        self.displayImageList()

    def displayImageList(self):

        # Table Source model
        self.mainW.imageSourceModel = QtSql.QSqlTableModel()
        self.mainW.imageSourceModel.setTable("images")
        self.mainW.imageSourceModel.setSort(3, QtCore.Qt.DescendingOrder)

        self.mainW.imageSourceModel.select()
        while self.mainW.imageSourceModel.canFetchMore():
            self.mainW.imageSourceModel.fetchMore()

        # Proxy model used for filtering and sorting.
        self.mainW.imageListModel.setDynamicSortFilter(True)
        self.mainW.imageListModel.setSourceModel(self.mainW.imageSourceModel)

        for i, label in enumerate(self.app.filterDictToList("description")):
            self.mainW.imageListModel.setHeaderData(i, QtCore.Qt.Horizontal, label)

        #restore the header state only if it is allowed
        if self.app.settings.value("readStateOnStart") == "True":
            try:
                rs = QByteArray.fromHex(bytes(self.app.settings.value("imageListState"), 'ascii'))
                self.mainW.ui.tableViewImages.horizontalHeader().restoreState(rs)
            except Exception as e:
                self.logger.error(f"Could not restore table header state {e}")
        else:
            self.app.settings.setValue("readStateOnStart","True")
         
        self.mainW.ui.tableViewImages.setWordWrap(False)
        self.mainW.ui.tableViewImages.verticalHeader().hide()
        self.mainW.ui.tableViewImages.setSortingEnabled(True)
        self.mainW.ui.tableViewImages.setAlternatingRowColors(True)
        self.mainW.ui.tableViewImages.setModel(self.mainW.imageListModel)
        self.mainW.ui.tableViewImages.setTextElideMode(QtCore.Qt.ElideLeft)
        self.mainW.ui.tableViewImages.setEditTriggers(
            QtGui.QAbstractItemView.NoEditTriggers
        )

        fd = FileDelegate(self.mainW.ui.tableViewImages)
        self.mainW.ui.tableViewImages.setItemDelegateForColumn(1, fd)
        dd = DateDelegate(self.mainW.ui.tableViewImages)
        self.mainW.ui.tableViewImages.setItemDelegateForColumn(16, dd)
        rd = RoundDelegate(self.mainW.ui.tableViewImages)
        rd.getPrecision(self.app.config["precision"])
        #Site Long and Site Lat have dms representation
        latd = LatDelegate(self.mainW.ui.tableViewImages)        
        longd = LongDelegate(self.mainW.ui.tableViewImages)        
        self.mainW.ui.tableViewImages.setItemDelegateForColumn(10, latd)
        self.mainW.ui.tableViewImages.setItemDelegateForColumn(11, longd)
        
        #RA has hms representation
        rad = HmsDelegate(self.mainW.ui.tableViewImages)
        self.mainW.ui.tableViewImages.setItemDelegateForColumn(12, rad)
        #DEC, ALT, AZ  have dms reprentation
        dad = DmsDelegate(self.mainW.ui.tableViewImages)        
        self.mainW.ui.tableViewImages.setItemDelegateForColumn(13, dad)
        self.mainW.ui.tableViewImages.setItemDelegateForColumn(14, dad)
        self.mainW.ui.tableViewImages.setItemDelegateForColumn(15, dad)
        
        self.mainW.ui.tableViewImages.setItemDelegateForColumn(25, rd)
        self.mainW.ui.tableViewImages.setItemDelegateForColumn(26, rd)
        self.mainW.ui.tableViewImages.setItemDelegateForColumn(27, rd)
        self.mainW.ui.tableViewImages.setItemDelegateForColumn(28, rd)
        
        
        hideColList = self.app.filterDictToList("hide", "hide")
        for col, val in enumerate(hideColList):
            if val > 0:
                self.mainW.ui.tableViewImages.hideColumn(col)
 
        
    def deleteRows(self):
        indexes = self.mainW.ui.tableViewImages.selectedIndexes()

        if indexes:
            ret = QMessageBox.question(None,
                    "Delete rows", 
                    "Are you sure to delete selected rows?", 
                    QMessageBox.Yes | QMessageBox.No
                )

            if ret == QMessageBox.Yes:
                self.mainW.imageListModel.removeSelectedRows(indexes, 1, None)
                # Force image list reload data
                self.mainW.imageSourceModel.select()
                while self.mainW.imageSourceModel.canFetchMore():
                    self.mainW.imageSourceModel.fetchMore()
                self.mainW.filterRegExpChanged()
            
class FileDelegate(QtWidgets.QStyledItemDelegate):
    def displayText(self, value, locale):
        value = ntpath.basename(value)
        return super(FileDelegate, self).displayText(value, locale)


class RoundDelegate(QtWidgets.QStyledItemDelegate):
    def displayText(self, value, locale):
        value = round(float(value), self.precision)
        return super(RoundDelegate, self).displayText(value, locale)
    def getPrecision(self, precision):
        self.precision = precision

class DateDelegate(QtWidgets.QStyledItemDelegate):
    def displayText(self, value, locale):
        utcDate = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
        value = utcDate.strftime("%Y-%m-%d  %H:%M:%S")
        return super(DateDelegate, self).displayText(value, locale)

class HmsDelegate(QtWidgets.QStyledItemDelegate):
    def displayText(self, value, locale):
        a = Angle(value, u.deg)
        value = str(a.to_string(unit=u.hour, precision=0, sep=("h", "m", "s")))
        return super(HmsDelegate, self).displayText(value, locale)
    def initStyleOption(self, option, index):
        super(HmsDelegate, self).initStyleOption(option, index)
        option.displayAlignment = QtCore.Qt.AlignRight

class DmsDelegate(QtWidgets.QStyledItemDelegate):
    def displayText(self, value, locale):
        a = Angle(value, u.deg)
        value = str(a.to_string(unit=u.degree,precision=0, sep=("°", "'" ,"''" )))
        return super(DmsDelegate, self).displayText(value, locale)
    def initStyleOption(self, option, index):
        super(DmsDelegate, self).initStyleOption(option, index)
        option.displayAlignment = QtCore.Qt.AlignRight

class LongDelegate(QtWidgets.QStyledItemDelegate):
    def displayText(self, value, locale):
        a = Longitude(value, u.deg)
        a.wrap_angle = 180 * u.deg
        value = str(a.to_string(unit=u.degree, precision=0, sep=("°", "'" ,"''" )))
        return super(LongDelegate, self).displayText(value, locale)
    def initStyleOption(self, option, index):
        super(LongDelegate, self).initStyleOption(option, index)
        option.displayAlignment = QtCore.Qt.AlignRight

class LatDelegate(QtWidgets.QStyledItemDelegate):
    def displayText(self, value, locale):
        a = Latitude(value, u.deg)
        a.wrap_angle = 90 * u.deg
        value = str(a.to_string(unit=u.degree,precision=0, sep=("°", "'" ,"''" )))
        return super(LatDelegate, self).displayText(value, locale)
    def initStyleOption(self, option, index):
        super(LatDelegate, self).initStyleOption(option, index)
        option.displayAlignment = QtCore.Qt.AlignRight
        
