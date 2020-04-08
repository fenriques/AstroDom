import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc

import csv


class ImportTableModel(qtc.QAbstractTableModel):

    def __init__(self, data, headers):
        super().__init__()
        self._data = data
        self._headers = headers

    def rowCount(self, parent):
        return len(self._data)

    def columnCount(self, parent):
        return len(self._headers)

    def data(self, index, role):
        # original if statement:
        # if role == qtc.Qt.DisplayRole:
        # Add EditRole so that the cell is not cleared when editing
        if role in (qtc.Qt.DisplayRole, qtc.Qt.EditRole):
            return self._data[index.row()][index.column()]

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
        self.beginInsertRows(
            parent or qtc.QModelIndex(),
            position,
            position + rows - 1
        )

        for i in range(rows):
            default_row = [''] * len(self._headers)
            self._data.insert(position, default_row)
        self.endInsertRows()

    def removeRows(self, position, rows, parent):
        self.beginRemoveRows(
            parent or qtc.QModelIndex(),
            position,
            position + rows - 1
        )
        for i in range(rows):
            del(self._data[position])
        self.endRemoveRows()
        self.layoutChanged.emit()

    def removeColumns(self, position, cols, parent):
        self.beginRemoveColumns(
            parent or qtc.QModelIndex(),
            position,
            position + cols - 1
        )
        for i in range(cols):
            del(self._data[position])
        self.endRemoveColumns()

    # method for saving
    def save_data(self):
        with open(self.filename, 'w', encoding='utf-8') as fh:
            writer = csv.writer(fh)
            writer.writerow(self._headers)
            writer.writerows(self._data)
