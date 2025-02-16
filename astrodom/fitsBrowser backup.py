from PyQt6.QtWidgets import QApplication, QTreeView
from PyQt6.QtGui import QFileSystemModel
from PyQt6.QtCore import QModelIndex, Qt
from PyQt6 import QtGui
import os, sys
from astropy.io import fits
from datetime import datetime

from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QWidget
from viewDelegates import *
import sqlite3
from PyQt6.QtCore import pyqtSignal

fits_keywords = {
    "OBJECT": {'fits_key': ["OBJECT", "OBJ", "TARGET"], 'type': 'text', 'display_name': 'Target'},
    "DATE-OBS": {'fits_key': ["DATE-OBS", "DATE"], 'type': 'datetime', 'display_name': 'Date'},
    "FILTER": {'fits_key': ["FILTER"], 'type': 'filter', 'display_name': 'Filter'},
    "EXPOSURE": {'fits_key': ["EXPOSURE","EXPTIME"], 'type': 'int', 'display_name': 'Exposure'},
    "CCD-TEMP": {'fits_key': ["CCD-TEMP"], 'type': 'float', 'display_name': 'Temperature'},
    "IMAGETYP": {'fits_key': ["IMAGETYP"], 'type': 'text', 'display_name': 'Frame'},
    "XBINNING": {'fits_key': ["XBINNING"], 'type': 'int', 'display_name': 'Bin X'},
    "OBJECT-RA": {'fits_key': ["OBJCTRA"], 'type': 'text', 'display_name': 'RA'},
    "OBJECT-DEC": {'fits_key': ["OBJCTDEC"], 'type': 'text', 'display_name': 'DEC'},
    "OBJECT-ALT": {'fits_key': ["OBJCTALT"], 'type': 'text', 'display_name': 'ALT'},
    "OBJECT-AZ": {'fits_key': ["OBJCTAZ"], 'type': 'text', 'display_name': 'AZ'},
    "GAIN": {'fits_key': ["GAIN"], 'type': 'int', 'display_name': 'Gain'},
    "OFFSET": {'fits_key': ["OFFSET"], 'type': 'int', 'display_name': 'Offset'},
    "FILE": {'fits_key': "", 'type': 'text', 'display_name': 'File Name'}

}
filters = {"L": ["Luminance", "luminance", "Lum", "lum", "L", "l"], "R": ["Red", "R", "r", "red"], "B": ["Blue", "B", "b", "blue"], "G": ["Green", "G", "g", "green"], "Ha": ["Ha", "ha", "Halpha", "halpha", "H_alpha", "h_alpha", "H_Alpha", "h_Alpha"], "Sii": ["SII", "Sii", "sii"], "Oiii": ["OIII", "Oiii", "oiii", "O3"], "LPR": ["Lpr", "LPR", "lpr"]}
filters_background = {"L": ["Luminance", "luminance", "Lum", "lum", "L", "l"], "R": ["Red", "R", "r", "red"], "B": ["Blue", "B", "b", "blue"], "G": ["Green", "G", "g", "green"], "Ha": ["Ha", "ha", "Halpha", "halpha", "H_alpha", "h_alpha", "H_Alpha", "h_Alpha"], "Sii": ["SII", "Sii", "sii"], "Oiii": ["OIII", "Oiii", "oiii", "O3"], "LPR": ["Lpr", "LPR", "lpr"]}


class CustomFileSystemModel(QFileSystemModel):
    

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            if section >= super().columnCount():
                fits_key_index = section - super().columnCount()
                fits_key = list(fits_keywords.keys())[fits_key_index]
                return fits_keywords[fits_key]['display_name']
        return super().headerData(section, orientation, role)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return super().columnCount(parent) + len(fits_keywords)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and index.column() >= super().columnCount():
            file_path = self.filePath(index)
            if os.path.isfile(file_path):
                with fits.open(file_path) as hdul:
                    header = hdul[0].header
                fits_key_index = index.column() - super().columnCount()
                fits_key = list(fits_keywords.keys())[fits_key_index]
                for key in fits_keywords[fits_key]['fits_key']:
                    if key in header:
                        item_value = header[key]
                        break
                else:
                    item_value = ''
                try:
                    if fits_keywords[fits_key]['type'] == 'datetime' and item_value:
                        try:
                            item_value = datetime.strptime(item_value, '%Y-%m-%dT%H:%M:%S.%f').strftime('%d-%m-%Y %H:%M:%S')
                        except ValueError:
                            item_value = datetime.strptime(item_value, '%Y-%m-%dT%H:%M:%S').strftime('%d-%m-%Y %H:%M:%S')
                    elif fits_keywords[fits_key]['type'] == 'int' and item_value:
                        item_value = int(item_value)
                    elif fits_keywords[fits_key]['type'] == 'text' and item_value:
                        item_value = str(item_value)
                    elif fits_keywords[fits_key]['type'] == 'filter' and item_value:
                        for filter_key, filter_values in filters.items():
                            if item_value in filter_values:
                                item_value = filter_key
                except Exception as e:
                    item_value = ''
                return item_value
            else:
                return ""
            
        if role == Qt.ItemDataRole.TextAlignmentRole and index.column() in [4,6,7,8,9,10]:
            return Qt.AlignmentFlag.AlignHCenter
        
        return super().data(index, role)

