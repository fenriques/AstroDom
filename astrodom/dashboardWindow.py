import sys
import logging
import time

from .gui.dashBoardWindowGui import *
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5.QtGui import *
import pandas as pd
import numpy as np
"""
"""


class DashboardWindow(QDialog):
    logger = logging.getLogger(__name__)

    def __init__(self, app, imageListModel):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.app = app
        self.setWindowTitle("Dashboard")
        self.imageListModel = imageListModel
        # Load windows position and size
        try:
            self.resize(self.app.settings.value("sizeDashboardW"))
            self.move(self.app.settings.value("posDashboardW"))
        except Exception as e:
            self.logger.error(f"{e}")
        self.show()

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
        df = pd.DataFrame(plist, columns=headers)
        df = df[["target", "filter", "exposure"]]
        df = df.sort_values(by=['target'])
        tableCount = pd.pivot_table(df,
                                    values='exposure',
                                    index=['target'],
                                    columns='filter',
                                    aggfunc=[lambda x: x.count()],
                                    fill_value="",
                                    margins=True, margins_name='Total')
        tableCount.columns = [f'{j}' for i, j in tableCount.columns]
        tableCount.reset_index(level=0, inplace=True)

        tableTime = pd.pivot_table(df,
                                   values='exposure',
                                   index=['target'],
                                   columns='filter',
                                   aggfunc=[np.sum],
                                   fill_value="",
                                   margins=True, margins_name='Total')
        tableTime.columns = [f'{j}' for i, j in tableTime.columns]
        tableTime.reset_index(level=0, inplace=True)
        self.modelCount = DashboardModel(self.app, tableCount)

        self.ui.tableViewDashboardCount.setModel(self.modelCount)
        self.ui.tableViewDashboardCount.setWordWrap(False)
        self.ui.tableViewDashboardCount.horizontalHeader().setResizeMode(QHeaderView.Stretch)

        self.ui.tableViewDashboardCount.verticalHeader().hide()
        self.ui.tableViewDashboardCount.setSortingEnabled(False)
        self.ui.tableViewDashboardCount.sortByColumn(0, qtc.Qt.AscendingOrder)
        self.ui.tableViewDashboardCount.setAlternatingRowColors(True)
        self.ui.tableViewDashboardCount.setTextElideMode(qtc.Qt.ElideLeft)
        roundDelegate = RoundDelegate(self.ui.tableViewDashboardCount)
        for i in range(tableCount.shape[1]):
            if i > 0:
                self.ui.tableViewDashboardCount.setItemDelegateForColumn(
                    i, roundDelegate)

        self.modelTime = DashboardModel(self.app, tableTime)
        self.ui.tableViewDashboardTime.setModel(self.modelTime)
        self.ui.tableViewDashboardTime.setWordWrap(False)
        self.ui.tableViewDashboardTime.horizontalHeader().setResizeMode(QHeaderView.Stretch)
        self.ui.tableViewDashboardTime.verticalHeader().hide()
        self.ui.tableViewDashboardTime.setSortingEnabled(False)
        self.ui.tableViewDashboardTime.sortByColumn(0, qtc.Qt.AscendingOrder)
        self.ui.tableViewDashboardTime.setAlternatingRowColors(True)
        self.ui.tableViewDashboardTime.setTextElideMode(qtc.Qt.ElideLeft)
        timeDelegate = TimeDelegate(self.ui.tableViewDashboardTime)
        for i in range(tableTime.shape[1]):
            if i > 0:
                self.ui.tableViewDashboardTime.setItemDelegateForColumn(
                    i, timeDelegate)

    def closeEvent(self, event):
        self.app.settings.setValue("sizeDashboardW", self.size())
        self.app.settings.setValue("posDashboardW", self.pos())
        self.close()
        event.accept()


"""
Generic class that extends QAbstractTableModel.
"""


class DashboardModel(qtc.QAbstractTableModel):

    def __init__(self, app, data):
        super(DashboardModel, self).__init__()
        self._data = data
        self.app = app

    def data(self, index, role):
        value = self._data.iloc[index.row(), index.column()]
        if role == qtc.Qt.DisplayRole:
            return str(value)
        if role == qtc.Qt.FontRole and index.column() == 0 and value != "":
            font = QFont()
            font.setBold(True)
            return font

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == qtc.Qt.DisplayRole:
            if orientation == qtc.Qt.Horizontal:
                return str(self._data.columns[section])

            if orientation == qtc.Qt.Vertical:
                return str(self._data.index[section])

        if role == qtc.Qt.FontRole:
            font = QFont()
            font.setBold(True)
            return font

        try:
            value = str(self._data.columns[section])
            if role == qtc.Qt.ForegroundRole:
                if value in self.app.confFilters["L"]:
                    return QBrush(QColor(44, 44, 44, 255))
                elif value in self.app.confFilters["R"]:
                    return QBrush(QColor(44, 44, 44, 255))
                elif value in self.app.confFilters["B"]:
                    return QBrush(QColor(44, 44, 44, 255))
                elif value in self.app.confFilters["G"]:
                    return QBrush(QColor(44, 44, 44, 255))
                elif value in self.app.confFilters["Ha"]:
                    return QBrush(QColor(44, 44, 44, 255))
                elif value in self.app.confFilters["Oiii"]:
                    return QBrush(QColor(44, 44, 44, 255))
                elif value in self.app.confFilters["Sii"]:
                    return QBrush(QColor(44, 44, 44, 255))

            if role == qtc.Qt.BackgroundRole:
                if value in self.app.confFilters["L"]:
                    return QBrush(QColor(244, 244, 244, 60))
                elif value in self.app.confFilters["R"]:
                    return QBrush(QColor(255, 0, 0, 60))
                elif value in self.app.confFilters["B"]:
                    return QBrush(QColor(55, 55, 255, 60))
                elif value in self.app.confFilters["G"]:
                    return QBrush(QColor(0, 140, 55, 60))
                elif value in self.app.confFilters["Ha"]:
                    return QBrush(QColor(190, 255, 0, 60))
                elif value in self.app.confFilters["Oiii"]:
                    return QBrush(QColor(150, 200, 255, 60))
                elif value in self.app.confFilters["Sii"]:
                    return QBrush(QColor(255, 120, 190, 60))

        except Exception as e:
            pass


class TimeDelegate(QtWidgets.QStyledItemDelegate):
    def displayText(self, value, locale):
        try:
            value = time.strftime("%H:%M:%S", time.gmtime(float(value)))
        except Exception as e:
            value = ""
        return super(TimeDelegate, self).displayText(value, locale)


class RoundDelegate(QtWidgets.QStyledItemDelegate):
    def displayText(self, value, locale):
        try:
            value = round(float(value), 0)
        except Exception as e:
            value = ""
        return super(RoundDelegate, self).displayText(value, locale)
