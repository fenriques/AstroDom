
import sys
import os
import csv
import hashlib
import ntpath
import logging

from pathlib import Path
from os.path import expanduser
from astropy.io import fits
from .astropyCalc import AstropyCalc
from PyQt5 import QtWidgets
from PyQt5 import QtSql, QtGui, QtCore
from datetime import datetime

from .importTableModel import *


class ImportDir(QtCore.QObject):
    logger = logging.getLogger(__name__)

    match_found = QtCore.pyqtSignal(list)
    finished = QtCore.pyqtSignal()

    def __init__(self, app):
        super().__init__()
        self.app = app

    def set_file(self, fileList):
        self.fileList = fileList

    @qtc.pyqtSlot()
    def do_search(self):

        self._search(self.fileList)
        self.finished.emit()

    def _search(self, fileList):

        fitsParameter = {}
        fitsKeyList = self.app.filterDictToList('fitsHeader', 'keys')
        fitsDefault = self.app.filterDictToList('fitsDefault', 'keys')

        for f in fileList:
            self.logger.info(f"importing {f}")
            row = []

            # Parse FITS header for given file
            fitsParameters = self.parseFitsHeader(f)
            for fitsParameter in fitsKeyList:
                oneitem = str(
                    fitsParameters[self.app.conf[fitsParameter]['fitsHeader']])
                row.insert(self.app.conf[fitsParameter]['order'], oneitem)

            row[fitsKeyList.index('file')] = str(f)
            row[fitsKeyList.index('hash')] = self.hashFile(f)

            # Calculate Alt, Az coordinates
            strAlt = ''
            strAz = ''
            AstropyCalcObj = AstropyCalc()

            altAz = AstropyCalcObj.getAltAzCoord(
                fitsParameters['RA'],
                fitsParameters['DEC'],
                fitsParameters['DATE-OBS'],
                fitsParameters['SITELONG'],
                fitsParameters['SITELAT'])

            if altAz:
                strAlt = str("{0.alt:.4f}".format(altAz))[:-4]
                strAz = str("{0.az:.4f}".format(altAz))[:-4]

            row[fitsKeyList.index('alt')] = strAlt
            row[fitsKeyList.index('az')] = strAz

            # if no value is read in FIT header try default value
            for keyD, valD in enumerate(fitsDefault):

                if len(row[fitsKeyList.index(valD)]) == 0:
                    defaultValue = self.app.conf[valD]['fitsDefault']
                    defaultField = self.app.conf[valD]['description']
                    self.logger.debug(
                        f"Inserted {defaultValue} for {defaultField}")
                    row[fitsKeyList.index(
                        valD)] = defaultValue
            self.match_found.emit(row)

    def parseFitsHeader(self, fitsFile):
        returnDifferentParameter = {}
        hdu = fits.open(fitsFile)
        hdr = hdu[0].header
        for fitsParameter in self.app.filterDictToList('fitsHeader'):
            if fitsParameter in hdr:
                returnDifferentParameter[fitsParameter] = hdr[fitsParameter]
            else:
                returnDifferentParameter[fitsParameter] = ''

        return returnDifferentParameter

    def hashFile(self, fileName):
        with open(fileName, 'rb') as afile:
            hasher = hashlib.md5()
            buf = afile.read(self.app.BLOCKSIZE)
            for i in range(5):
                hasher.update(buf)
                buf = afile.read(self.app.BLOCKSIZE)
        hash = hasher.hexdigest()
        return hash


