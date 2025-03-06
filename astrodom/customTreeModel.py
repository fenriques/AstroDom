import pandas as pd
import numpy as np
import logging

from PyQt6.QtCore import QAbstractItemModel, QModelIndex, Qt, QVariant, QSize
from PyQt6.QtGui import QBrush, QColor, QFont
from PyQt6.QtCore import QSortFilterProxyModel, Qt

from astrodom.utils import format_seconds, format_file_size  # Import utility functions
from astrodom.loadSettings import *
from PyQt6.QtGui import QIcon

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

        self.checked_items = set() # Initialize the set to keep track of checked items

        self.itemList = ["Target", "#", "Exposure", "Size", "Date", "Time","Filter","FWHM", "Eccentricity","SNR","ALT", "AZ", "Temp", "Frame",
                         "Bin","RA", "DEC", "Gain", "Offset", "Mean", "Median", "Site Lat", "Site Long", "Moon Phase", "Moon Separation","File"]

        self.rootItem = TreeItem(self.itemList, None)
        self.rsc_path = importlib_resources.files("astrodom").joinpath('rsc')
        self.parent = parent

        self.setupModelData(data, self.rootItem)

    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return parent.internalPointer().columnCount()
        return self.rootItem.columnCount()

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return QVariant()

        item = index.internalPointer()
        
        match role:
            case Qt.ItemDataRole.DisplayRole:
                # Format the date and time
                if index.column() == self.itemList.index("Exposure"):
                    if not item.parent().parent(): # Target grouping row
                        return format_seconds(item.data(index.column()), "hms")
                    elif item.parent() and item.parent().parent() == self.rootItem: #Filter grouping row
                        return format_seconds(item.data(index.column()), "hms")

                    else:
                        return format_seconds(item.data(index.column()), "s") # Image row

                # Format the file size
                if index.column() == self.itemList.index("Size"):
                    return format_file_size(item.data(index.column()))

                #  Add the check box for the target rows
                if (index.column() == self.itemList.index("FWHM") and hasattr(self, 'fwhm') and item.data(index.column()) and float(item.data(index.column())) > self.fwhm) or \
                    (index.column() == self.itemList.index("Eccentricity") and hasattr(self, 'eccentricity') and item.data(index.column()) and float(item.data(index.column())) > self.eccentricity) or \
                    (index.column() == self.itemList.index("SNR") and hasattr(self, 'snr') and item.data(index.column()) and float(item.data(index.column())) < self.snr) or \
                    (index.column() == self.itemList.index("ALT") and hasattr(self, 'alt') and item.data(index.column()) and float(item.data(index.column())) < self.alt) :
                    parent_parent_row = index.parent().parent().row()
                    parent_row = index.parent().row()            
                    if parent_parent_row >=0 and parent_row >=0:
                        self.checked_items.add((parent_parent_row,parent_row, index.row()))
                
                # Format FWHM and Eccentricity
                
                if index.column() == self.itemList.index("FWHM") or index.column() == self.itemList.index("Eccentricity") or \
                    index.column() == self.itemList.index("SNR") or index.column() == self.itemList.index("Mean") or \
                    index.column() == self.itemList.index("Median"):

                    if item.data(index.column()) == "":
                        return ""
                    else:
                        return f"{float(item.data(index.column())):.2f}"

                return item.data(index.column())
        
            case Qt.ItemDataRole.DecorationRole:
                if index.column() == self.itemList.index("Date"):
                    moon_icon = QIcon(str(self.rsc_path.joinpath( 'icons', self.get_moon_phase_icon(item.data(self.itemList.index("Moon Phase"))))))
                    return moon_icon
            
            case Qt.ItemDataRole.ToolTipRole:
                if index.column() == self.itemList.index("Date"):
                    return f"Moon Illumination: {item.data(self.itemList.index("Moon Phase"))}%\nMoon to Target Separation: {item.data(self.itemList.index("Moon Separation"))} degrees"
                
            case Qt.ItemDataRole.BackgroundRole:
                # Set the background color for the filters for  filter grouped rows 
                if item.parent() and item.parent().parent() == self.rootItem:
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
                
            case Qt.ItemDataRole.FontRole:
                # Set the font style for the grouped rows at target level
                if not item.parent().parent():
                    font = QFont()
                    font.setBold(True)
                    font.setItalic(True)

                    return font
                # Set the font style for the grouped rows at filter level
                elif item.parent() and item.parent().parent() == self.rootItem:
                    font = QFont()
                    font.setItalic(True)
                    return font

                return QVariant()
        

            # Set the text alignment for the columns
            case Qt.ItemDataRole.TextAlignmentRole:
                if index.column() == self.itemList.index("Target"):
                    return Qt.AlignmentFlag.AlignLeft
                elif index.column() == self.itemList.index("Exposure") or index.column() == self.itemList.index("Size"): 
                    return Qt.AlignmentFlag.AlignRight
                else:
                    return Qt.AlignmentFlag.AlignCenter

            case Qt.ItemDataRole.CheckStateRole:
                if index.column() == self.itemList.index("Target") and item.childCount() == 0:
                    if (index.parent().parent().row(),index.parent().row(), index.row()) in self.checked_items:
                        return Qt.CheckState.Checked
                    else:
                        return Qt.CheckState.Unchecked

        return None
       
    def get_moon_phase_icon(self,phase):
        if phase == "":
            return ""
        phase = float(phase)

        if phase < 12.5:    
            return "newmoon.png" 
        elif phase < 25:
            return "waxinggibbous.png"
        elif phase < 37.5:
            return "firstquarter.png"
        elif phase < 50:
            return "waxingcrescent.png"
        elif phase < 62.5:
            return "fullmoon.png" 
        elif phase < 75:
            return "waningcrescent.png"
        elif phase < 87.5:
            return "lastquarter.png" 
        else:
            return "waninggibbous.png"
    
    def setThresholds(self, fwhm, snr, alt, eccentricity):
        self.fwhm = float(fwhm)
        self.snr = float(snr)
        self.alt = float(alt)
        self.eccentricity = float(eccentricity)
        self.checked_items.clear()

        return None
    
    # This function is called from the mainWindow when the 'file operation' button is pressed.
    # It returns a list of selected file names that will be managed by FileOperationDialog
    def get_checked_files(self):
        files = []
        
        # Iterate over the checked_items and retrieve the file name from 'File' column
        for parent_parent_row, parent_row, row in self.checked_items:
            parent_parent_index = self.index(parent_parent_row, 0, QModelIndex())
            parent_index = self.index(parent_row, 0, parent_parent_index)
            index = self.index(row, self.itemList.index("File"), parent_index)
        
            files.append(self.data(index, Qt.ItemDataRole.DisplayRole))
            logging.debug(self.data(index, Qt.ItemDataRole.DisplayRole))
        
        return files

    def setData(self, index, value, role):
        if not index.isValid():
            return False
        
        logging.debug(f"Index: {self.checked_items}")
        
        if role == Qt.ItemDataRole.CheckStateRole :
            # Target level
            parent_parent_row = index.parent().parent().row()
            # Filter level
            parent_row = index.parent().row()           

            # If the selected checkbox in a row is already in the checked_items set, it is removed
            if (parent_parent_row,parent_row, index.row()) in self.checked_items:
                self.checked_items.discard((parent_parent_row,parent_row, index.row()))

            else:
                # The item row is added to the checked_items set
                self.checked_items.add((parent_parent_row,parent_row, index.row()))

            #self.dataChanged.emit(index, index,  [Qt.ItemDataRole.CheckStateRole])
            return True

        return False

    def flags(self, index):
        if not index.isValid():
            logging.warning("Index is not valid")
            return Qt.ItemFlag.ItemIsEnabled

        flags = super().flags(index)
        # Set the flags for the target column
        if index.column() == self.itemList.index("Target") :  
            flags |= Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsSelectable 

        return flags
    

    def getItem(self, index):
        if index.isValid():
            item = index.internalPointer()
            if item:
                return item
        return self.rootItem

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
        # The dashboard is a tree structure with the following hierarchy:
        # Target/object -> Filter -> Image
        # The first iteration is on the object level, the second on the filter level, and the third on the image level
        for object_name, object_group in data.groupby('OBJECT'):

            object_item = TreeItem([object_name, len(object_group), str(object_group['EXPOSURE'].sum()), object_group['SIZE'].sum(), 
                                    "","", "", str(object_group['FWHM'].mean()), str(object_group['ECCENTRICITY'].mean()), 
                                    "", "", "", "", "", "", "", "", "", "", "", "", 
                                    "", "", "", "", "", ""], parent)
            parent.appendChild(object_item)

            
            #Second iteration on the filter level
            for filter_name, filter_group in object_group.groupby('FILTER'):

                #Compute SNR at filter level
                if np.sqrt(np.sum(np.square(filter_group['STD']))) != 0:
                    filter_snr = str((filter_group['MEDIAN']-BIAS_SIGNAL).sum()/np.sqrt(np.sum(np.square(filter_group['STD']))))
                else:
                    filter_snr = ""

                filter_item = TreeItem([filter_name, len(filter_group), filter_group['EXPOSURE'].sum(), filter_group['SIZE'].sum(), 
                                        "", "", "", str(filter_group['FWHM'].mean()), str(filter_group['ECCENTRICITY'].mean()), 
                                        filter_snr, "", "", 
                                        "", "", "", "", "", "", "", str(filter_group['MEAN'].mean()), str(filter_group['MEDIAN'].mean()), 
                                        "", "", "", "", "", ""], object_item)
                
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
                        str((image_row['MEDIAN']-BIAS_SIGNAL)/image_row['STD']),
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
                        image_row['SITELAT'],
                        image_row['SITELONG'],
                        image_row['MOON_PHASE'],
                        image_row['MOON_SEPARATION'],
                        image_row['FILE'],
                    ], filter_item)
                    filter_item.appendChild(image_item)
