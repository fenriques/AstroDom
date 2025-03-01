import os
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTableView, QHeaderView
from PyQt6.QtCore import QAbstractTableModel, Qt
from astropy.io import fits

class FitsHeaderModel(QAbstractTableModel):
    def __init__(self, header, parent=None):
        super(FitsHeaderModel, self).__init__(parent)
        self.header = header
        self.keys = list(header.keys())
        self.values = list(header.values())

    def rowCount(self, parent=None):
        return len(self.keys)

    def columnCount(self, parent=None):
        return 2

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole:
            return None
        if index.column() == 0:
            return self.keys[index.row()]
        elif index.column() == 1:
            return self.values[index.row()]

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            if section == 0:
                return "Keyword"
            elif section == 1:
                return "Value"
        return None

class FitsHeaderDialog(QDialog):
    def __init__(self, parent = None, fits_path = None):
        super().__init__(parent)
        file_name = os.path.basename(fits_path)

        self.setWindowTitle("FITS Header  -  " + file_name)
        self.setGeometry(100, 100, 400, 800)

        layout = QVBoxLayout(self)
        self.tableView = QTableView(self)
        layout.addWidget(self.tableView)

        self.loadFitsHeader(fits_path)

    def loadFitsHeader(self, fits_path):
        with fits.open(fits_path) as hdul:
            header = hdul[0].header
            model = FitsHeaderModel(header)
            self.tableView.setModel(model)
            self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

