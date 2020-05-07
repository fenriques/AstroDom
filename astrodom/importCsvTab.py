
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
            self.logger.info(f"Opened {filename}")

        csvList = self.app.filterDictToList('pix_csv')

        # First rows of the CSV file don't contain images.
        checkCsv = False
        self._data = []
        self._headers = []
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
                            print(filenameMatch)
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
                                item = hashItem
                                self.logger.debug(
                                    f"File {filenameMatch} found")
                            else:
                                item = "FITS file not found"
                                self.logger.debug(
                                    f"File {filenameMatch} not found")

                        filteredRow.insert(col,  str(item))

                self._data.append(filteredRow)

            # Headers row
            if dataTemp[row][0] == 'Index':
                self._headers = self.app.filterDictToList(
                    'pix_csv', 'description')
                checkCsv = True

            self.model = ImportTableModel(self._data, self._headers)
            self.mainW.ui.tableViewImportCsv.setModel(self.model)
            self.mainW.ui.tableViewImportCsv.setSortingEnabled(True)

    def filterHeaders(self, csvHeaders):
        csvList = self.app.filterDictToList('pix_csv')
        print("svList "+csvList)
        print("svheaders "+csvHeaders)
        return csvHeaders in csvList

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
            self.logger.error(f"CSV match, Fits file not found:  {fileName}")
        return ""

    # Data from PI csv (FWHM, Noise etc) are imported in db
    def saveCsv(self):

        fieldUpdate = self.app.filterDictToList('pix_csv', 'keys')
        rows = self.model.rowCount(self.mainW.ui.tableViewImportCsv.rootIndex())

        for row in range(rows):
            query = "UPDATE images SET "

            for col in range(len(fieldUpdate)):
                currentIndex = self.model.index(row, col)
                item = self.model.data(currentIndex, QtCore.Qt.DisplayRole)
                if item is not None:
                    query += str(fieldUpdate[col]) + "= '"+str(item)+"',"
                    if fieldUpdate[col] == "csvFile":
                        csvHash = str(item)
                else:
                    query += "'',"
            query = query[:-1]
            query += " WHERE hash = '"+csvHash + "';"

            try:
                ret = self.app.db.exec(query)
                if ret.lastError().number() == 19:
                    self.model.setData(
                        self.model.index(row, 5), "Error: FITS file already exists in database", QtCore.Qt.EditRole)
                    self.logger.info("Error: FITS file already exists in database")
                    error = ret.lastError().text()
                    self.logger.error(f"{error}")
                    self.logger.error(f"{query}")
                elif ret.lastError().number() > 0:
                    error = ret.lastError().text()
                    self.logger.error(f"{error}")
                    self.logger.error(f"{query}")
                else:
                    self.model.setData(
                        self.model.index(row, 5), "OK: FITS file updated", QtCore.Qt.EditRole)
                    self.logger.debug(
                        f"OK: FITS file updated with query {query}")

            except Exception as e:
                self.logger.error(f"Update error {e}")

            self.model.layoutChanged.emit()
        # Force image list data reload
        self.mainW.imageSourceModel.select()
        while (self.mainW.imageSourceModel.canFetchMore()):
            self.mainW.imageSourceModel.fetchMore()
