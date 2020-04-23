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

from datetime import datetime
from PyQt5 import QtSql
from PyQt5 import QtCore, QtGui
from PyQt5 import QtWidgets

from dateutil.relativedelta import relativedelta

# local imports


class ImageListTab():

    logger = logging.getLogger(__name__)

    def __init__(self, mainW, app):
        super().__init__()
        self.mainW = mainW
        self.app = app

        self.displayImageList()

    def displayImageList(self):

        # Table Source model
        self.mainW.imageSourceModel = QtSql.QSqlTableModel()
        self.mainW.imageSourceModel.setTable('images')
        self.mainW.imageSourceModel.setSort(3, QtCore.Qt.DescendingOrder)

        self.mainW.imageSourceModel.select()
        while (self.mainW.imageSourceModel.canFetchMore()):
            self.mainW.imageSourceModel.fetchMore()
        self.logger.info("set source")
        # Proxy model used for filtering and sorting.
        self.mainW.imageListModel.setDynamicSortFilter(True)
        self.mainW.imageListModel.setSourceModel(self.mainW.imageSourceModel)

        for i, label in enumerate(self.app.filterDictToList('description')):
            self.mainW.imageListModel.setHeaderData(
                i, QtCore.Qt.Horizontal, label)

        self.mainW.ui.tableViewImages.horizontalHeader().setStretchLastSection(True)
        self.mainW.ui.tableViewImages.setWordWrap(False)
        self.mainW.ui.tableViewImages.verticalHeader().hide()
        self.mainW.ui.tableViewImages.setSortingEnabled(True)
        self.mainW.ui.tableViewImages.setAlternatingRowColors(True)
        self.mainW.ui.tableViewImages.setModel(self.mainW.imageListModel)
        self.mainW.ui.tableViewImages.setTextElideMode(QtCore.Qt.ElideLeft)
        self.mainW.ui.tableViewImages.setEditTriggers(
            QtGui.QAbstractItemView.NoEditTriggers)

        fd = FileDelegate(self.mainW.ui.tableViewImages)
        self.mainW.ui.tableViewImages.setItemDelegateForColumn(1, fd)
        dd = DateDelegate(self.mainW.ui.tableViewImages)
        self.mainW.ui.tableViewImages.setItemDelegateForColumn(16, dd)
        rd = RoundDelegate(self.mainW.ui.tableViewImages)

        self.mainW.ui.tableViewImages.setItemDelegateForColumn(12, rd)
        self.mainW.ui.tableViewImages.setItemDelegateForColumn(13, rd)
        self.mainW.ui.tableViewImages.setItemDelegateForColumn(14, rd)
        self.mainW.ui.tableViewImages.setItemDelegateForColumn(15, rd)
        self.mainW.ui.tableViewImages.setItemDelegateForColumn(25, rd)
        self.mainW.ui.tableViewImages.setItemDelegateForColumn(26, rd)
        self.mainW.ui.tableViewImages.setItemDelegateForColumn(27, rd)
        self.mainW.ui.tableViewImages.setItemDelegateForColumn(28, rd)

        self.mainW.ui.tableViewImages.hideColumn(0)  # Hide ID
        self.mainW.ui.tableViewImages.hideColumn(2)  # Hide HASH
        self.mainW.ui.tableViewImages.hideColumn(9)  # Hide Bin Y
        self.mainW.ui.tableViewImages.hideColumn(10)  # Hide Site position
        self.mainW.ui.tableViewImages.hideColumn(11)  # Hide Site position
        self.mainW.ui.tableViewImages.hideColumn(19)
        self.mainW.ui.tableViewImages.hideColumn(20)
        self.mainW.ui.tableViewImages.hideColumn(21)
        self.mainW.ui.tableViewImages.hideColumn(22)
        self.mainW.ui.tableViewImages.hideColumn(23)
        self.mainW.ui.tableViewImages.hideColumn(24)


class FileDelegate(QtWidgets.QStyledItemDelegate):
    def displayText(self, value, locale):
        value = ntpath.basename(value)
        return super(FileDelegate, self).displayText(value, locale)


class RoundDelegate(QtWidgets.QStyledItemDelegate):
    def displayText(self, value, locale):
        value = round(float(value), 2)
        return super(RoundDelegate, self).displayText(value, locale)


class DateDelegate(QtWidgets.QStyledItemDelegate):
    def displayText(self, value, locale):
        utcDate = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%f')
        value = utcDate.strftime("%Y-%m-%d  %H:%M:%S")
        return super(DateDelegate, self).displayText(value, locale)
