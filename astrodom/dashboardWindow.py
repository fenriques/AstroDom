import sys
import logging
import time

from .gui.dashBoardWindowGui import *
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5.QtGui import *
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
        self.show()
      
        rowCount = self.imageListModel.rowCount()
        field = self.app.filterDictToList("order","keys")
        eNew=[]
        
        for i in range(rowCount):
            target = self.imageListModel.data(self.imageListModel.index(i, field.index("target")))
            filter = self.imageListModel.data(self.imageListModel.index(i, field.index("filter")))
            exposure = self.imageListModel.data(self.imageListModel.index(i, field.index("exposure")))

            checkAppend = False
            if len(eNew) ==0:
                eNew.append([target , filter, 1,  exposure])
                checkAppend = True
                                
            for k,v in enumerate(eNew):
                if checkAppend == False and v[0] == target and v[1] == filter:
                    countNew  = v[2] +1 
                    exposureNew =v[3] +exposure
                    eNew[k]= [ target ,filter, countNew,  exposureNew]
                    checkAppend = True
            if checkAppend == False:
                eNew.append( [target , filter, 1, exposure])

        headers=["Target", "Filter", "Count", "Tot Exposure"]

        self.model = DashboardModel(eNew,headers)
        self.ui.tableViewDashboard.setModel(self.model)
        self.ui.tableViewDashboard.setWordWrap(False)
        self.ui.tableViewDashboard.verticalHeader().hide()
        self.ui.tableViewDashboard.setSortingEnabled(False)
        self.ui.tableViewDashboard.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.ui.tableViewDashboard.setAlternatingRowColors(False)
        self.ui.tableViewDashboard.setTextElideMode(QtCore.Qt.ElideLeft)
        timeDelegate = TimeDelegate(self.ui.tableViewDashboard)        
        self.ui.tableViewDashboard.setItemDelegateForColumn(3, timeDelegate)
 


"""
Generic class that extends QAbstractTableModel.
"""


class DashboardModel(qtc.QAbstractTableModel):
    logger = logging.getLogger(__name__)

    def __init__(self, data, headers):
        super().__init__()
        self._data = data
        self._headers = headers
        print(data)
    def rowCount(self, parent):
        return len(self._data)

    def columnCount(self, parent):
        return len(self._headers)

    def data(self, index, role):
        data = self._data[index.row()][index.column()]

        if role in (qtc.Qt.DisplayRole, qtc.Qt.EditRole):
            return data
        if role == qtc.Qt.BackgroundRole and (
            data == "Error: FITS file already exists in database"
            or data == "File not found"
            or data == ""
        ):
            return QBrush(qtc.Qt.darkRed)
        if role == qtc.Qt.BackgroundRole and (
            data == "OK: FITS file saved"
            or data == "OK: FITS file updated"
            or data == "File found"
        ):
            return QBrush(qtc.Qt.darkGreen)

    # Additional features methods:
    def headerData(self, section, orientation, role):

        if orientation == qtc.Qt.Horizontal and role == qtc.Qt.DisplayRole:
            return self._headers[section]
        else:
            return super().headerData(section, orientation, role)

    def sort(self, column, order):
        self.layoutAboutToBeChanged.emit()  # needs to be emitted before a sort
        self._data.sort(key=lambda x: x[column])
        if order == qtc.Qt.DescendingOrder:
            self._data.reverse()
        self.layoutChanged.emit()  # needs to be emitted after a sort

    # Methods for Read/Write

    def flags(self, index):
        return super().flags(index) | qtc.Qt.ItemIsEditable

    def setData(self, index, value, role):
        if index.isValid() and role == qtc.Qt.EditRole:
            self._data[index.row()][index.column()] = value
            self.dataChanged.emit(index, index, [role])
            return True
        else:
            return False

class TimeDelegate(QtWidgets.QStyledItemDelegate):
    def displayText(self, value, locale):
        value = time.strftime('%H:%M:%S',  time.gmtime(value))
        return super(TimeDelegate, self).displayText(value, locale)