import sys
import os
class FitsBrowser(QWidget):
    save_to_db_pressed = pyqtSignal()

    def __init__(self, parent=None, project_id="your_project_id", base_dir="your_base_directory"):
        super().__init__(parent)
        self.resize(800, 600)
        self.setWindowTitle("File System Model with Size Column")

        self.model = CustomFileSystemModel()

        self.project_id = project_id
        self.base_directory = base_dir
        self.model.setRootPath(self.base_directory)
        
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(self.base_directory))
        
        self.model.setNameFilters(["*.FIT", "*.fit", "*.FITS", "*.fits"])
        self.model.setNameFilterDisables(False)
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(self.base_directory))
        self.tree.setSortingEnabled(True)
        self.tree.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.tree.setAlternatingRowColors(True)
        self.tree.setColumnHidden(2, True)
        self.tree.setColumnHidden(3, True)
        self.tree.setColumnWidth(0, 350)
        self.tree.setColumnWidth(4, 150)
        self.tree.setColumnWidth(5, 150)

        self.filterDelegate = FilterDelegate(self.tree)
        self.tree.setItemDelegateForColumn(6, self.filterDelegate)
        self.frameDelegate = FrameDelegate(self.tree)
        self.tree.setItemDelegateForColumn(9, self.frameDelegate)
        self.raDelegate = HmsDelegate(self.tree)
        self.tree.setItemDelegateForColumn(11, self.raDelegate)
        self.decDelegate = DmsDelegate(self.tree)
        self.tree.setItemDelegateForColumn(12, self.decDelegate)
        self.altDelegate = DmsDelegate(self.tree)
        self.tree.setItemDelegateForColumn(13, self.altDelegate)
        self.azDelegate = DmsDelegate(self.tree)
        self.tree.setItemDelegateForColumn(14, self.azDelegate)
 
        self.save_db_button = QPushButton("Save to DB", self)
        self.save_db_button.clicked.connect(self.save_to_db)

        layout = QVBoxLayout()
        layout.addWidget(self.tree)
        layout.addWidget(self.save_db_button)
        self.setLayout(layout)

    def save_to_db(self):
        def iterate_directory(index):
            for row in range(self.tree.model().rowCount(index)):
                child_index = self.tree.model().index(row, 0, index)
                if self.tree.model().isDir(child_index):
                    iterate_directory(child_index)
                else:
                    file_path = self.tree.model().filePath(child_index)
                    file_name = os.path.basename(file_path)
                    file_size = os.path.getsize(file_path) / (1024 * 1024)  # Convert bytes to MB

                    data = {}
                    for col, key in enumerate(fits_keywords.keys(), start=super(CustomFileSystemModel, self.tree.model()).columnCount()):
                        data[key] = self.tree.model().data(self.tree.model().index(row, col, index))

                    try:
                        cursor.execute('''
                            INSERT INTO images (
                                OBJECT, DATE_OBS, FILTER, EXPOSURE, CCD_TEMP, IMAGETYP, XBINNING, OBJECT_RA, OBJECT_DEC, OBJECT_ALT, OBJECT_AZ, GAIN, OFFSET, FILE, SIZE
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            data.get('OBJECT', ''),
                            data.get('DATE-OBS', ''),
                            data.get('FILTER', ''),
                            data.get('EXPOSURE', 0),
                            data.get('CCD-TEMP', 0.0),
                            data.get('IMAGETYP', ''),
                            data.get('XBINNING', 0),
                            data.get('OBJECT-RA', ''),
                            data.get('OBJECT-DEC', ''),
                            data.get('OBJECT-ALT', ''),
                            data.get('OBJECT-AZ', ''),
                            data.get('GAIN', 0),
                            data.get('OFFSET', 0),
                            file_name,
                            int(file_size)
                        ))
                    except sqlite3.IntegrityError as e:
                        print(f"IntegrityError: {e} for file {file_name}")
                    except Exception as e:
                        print(f"Error: {e} for file {file_name}")
        # Connect to the database (or create it if it doesn't exist)
        db_path = os.path.join(os.path.dirname(__file__), 'rsc', DBNAME)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Start iterating from the root index
        root_index = self.tree.rootIndex()
        iterate_directory(root_index)

        # Commit the transaction and close the connection
        conn.commit()
        conn.close()

        print("Data saved to database.db")
    
        print(" Emit the custom signal")
        self.save_to_db_pressed.emit()
            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = FitsBrowser()
    viewer.show()
    sys.exit(app.exec())


