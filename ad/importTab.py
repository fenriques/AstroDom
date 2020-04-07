
import sys
import os
import csv
import hashlib
import ntpath


from pathlib import Path
from os.path import expanduser
from astropy.io import fits
from .astropyCalc import AstropyCalc
from PyQt5 import QtWidgets
from PyQt5 import QtSql, QtGui, QtCore
from datetime import datetime

from .importTableModel import *


class ImportTab():

    def __init__(self, mainW, app):
        super().__init__()
        self.mainW = mainW
        self.app = app

    def importFitsDir(self):

        # List .fits file contained in chosen dir
        fileList = []
        fitsParameter = {}

        # Choose dir and filter .fits files
        input_dir = QtWidgets.QFileDialog.getExistingDirectory(
            None, 'Select a folder:', expanduser("~"))
        fileList = list(Path(input_dir).rglob("*.[Ff][Ii][Tt][Ss]"))

        fitsKeyList = self.app.filterDictToList('fitsHeader', 'keys')
        self._headers = self.app.filterDictToList(
            'fitsHeader', 'description')
        self._data = []

        # Populate tableview
        for f in fileList:
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

            self._data.append(row)

        self.model = ImportTableModel(self._data, self._headers)
        self.mainW.ui.tableViewImport.setSortingEnabled(True)
        self.mainW.ui.tableViewImport.setAlternatingRowColors(True)
        self.mainW.ui.tableViewImport.hideColumn(2)  # Hide HASH

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
                            hashItem = self.hashFile(item)
                            sqlStatement = "SELECT hash FROM images where hash = '"+hashItem+"'"

                            r = self.app.db.exec(sqlStatement)
                            r.next()
                            if r.value(0):
                                item = "Corresponding FITS file found"
                            else:
                                item = "FITS file not found"
                        filteredRow.insert(col,  str(item))
                        """
                        print("row "+str(row) +
                              " col " + str(col) +
                              " item "+str(item))
                        """
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

    def saveDB(self):

        row = 0
        col = 0
        separator = ','
        fieldInsert = self.app.filterDictToList('fitsHeader', 'keys')
        sqlInsert = separator.join(fieldInsert)

        for r in range(self.mainW.ui.tableWidgetData.rowCount()):
            query = "INSERT INTO images ( " +\
                sqlInsert + ") VALUES("

            for cl in range(len(fieldInsert)):
                item = self.mainW.ui.tableWidgetData.item(row, col)
                if item is not None:
                    query += "'"+item.text()+"',"
                else:
                    query += "'',"
                col += 1
            col = 0
            row += 1
            query = query[:-1]
            query += ");"
            try:
                self.app.db.exec(query)
            except Exception as e:
                print(f'Insert error: {e}')

        self.mainW.ui.tableWidgetData.clear()

    def updateDB(self):
        if self.model:
            self.model.save_data()

    def updateDB2(self):

        row = 0
        col = 0

        fieldUpdate = self.app.filterDictToList('pix_csv', 'keys')

        for r in range(self.mainW.ui.tableWidgetData.rowCount()):
            query = "UPDATE images SET "

            for field in range(len(fieldUpdate)):

                item = self.mainW.ui.tableWidgetData.item(row, col)
                if item is not None:
                    query += str(fieldUpdate[field]) + "= '"+item.text()+"',"
                    if fieldUpdate[field] == "csvFile":
                        csvHash = item.text()
                else:
                    query += "'',"
                col += 1
            col = 0
            row += 1
            query = query[:-1]
            query += " WHERE hash = '"+csvHash + "';"
            self.app.db.exec(query)

        self.mainW.ui.tableWidgetData.clear()
