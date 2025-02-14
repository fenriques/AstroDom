import sys
import os
from PyQt6.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QHeaderView
from astropy.io import fits
from datetime import datetime

class FitsHeaderTable(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('FITS Headers')
        self.setGeometry(100, 100, 800, 600)
        self.layout = QVBoxLayout()
        self.table_widget = QTableWidget()
        self.layout.addWidget(self.table_widget)
        self.setLayout(self.layout)
        self.folder_path = "/home/ferrante/astrophoto/M81/"
        self.fits_keywords = {
            "OBJECT": {'fits_key': ["OBJECT", "OBJ", "TARGET"], 'type': 'text', 'display_name': 'Target'},
            "DATE-OBS": {'fits_key': ["DATE-OBS", "DATE"], 'type': 'datetime', 'display_name': 'Date'},
            "IMAGETYP": {'fits_key': ["IMAGETYP"], 'type': 'text', 'display_name': 'Frame'},
            "OBJECT-RA": {'fits_key': ["OBJCTRA"], 'type': 'text', 'display_name': 'RA'},
            "OBJECT-DEC": {'fits_key': ["OBJCTDEC"], 'type': 'text', 'display_name': 'DEC'},
            "OBJECT-ALT": {'fits_key': ["OBJCTALT"], 'type': 'text', 'display_name': 'ALT'},
            "OBJECT-AZ": {'fits_key': ["OBJCTAZ"], 'type': 'text', 'display_name': 'AZ'},
            "XBINNING": {'fits_key': ["XBINNING"], 'type': 'int', 'display_name': 'Bin X'},
            "YBINNING": {'fits_key': ["YBINNING"], 'type': 'int', 'display_name': 'Bin Y'},
            "EXPOSURE": {'fits_key': ["EXPOSURE","EXPTIME"], 'type': 'int', 'display_name': 'Exposure'},
            "CCD-TEMP": {'fits_key': ["CCD-TEMP"], 'type': 'float', 'display_name': 'Temperature'},
            "FILTER": {'fits_key': ["FILTER"], 'type': 'filter', 'display_name': 'Filter'},
            "GAIN": {'fits_key': ["GAIN"], 'type': 'int', 'display_name': 'Gain'},
            "OFFSET": {'fits_key': ["OFFSET"], 'type': 'int', 'display_name': 'Offset'},
        }
        self.filters = {"L": ["Luminance", "luminance", "Lum", "lum", "L", "l"], "R": ["Red", "R", "r", "red"], "B": ["Blue", "B", "b", "blue"], "G": ["Green", "G", "g", "green"], "Ha": ["Ha", "ha", "Halpha", "halpha", "H_alpha", "h_alpha", "H_Alpha", "h_Alpha"], "Sii": ["SII", "Sii", "sii"], "Oiii": ["OIII", "Oiii", "oiii", "O3"], "LPR": ["Lpr", "LPR", "lpr"]}
        self.filters_background = {"L": ["Luminance", "luminance", "Lum", "lum", "L", "l"], "R": ["Red", "R", "r", "red"], "B": ["Blue", "B", "b", "blue"], "G": ["Green", "G", "g", "green"], "Ha": ["Ha", "ha", "Halpha", "halpha", "H_alpha", "h_alpha", "H_Alpha", "h_Alpha"], "Sii": ["SII", "Sii", "sii"], "Oiii": ["OIII", "Oiii", "oiii", "O3"], "LPR": ["Lpr", "LPR", "lpr"]}
        
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table_widget.setSortingEnabled(True)
        self.load_fits_headers(self.folder_path)

    def load_fits_headers(self, folder_path):
        fits_files = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(('.fits', '.fit')):
                    fits_files.append(os.path.join(root, file))

        if not fits_files:
            print("No FITS files found in the folder.")
            return

        # Set the columns based on self.fits_keywords
        filtered_keys = list(self.fits_keywords.keys())
        display_names = [value['display_name'] for value in self.fits_keywords.values()]

        self.table_widget.setColumnCount(len(filtered_keys))
        self.table_widget.setHorizontalHeaderLabels(display_names)
        self.table_widget.setRowCount(len(fits_files))

        for row, fits_file in enumerate(fits_files):
            with fits.open(fits_file) as hdul:
                header = hdul[0].header
            for col, key in enumerate(filtered_keys):
                for fits_key in self.fits_keywords[key]['fits_key']:
                    if fits_key in header:
                        item_value = header[fits_key]
                        break
                else:
                    item_value = ''
                try:
                    # Format the item value if necessary
                    if self.fits_keywords[key]['type'] == 'datetime' and item_value:
                        try:
                            item_value = datetime.strptime(item_value, '%Y-%m-%dT%H:%M:%S.%f').strftime('%d-%m-%Y %H:%M:%S')
                        except ValueError:
                            item_value = datetime.strptime(item_value, '%Y-%m-%dT%H:%M:%S').strftime('%d-%m-%Y %H:%M:%S')
                    elif self.fits_keywords[key]['type'] == 'int' and item_value:
                        item_value = int(item_value)
                    elif self.fits_keywords[key]['type'] == 'text' and item_value:
                        item_value = str(item_value)
                    elif self.fits_keywords[key]['type'] == 'filter' and item_value:
                        for filter_key, filter_values in self.filters.items():
                            if item_value in filter_values:
                                item_value = filter_key
                except Exception as e:
                    item_value = ''
                item = QTableWidgetItem(str(item_value))
                self.table_widget.setItem(row, col, item)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    folder_path = '/path/to/your/fits/files'  # Change this to your folder path
    fits_header_table = FitsHeaderTable()
    fits_header_table.show()
    sys.exit(app.exec())