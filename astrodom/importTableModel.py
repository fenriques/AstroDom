import sys
import logging
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5.QtGui import *

import csv

"""
Generic class that extends QAbstractTableModel.
Used in importTab to show and manage data read
from FITS or CSV files.
"""


class ImportTableModel(qtc.QAbstractTableModel):
    logger = logging.getLogger(__name__)

    def __init__(self, data, headers):
        super().__init__()
        self._data = data
        self._headers = headers

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

    # Methods for inserting or deleting

    def insertRows(self, position, rows, parent):
        self.beginInsertRows(parent or qtc.QModelIndex(), position, position + rows - 1)

        for i in range(rows):
            default_row = [""] * len(self._headers)
            self._data.insert(position, default_row)
        self.endInsertRows()

    def removeRows(self, position, rows, parent):
        self.beginRemoveRows(parent or qtc.QModelIndex(), position, position + rows - 1)
        for i in range(rows):
            del self._data[position]
        self.endRemoveRows()
        self.layoutChanged.emit()

    # method for saving
    def save_data(self):
        with open(self.filename, "w", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(self._headers)
            writer.writerows(self._data)
