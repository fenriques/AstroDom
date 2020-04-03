# -----------------------------------------------------------
# pixView:
#
# (C) 2020 Ferrante Enriques, ferrante.enriques@gmail.com
# Released under GNU Public License (GPL)
# -----------------------------------------------------------

import sys
import os
import ntpath


from datetime import datetime
from PyQt5 import QtSql
from PyQt5 import QtCore
from PyQt5 import QtWidgets

from dateutil.relativedelta import relativedelta

# local imports


class ImageListTab():

    def __init__(self, mainW, app):
        super().__init__()
        self.mainW = mainW
        self.app = app

        self.displayImageList()

    def displayImageList(self):

        # Table Source model
        self.imageSourceModel = QtSql.QSqlTableModel()
        self.imageSourceModel.setTable('images')
        self.imageSourceModel.setSort(3, QtCore.Qt.DescendingOrder)

        self.imageSourceModel.select()
        self.imageSourceModel.fetchMore()

        # Proxy model used for filtering and sorting.
        self.mainW.imageListModel.setDynamicSortFilter(True)
        self.mainW.imageListModel.setSourceModel(self.imageSourceModel)

        for i, label in enumerate(self.app.filterDictToList('description')):
            self.mainW.imageListModel.setHeaderData(
                i, QtCore.Qt.Horizontal, label)

        self.mainW.ui.tableViewImages.horizontalHeader().setStretchLastSection(True)
        self.mainW.ui.tableViewImages.setWordWrap(False)
        self.mainW.ui.tableViewImages.setSortingEnabled(True)
        self.mainW.ui.tableViewImages.setAlternatingRowColors(True)
        self.mainW.ui.tableViewImages.setModel(self.mainW.imageListModel)
        self.mainW.ui.tableViewImages.setTextElideMode(QtCore.Qt.ElideLeft)
        fd = FileDelegate(self.mainW.ui.tableViewImages)
        self.mainW.ui.tableViewImages.setItemDelegateForColumn(1, fd)
        dd = DateDelegate(self.mainW.ui.tableViewImages)
        self.mainW.ui.tableViewImages.setItemDelegateForColumn(16, dd)

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
        # self.reviews.model().setFilter(f'coffee_id = {self.coffee_id}')
        # self.reviews.resizeRowsToContents()
        # self.mainW.ui.tableViewImages.resizeColumnsToContents()


class FileDelegate(QtWidgets.QStyledItemDelegate):
    def displayText(self, value, locale):
        value = ntpath.basename(value)
        return super(FileDelegate, self).displayText(value, locale)


class DateDelegate(QtWidgets.QStyledItemDelegate):
    def displayText(self, value, locale):
        utcDate = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%f')
        value = utcDate.strftime("%Y-%m-%d  %H:%M:%S")
        return super(DateDelegate, self).displayText(value, locale)
