
import sys
import os
import csv
import hashlib
import ntpath
import logging

from pathlib import Path
from PyQt5 import QtWidgets
from PyQt5 import QtSql, QtGui, QtCore

from .importTableModel import *

'''
This class manages imports: first step is to import
FITS files and their headers scanning dirs. Then we
can add information like FWHM, noise etc importing
a CSV file as the output from SubFrameSelector from
Pixinsight. There are read and save method for both
operations (FITS import and CSV import).
The models (both FITS and CSV) are managed by 
ImportTableModel.
'''
class ImportCsvTab():
    logger = logging.getLogger(__name__)

    def __init__(self, mainW, app):
        super().__init__()
        self.mainW = mainW
        self.app = app
        # GUI logging handler
        self.handler = h = QtHandler(self.printLogMessage)
        fs = "%(asctime)s  %(levelname)-8s %(message)s"
        formatter = logging.Formatter(fs)
        h.setFormatter(formatter)
        h.setLevel(logging.INFO)
        self.logger.addHandler(h)
    
    # Slot for printing log message in the main thread
    def printLogMessage(self, msg, record):
        color = self.app.COLORS.get(record.levelno, "black")
        s = '<pre><font color="%s">%s</font></pre>' % (color, msg)
        self.mainW.ui.plainTextEditLogCsv.appendHtml(s)   
    
    def importCsvFile(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self.mainW,
            'Select a CSV file to open…',
            QtCore.QDir.homePath(),
            'CSV Files (*.csv) ;; All Files (*)'
        )
        if filename:
            with open(filename) as fh:
                csvreader = csv.reader(fh)
                dataTemp = list(csvreader)
            self.mainW.ui.lineEditCsv.setText(filename)
            self.logger.info(f"Reading {filename}")

        csvList = self.app.filterDictToList('pix_csv')

        # First rows of the CSV file don't contain images.
        checkCsv = False
        self._data = []
        self._headers = []
        i = 1
        for row, val in enumerate(dataTemp):
            if dataTemp[row][0] == 'Subframe Scale':
                subframeScale = str(dataTemp[row][1])
            if dataTemp[row][0] == 'Camera Gain':
                cameraGain = str(dataTemp[row][1])
            if dataTemp[row][0] == 'Camera Resolution':
                cameraResolution = str(dataTemp[row][1])
            if dataTemp[row][0] == 'Scale Unit':
                scaleUnit = str(dataTemp[row][1])
            if dataTemp[row][0] == 'Data Unit':
                dataUnit = str(dataTemp[row][1])

            if checkCsv == True:
                dataTemp[row].insert(0, subframeScale)
                dataTemp[row].insert(1, cameraGain)
                dataTemp[row].insert(2, cameraResolution)
                dataTemp[row].insert(3, scaleUnit)
                dataTemp[row].insert(4, dataUnit)

                self.logger.info(f"Row n {i}")
                i+=1
                # Items (columns) for each row
                filteredRow = []
                for col in range(len(val)):
                    if str(col) in csvList:
                        item = dataTemp[row][col]
                        # Check if the file (hash) exists in the database
                        if col == 8:
                            filenameMatch = ntpath.splitext(
                                ntpath.basename(item))[0]
                            '''
                            TO BE COMPLETED:
                            filenameMatch = ntpath.splitext(
                                ntpath.basename(item))[0]
                            sqlStatementF = "SELECT file FROM images where file like '%"+filenameMatch+"'%"

                            rF = self.app.db.exec(sqlStatementF)
                            rF.next()
                            if rF.value(0):
                                print("trovato")
                            else:
                                print("FITS file not found")
                            '''
                            hashItem = self.hashFile(item)
                            sqlStatement = "SELECT hash FROM images where hash = '"+hashItem+"'"

                            r = self.app.db.exec(sqlStatement)
                            r.next()
                            if r.value(0):
                                strStatus = "File found"
                                self.logger.info(
                                    f"File {filenameMatch} found in the database")
                            else:
                                strStatus = "File not found"
                                self.logger.error(
                                    f"File {filenameMatch} not found in the database")

                        filteredRow.insert(col, str(item))
                
                # Append info about matching fits file found/not found
                filteredRow.insert(len(filteredRow), strStatus)
                self._data.append(filteredRow)

            # Headers row are read after 'index' in csv file.
            if dataTemp[row][0] == 'Index':
                self._headers = self.app.filterDictToList(
                    'pix_csv', 'description')
                self._headers.append('Matching FITS File')
                checkCsv = True
                
        if checkCsv == True:
            self.model = ImportTableModel(self._data, self._headers)
            self.mainW.ui.tableViewImportCsv.setModel(self.model)
            self.mainW.ui.tableViewImportCsv.setSortingEnabled(False)
        else:
            self.logger.error("Invalid CSV format")

    def deleteRows(self):
        selected = self.mainW.ui.tableViewImportCsv.selectedIndexes()
        if selected:
            self.model.removeRows(selected[0].row(), 1, None)

    def hashFile(self, fileName):
        try:
            with open(fileName, 'rb') as afile:
                hasher = hashlib.md5()
                buf = afile.read(self.app.BLOCKSIZE)
                for i in range(5):
                    hasher.update(buf)
                    buf = afile.read(self.app.BLOCKSIZE)
            hash = hasher.hexdigest()
            return hash
        except Exception as e:
            self.logger.error(f"Hash file: fits not found:  {fileName}")
        return ""

    # Data from PI csv (FWHM, Noise etc) are imported in db
    def saveCsv(self):

        fieldUpdate = self.app.filterDictToList('pix_csv', 'keys')
        rows = self.model.rowCount(self.mainW.ui.tableViewImportCsv.rootIndex())
        self.logger.info(f"Saving {rows} CSV rows")
        
        # Each row from table view is an SQL update statement
        for row in range(rows):
            query = "UPDATE images SET "
            csvHash = ''
            for col in range(len(fieldUpdate)):
                currentIndex = self.model.index(row, col)
                item = self.model.data(currentIndex, QtCore.Qt.DisplayRole)
                if item is not None:
                    query += str(fieldUpdate[col]) + "= '"+str(item)+"',"
                    if fieldUpdate[col] == "csvFile":
                        fileName = str(item)
                        csvHash = self.hashFile(item)
                else:
                    query += "'',"
            query = query[:-1]
            query += " WHERE hash = '"+csvHash + "';"

            try:
                ret = self.app.db.exec(query)
                error = ret.lastError().text()
                if ret.lastError().number() > 0:
                    self.logger.error(f"{error}")
                    self.logger.error(f"{query}")
                else:
                    if ret.numRowsAffected() < 1:
                        self.logger.error(f"{fileName} not found")
                    else:
                        self.model.setData(
                            self.model.index(row, 10), "OK: FITS file updated", QtCore.Qt.EditRole)
                        self.logger.info(f"{fileName} updated")
                        self.logger.debug(
                            f"OK: FITS file updated with query {query}")

            except Exception as e:
                self.logger.error(f"Update error {e}")

            self.model.layoutChanged.emit()
        
        # Force image list data reload
        self.mainW.imageSourceModel.select()
        while (self.mainW.imageSourceModel.canFetchMore()):
            self.mainW.imageSourceModel.fetchMore()
        self.mainW.filterRegExpChanged()


"""
This two classes manage the GUI log messages using an additional 
log handler. Be careful that log messages are logged from outside 
of the main thread and widgets are not thread safe so we cannot 
update the GUI from inside the worker but build a signal/slot for
that. 
"""


class Signaller(QtCore.QObject):
    signal = QtCore.pyqtSignal(str, logging.LogRecord)


class QtHandler(logging.Handler):
    def __init__(self, slotfunc, *args, **kwargs):
        super(QtHandler, self).__init__(*args, **kwargs)
        self.signaller = Signaller()
        self.signaller.signal.connect(slotfunc)

    def emit(self, record):
        s = self.format(record)
        self.signaller.signal.emit(s, record)
