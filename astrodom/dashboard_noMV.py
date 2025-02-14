import sys
import sqlite3
import pandas as pd

from PyQt6.QtWidgets import QApplication, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget, QHeaderView, QMenu
from PyQt6.QtCore import Qt, QSize
from viewDelegates import *
from utils import format_seconds, format_file_size  # Import utility functions

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
}


class Dashboard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Dashboard")
        self.setGeometry(100, 100, 800, 600)
        self.layout = QVBoxLayout(self)
        
        self.tree = QTreeWidget()
        self.tree.setColumnCount(3)
        self.tree.setHeaderLabels(["Target", "#", "Exposure", "Size","Filter", "Date", "Temp", "Frame","Binning","RA", "DEC", "ALT", "AZ"])
        self.tree.setAlternatingRowColors(True)
        self.tree.setColumnWidth(0, 250)
        self.tree.header().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)

        '''
        self.filterDelegate = FilterDelegate(self.tree)
        self.tree.setItemDelegateForColumn(2, self.filterDelegate)
        self.frameDelegate = FrameDelegate(self.tree)
        self.tree.setItemDelegateForColumn(5, self.frameDelegate)
        self.raDelegate = HmsDelegate(self.tree)
        self.tree.setItemDelegateForColumn(7, self.raDelegate)
        self.decDelegate = DmsDelegate(self.tree)
        self.tree.setItemDelegateForColumn(8, self.decDelegate)
        self.altDelegate = DmsDelegate(self.tree)
        self.tree.setItemDelegateForColumn(9, self.altDelegate)
        self.azDelegate = DmsDelegate(self.tree)
        self.tree.setItemDelegateForColumn(10, self.azDelegate)
        '''

        self.layout.addWidget(self.tree)
        self.load_data()
        
    def load_data(self):
        # Connect to the database
        conn = sqlite3.connect(DBNAME)
        query = "SELECT * FROM images"
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # Group by OBJECT and calculate number of records and total EXPOSURE
        grouped_df = df.groupby('OBJECT').agg({'EXPOSURE': 'sum', 'SIZE': 'sum', 'OBJECT': 'count'}).rename(columns={'OBJECT': 'n', 'EXPOSURE': 'totExposure',  'SIZE': 'totSize'}).reset_index()

        # Clear the tree widget
        self.tree.clear()

        # Populate the tree widget
        for _, row in grouped_df.iterrows():
            parent = QTreeWidgetItem(self.tree)
            
            spacer = QTreeWidgetItem(self.tree)
            spacer.setDisabled(True)
            spacer.setSizeHint(0, QSize(0, 5))

            parent.setText(0, row['OBJECT'])
            parent.setTextAlignment(0, Qt.AlignmentFlag.AlignLeft)
            parent.setText(1, str(row['n']))
            parent.setTextAlignment(1, Qt.AlignmentFlag.AlignCenter)
            parent.setText(2, format_seconds(row['totExposure'], "hms"))
            parent.setTextAlignment(2, Qt.AlignmentFlag.AlignRight)
            parent.setText(3, format_file_size(row['totSize']))
            parent.setTextAlignment(3, Qt.AlignmentFlag.AlignRight)

            # Set background color and font
            font = parent.font(0)
            font.setBold(True)
            dark_blue = self.palette().brush(self.backgroundRole()).color().darker(250)
            dark_blue.setRgb(0, 0, 111,50)  # RGB for dark blue
            for col in range(13):
                parent.setFont(col, font)
            # Add child items for drill down
            object_records = df[df['OBJECT'] == row['OBJECT']]
            #filters = object_records.groupby('FILTER')
            #filters = object_records.groupby('FILTER').agg({'EXPOSURE': 'sum', 'SIZE': 'sum', 'OBJECT': 'count'}).rename(columns={'OBJECT': 'filter_n', 'EXPOSURE': 'filter_totExposure',  'SIZE': 'filter_totSize'}).reset_index()
            filters = object_records.groupby('FILTER').agg({
                'EXPOSURE': 'sum',
                'SIZE': 'sum',
                'FILTER': 'count'
            }).rename(columns={
                'FILTER': 'filter_n',
                'EXPOSURE': 'filter_totExposure',
                'SIZE': 'filter_totSize'
            }).reset_index()
            for _, filter_row in filters.iterrows():
                filter_item = QTreeWidgetItem(parent)
                filter_item.setText(0, filter_row['FILTER'])
                filter_item.setTextAlignment(0, Qt.AlignmentFlag.AlignLeft)
                filter_item.setText(1, str(filter_row['filter_n']))
                filter_item.setTextAlignment(1, Qt.AlignmentFlag.AlignCenter)
                filter_item.setText(2, format_seconds(filter_row['filter_totExposure'], "hms"))
                filter_item.setTextAlignment(2, Qt.AlignmentFlag.AlignRight)
                filter_item.setText(3, format_file_size(filter_row['filter_totSize']))
                filter_item.setTextAlignment(3, Qt.AlignmentFlag.AlignRight)

                # Set background color
                bg = self.palette().brush(self.backgroundRole()).color().darker(250)
                if filter_row['FILTER'] in ["Luminance", "luminance", "Lum", "lum", "L", "l"]:
                    bg.setRgb(244, 244, 244, 35)
                elif filter_row['FILTER'] in ["Red", "R", "r", "red"]:
                    bg.setRgb(255, 0, 0, 35)
                elif filter_row['FILTER'] in ["Blue", "B", "b", "blue"]:
                    bg.setRgb(55, 55, 255, 35)
                elif filter_row['FILTER'] in ["Green", "G", "g", "green"]:
                    bg.setRgb(0, 140, 55, 35)
                elif filter_row['FILTER'] in ["Ha", "ha", "Halpha", "halpha", "H_alpha", "h_alpha", "H_Alpha", "h_Alpha"]:
                    bg.setRgb(190, 255, 0, 35)
                elif filter_row['FILTER'] in ["OIII", "Oiii", "oiii", "O3"]:
                    bg.setRgb(150, 200, 255, 35)
                elif filter_row['FILTER'] in ["SII", "Sii", "sii"]:
                    bg.setRgb(255, 120, 190, 35)

                for col in range(13):
                    filter_item.setBackground(col, bg)
                    filter_item.setFont(col, font)    
                    filter_item.setForeground(col, Qt.GlobalColor.lightGray)
                
                # Add child items for each record under the filter
                filter_records = object_records[object_records['FILTER'] == filter_row['FILTER']]
                for _, record in filter_records.iterrows():
                    record_item = QTreeWidgetItem(filter_item)
                    record_item.setText(0, record['FILE'])
                    record_item.setTextAlignment(0, Qt.AlignmentFlag.AlignLeft)
                    record_item.setText(1, " ")
                    record_item.setText(2, format_seconds(record['EXPOSURE'], "s"))
                    record_item.setTextAlignment(2, Qt.AlignmentFlag.AlignRight)
                    record_item.setText(3, format_file_size(record['SIZE']))
                    record_item.setTextAlignment(3, Qt.AlignmentFlag.AlignRight)
                    record_item.setText(4, record['FILTER'])
                    record_item.setTextAlignment(4, Qt.AlignmentFlag.AlignCenter)
                    record_item.setText(5, record['DATE_OBS'])
                    record_item.setTextAlignment(5, Qt.AlignmentFlag.AlignCenter)
                    record_item.setText(6, str(record['CCD_TEMP']))
                    record_item.setTextAlignment(6, Qt.AlignmentFlag.AlignRight)
                    record_item.setText(7, record['IMAGETYP'])
                    record_item.setTextAlignment(7, Qt.AlignmentFlag.AlignCenter)
                    record_item.setText(8, str(record['XBINNING']))
                    record_item.setTextAlignment(8, Qt.AlignmentFlag.AlignCenter)
                    record_item.setText(9, record['OBJECT_RA'])
                    record_item.setTextAlignment(9, Qt.AlignmentFlag.AlignCenter)
                    record_item.setText(10, record['OBJECT_DEC'])
                    record_item.setTextAlignment(10, Qt.AlignmentFlag.AlignCenter)
                    record_item.setText(11, record['OBJECT_ALT'])
                    record_item.setTextAlignment(11, Qt.AlignmentFlag.AlignCenter)
                    record_item.setText(12, record['OBJECT_AZ'])
                    record_item.setTextAlignment(12, Qt.AlignmentFlag.AlignCenter)


        self.tree.collapseAll()
    
    def refresh_tree(self):
        print("Refreshing tree")
        self.load_data()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = Dashboard()
    viewer.show()
    sys.exit(app.exec())
