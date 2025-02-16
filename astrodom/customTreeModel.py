import pandas as pd
import numpy as np
import logging

from PyQt6.QtCore import QAbstractItemModel, QModelIndex, Qt, QVariant, QSize
from PyQt6.QtGui import QBrush, QColor, QFont
from PyQt6.QtCore import QSortFilterProxyModel, Qt

from astrodom.utils import format_seconds, format_file_size  # Import utility functions
from astrodom.loadSettings import *

class CustomFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.filter_string = ""

    def setFilterString(self, filter_string):
        self.filter_string = filter_string
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):

        model = self.sourceModel()
        index = model.index(source_row, 0, source_parent)
        if not index.internalPointer().parent().parent():
        #return self.filter_string.lower() in model.data(index, Qt.ItemDataRole.DisplayRole).lower()
            return self.filter_string.lower() in model.data(index, Qt.ItemDataRole.DisplayRole).lower()
        else:
            return True
   
class TreeItem:
    def __init__(self, data, parent=None):
        self.parentItem = parent
        self.itemData = [str(d) for d in data]
        self.childItems = []

    def appendChild(self, item):
        self.childItems.append(item)

    def child(self, row):
        return self.childItems[row]

    def childCount(self):

        return len(self.childItems)

    def columnCount(self):
        return len(self.itemData)

    def data(self, column):
        if column < len(self.itemData):
            return self.itemData[column]
        return None

    def parent(self):
        return self.parentItem

    def row(self):
        if self.parentItem:
            return self.parentItem.childItems.index(self)
        return 0