class ImportTab():
    logger = logging.getLogger(__name__)

    def __init__(self, mainW, app):
        super().__init__()
        self.mainW = mainW
        self.app = app

    def addResultsToModel(self, row):
        self._data.append(row)
        self.model.layoutChanged.emit()

    def importFitsDir(self):

        # Choose dir and filter .fits files
        input_dir = QtWidgets.QFileDialog.getExistingDirectory(
            None, 'Select a folder:', expanduser("~"))
        fileList = list(Path(input_dir).rglob("*.[Ff][Ii][Tt][Ss]"))

        self.mainW.ui.lineEditFitsDir.setText(input_dir)
        self.mainW.importDir.set_file(fileList)
        self._headers = self.app.filterDictToList(
            'fitsHeader', 'description')
        self._data = []

        # Populate tableview
        self.model = ImportTableModel(self._data, self._headers)
        self.mainW.ui.tableViewImport.setSortingEnabled(True)
        self.mainW.ui.tableViewImport.setAlternatingRowColors(True)
        # self.mainW.ui.tableViewImport.hideColumn(1)  # Hide HASH

        self.mainW.ui.tableViewImport.setModel(self.model)

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
            self.mainW.ui.tableViewImport.setModel(self.model)
            self.mainW.ui.tableViewImport.setSortingEnabled(True)

    def filterHeaders(self, csvHeaders):
        csvList = self.app.filterDictToList('pix_csv')
        print("svList "+csvList)
        print("svheaders "+csvHeaders)
        return csvHeaders in csvList

    def deleteRows(self):
        selected = self.mainW.ui.tableViewImport.selectedIndexes()
        if selected:
            self.model.removeRows(selected[0].row(), 1, None)

    def hashFile(self, fileName):
        with open(fileName, 'rb') as afile:
            hasher = hashlib.md5()
            buf = afile.read(self.app.BLOCKSIZE)
            for i in range(5):
                hasher.update(buf)
                buf = afile.read(self.app.BLOCKSIZE)
        hash = hasher.hexdigest()
        return hash

    def saveFits(self):

        separator = ','
        fieldInsert = self.app.filterDictToList('fitsHeader', 'keys')
        fitsDefault = self.app.filterDictToList('fitsDefault', 'keys')
        sqlInsert = separator.join(fieldInsert)

        rows = self.model.rowCount(self.mainW.ui.tableViewImport.rootIndex())
        targetOverride = self.mainW.ui.lineEditOverrideTarget.text()

        for row in range(rows):
            emptyCellCheck = True
            query = "INSERT INTO images ( " +\
                sqlInsert + ") VALUES("

            for col, val in enumerate(fieldInsert):
                currentIndex = self.model.index(row, col)
                item = self.model.data(currentIndex, QtCore.Qt.DisplayRole)
                if len(str(item)) > 0:
                    # Override target name if asked to
                    if col == 2 and targetOverride:
                        item = targetOverride
                        self.model.setData(
                            self.model.index(row, col), item, QtCore.Qt.EditRole)
                    query += "'"+str(item)+"',"
                else:
                    # if no value is read in FIT header try default value
                    if val in fitsDefault:
                        item = self.app.conf[val]['fitsDefault']
                        query += "'"+str(item)+"',"
                    else:
                        emptyCellCheck = False

            if emptyCellCheck == False:
                continue
            query = query[:-1]
            query += ");"
            try:
                ret = self.app.db.exec(query)
                if ret.lastError().number() == 19:
                    self.model.setData(
                        self.model.index(row, 1), "Error: FITS file already exists in database", QtCore.Qt.EditRole)
                    error = ret.lastError().text()
                    self.logger.error(f"{error}")
                    self.logger.error(f"{query}")
                elif ret.lastError().number() > 0:
                    error = ret.lastError().text()
                    self.logger.error(f"{error}")
                    self.logger.error(f"{query}")
                else:
                    self.model.setData(
                        self.model.index(row, 1), "OK: FITS file saved", QtCore.Qt.EditRole)
                    self.logger.debug(
                        f"OK: FITS file saved with query {query}")

            except Exception as e:
                self.logger.error(f"Insert error {e}")

            self.model.layoutChanged.emit()
        # Force image list reload data
        self.mainW.imageSourceModel.select()
        while (self.mainW.imageSourceModel.canFetchMore()):
            self.mainW.imageSourceModel.fetchMore()

    # Data from PI csv (FWHM, Noise etc) are imported in db
    def saveCsv(self):

        fieldUpdate = self.app.filterDictToList('pix_csv', 'keys')
        rows = self.model.rowCount(self.mainW.ui.tableViewImport.rootIndex())

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
        # Force image list reload data
        self.mainW.imageSourceModel.select()
        while (self.mainW.imageSourceModel.canFetchMore()):
            self.mainW.imageSourceModel.fetchMore()