class CustomTreeModel(QAbstractItemModel):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        itemList = ["Target", "#", "Exposure", "Size", "Date", "Time","Filter","FWHM", "Eccentricity","SNR","ALT", "AZ", "Temp", "Frame"]
        if COMPACT_DASHBOARD == "Extended": 
            itemList.extend(["Bin","RA", "DEC", "Gain", "Offset", "Mean", "Median"])
        itemList.extend(["File"])

        self.rootItem = TreeItem(itemList, None)
        self.hiddenColumns = [self.rootItem.columnCount() - 1]
        
        self.setupModelData(data, self.rootItem)

    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return parent.internalPointer().columnCount()
        return self.rootItem.columnCount()

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return QVariant()

        item = index.internalPointer()

        if role == Qt.ItemDataRole.DisplayRole:
            # Format the date and time
            if index.column() == 2:
                if not index.internalPointer().parent().parent(): # Target grouping row
                    return format_seconds(item.data(index.column()), "hms")
                elif index.internalPointer().parent() and index.internalPointer().parent().parent() == self.rootItem: #Filter grouping row
                    return format_seconds(item.data(index.column()), "hms")

                return format_seconds(item.data(index.column()), "s") # Image row

            # Format the file size
            if index.column() == 3:
                return format_file_size(item.data(index.column()))


            # Format FWHM and Eccentricity
            if index.column() in [7,8,9,19,20]:
                if item.data(index.column()) == "":
                    return ""
                else:
                    return f"{float(item.data(index.column())):.2f}"

            return item.data(index.column())
    
        if role == Qt.ItemDataRole.BackgroundRole:
            # Set the background color for the filters for  filter grouped rows 
            if index.internalPointer().parent() and index.internalPointer().parent().parent() == self.rootItem:
                if item.data(0) in ["Luminance", "luminance", "Lum", "lum", "L", "l"]:
                    return QBrush(QColor(244, 244, 244, 35))
                elif item.data(0) in ["Red", "R", "r", "red"]:
                    return QBrush(QColor(255, 0, 0, 35))
                elif item.data(0) in ["Blue", "B", "b", "blue"]:
                    return QBrush(QColor(55, 55, 255, 35))
                elif item.data(0) in ["Green", "G", "g", "green"]:
                    return QBrush(QColor(0, 140, 55, 35))
                elif item.data(0) in ["Ha", "ha", "Halpha", "halpha", "H_alpha", "h_alpha", "H_Alpha", "h_Alpha"]:
                    return QBrush(QColor(190, 255, 0, 35))
                elif item.data(0) in ["OIII", "Oiii", "oiii", "O3"]:
                    return QBrush(QColor(150, 200, 255, 35))
                elif item.data(0) in ["SII", "Sii", "sii"]:
                    return QBrush(QColor(255, 120, 190, 35))
            return QVariant()
            
        if role == Qt.ItemDataRole.FontRole:
            # Set the font style for the grouped rows at target level
            if not index.internalPointer().parent().parent():
                font = QFont()
                font.setBold(True)
                font.setItalic(True)

                return font
            # Set the font style for the grouped rows at filter level
            elif index.internalPointer().parent() and index.internalPointer().parent().parent() == self.rootItem:
                font = QFont()
                font.setItalic(True)
                return font

            return QVariant()
        if role == Qt.ItemDataRole.SizeHintRole:
            if index.column() in self.hiddenColumns:
                return QSize(0, 0)
    # Set the text alignment for the columns
        if role == Qt.ItemDataRole.TextAlignmentRole:
            if index.column() in [0]: # Left align the Target column
                return Qt.AlignmentFlag.AlignLeft
            elif index.column() in [2,3]: # Right align the Exposure and Size columns
                return Qt.AlignmentFlag.AlignRight
            else:
                return Qt.AlignmentFlag.AlignCenter

        return QVariant()

    def flags(self, index):
        if not index.isValid():
            logging.warning("Index is not valid")
            return Qt.ItemFlag.ItemIsEnabled
        
        if index.column() == 1:
            #logging.debug(f"Index {index.column()} value {index.internalPointer().data(index.column())} ")
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEditable
        
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable 

    def headerData(self, section, orientation, role):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.rootItem.data(section)

        return QVariant()

    def index(self, row, column, parent=QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()

        if parentItem == self.rootItem:
            return QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent=QModelIndex()):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        return parentItem.childCount()

    def setupModelData(self, data, parent):

        for object_name, object_group in data.groupby('OBJECT'):
            object_item = TreeItem([object_name, len(object_group), str(object_group['EXPOSURE'].sum()), object_group['SIZE'].sum(), 
                                    "","", "", str(object_group['FWHM'].mean()), str(object_group['ECCENTRICITY'].mean()), "", "", "", 
                                    "", "", "", "", "", "", "", "", "", ""], parent)
            parent.appendChild(object_item)
            parent.appendChild(TreeItem(["","","","","","","","","","","","","","","","","","","", "", "", "", ""],parent))
            
            for filter_name, filter_group in object_group.groupby('FILTER'):
                #Compute SNR
                if np.sqrt(np.sum(np.square(filter_group['STD']))) != 0:
                    snr = str(filter_group['MEAN'].sum()/np.sqrt(np.sum(np.square(filter_group['STD']))))
                else:
                    snr = ""
                filter_item = TreeItem([filter_name, len(filter_group), filter_group['EXPOSURE'].sum(), filter_group['SIZE'].sum(), 
                                        "", "", "", str(filter_group['FWHM'].mean()), str(filter_group['ECCENTRICITY'].mean()), 
                                        snr, "", "", 
                                        "", "", "", "", "", "", "", str(filter_group['MEAN'].sum()), str(filter_group['MEDIAN'].sum()), 
                                        "", ""], object_item)
                
                object_item.appendChild(filter_item)
                
                for _, image_row in filter_group.iterrows():
                    image_item = TreeItem([
                        image_row['OBJECT'], 
                        "", 
                        image_row['EXPOSURE'], 
                        image_row['SIZE'], 
                        image_row['DATE_OBS'], 
                        image_row['DATE_OBS'], # Second column DATE_OBS needed for splitting date and time
                        image_row['FILTER'], 
                        image_row['FWHM'],
                        image_row['ECCENTRICITY'],
                        image_row['STD'],
                        image_row['OBJECT_ALT'], 
                        image_row['OBJECT_AZ'],
                        image_row['CCD_TEMP'], 
                        image_row['IMAGETYP'], 
                        image_row['XBINNING'], 
                        image_row['OBJECT_RA'], 
                        image_row['OBJECT_DEC'], 
                        image_row['GAIN'],
                        image_row['OFFSET'],
                        image_row['MEAN'],
                        image_row['MEDIAN'],
                        image_row['FILE'],
                    ], filter_item)
                    filter_item.appendChild(image_item)
