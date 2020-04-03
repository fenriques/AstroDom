
import sys
import os
import csv
import hashlib
import ntpath


from pathlib import Path
from os.path import expanduser
from astropy.io import fits
from .astropyCalc import AstropyCalc
from PyQt5.QtWidgets import QTableWidgetItem, QFileDialog
from PyQt5 import QtSql, QtGui, QtCore
from .csvTableView import *


class ImportTab():

    def __init__(self, mainW, app):
        super().__init__()
        self.mainW = mainW
        self.app = app

    def importFitsDir(self):

        # Table row counter
        rowTable = 0

        # List .fits file contained in chosen dir
        fileList = []
        fitsParameter = {}

        fitsKeyList = self.app.filterDictToList('fitsHeader', 'keys')

        self.mainW.ui.tableWidgetData.setHorizontalHeaderLabels(fitsKeyList)

        # Choose dir and filter .fits files
        input_dir = QFileDialog.getExistingDirectory(
            None, 'Select a folder:', expanduser("~"))
        fileList = list(Path(input_dir).rglob("*.[Ff][Ii][Tt][Ss]"))

        # Create a list containing the files
        for file in fileList:
            rowPosition = self.mainW.ui.tableWidgetData.rowCount()
            self.mainW.ui.tableWidgetData.insertRow(rowPosition)

            fileItem = QTableWidgetItem(str(file))
            self.mainW.ui.tableWidgetData.setItem(rowTable, 0, fileItem)
            hashItem = QTableWidgetItem(self.hashFile(file))
            self.mainW.ui.tableWidgetData.setItem(rowTable, 1, hashItem)

            rowTable += 1

        rowTable = 0

        # Populate tablewidget
        for f in fileList:

            fitsParameters = self.parseFitsHeader(f)

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

            altItem = QTableWidgetItem(strAlt)
            self.mainW.ui.tableWidgetData.setItem(
                rowTable, self.app.conf['alt']['order'], altItem)

            azItem = QTableWidgetItem(strAz)
            self.mainW.ui.tableWidgetData.setItem(
                rowTable, self.app.conf['az']['order'], azItem)

            for fitsParameter in fitsKeyList:
                oneitem = QTableWidgetItem(
                    str(fitsParameters[self.app.conf[fitsParameter]['fitsHeader']]))
                if self.mainW.ui.tableWidgetData.item(rowTable, self.app.conf[fitsParameter]['order']) is None:

                    self.mainW.ui.tableWidgetData.setItem(
                        rowTable, self.app.conf[fitsParameter]['order'], oneitem)
            rowTable += 1

    def importCSV(self, data):
        # counts the rows read from file
        rowFile = 0
        # Table row counter
        rowTable = 0
        self.data = data

        csvList = self.app.filterDictToList('pix_csv')
        self.mainW.ui.tableWidgetData.setHorizontalHeaderLabels(
            self.app.filterDictToList('pix_csv', 'description'))

        for csvRow in self.data:
            # File column counter
            colFile = 0
            # Table column counter
            colTable = 0

            # Some parameters in the header of csv are 0.0'
            # added to the row item list
            if self.data[rowFile][0] == 'Subframe Scale':
                subframeScale = str(self.data[rowFile][1])

            if self.data[rowFile][0] == 'Camera Gain':
                cameraGain = str(self.data[rowFile][1])

            if self.data[rowFile][0] == 'Camera Resolution':
                cameraResolution = str(self.data[rowFile][1])

            if self.data[rowFile][0] == 'Scale Unit':
                scaleUnit = str(self.data[rowFile][1])

            if self.data[rowFile][0] == 'Data Unit':
                dataUnit = str(self.data[rowFile][1])

            if self.data[rowFile][0].isnumeric():
                rowPosition = self.mainW.ui.tableWidgetData.rowCount()
                self.mainW.ui.tableWidgetData.insertRow(rowPosition)

                csvRow.insert(0, subframeScale)
                csvRow.insert(1, cameraGain)
                csvRow.insert(2, cameraResolution)
                csvRow.insert(3, scaleUnit)
                csvRow.insert(4, dataUnit)

                # Items (columns) for each row
                for item in csvRow:
                    if str(colFile) in csvList:

                        oneitem = QTableWidgetItem(item)
                        self.mainW.ui.tableWidgetData.setItem(
                            rowTable, colTable, oneitem)

                        # Check if the file (hash) exists in the database
                        if colFile == 8:
                            hashItem = self.hashFile(item)
                            sqlStatement = "SELECT hash FROM images where hash = '"+hashItem+"'"

                            r = self.app.db.exec(sqlStatement)
                            r.next()
                            if r.value(0):
                                color = QtGui.QColor('green')
                                oneitem = QTableWidgetItem(hashItem)
                            else:
                                color = QtGui.QColor('red')
                                oneitem = QTableWidgetItem(hashItem)

                            self.mainW.ui.tableWidgetData.setItem(
                                rowTable, colTable, oneitem)
                            self.mainW.ui.tableWidgetData.item(
                                rowTable, colTable).setBackground(color)

                        colTable += 1
                    colFile += 1

                # increase row counters
                rowTable += 1
            rowFile += 1

    def loadCSVDialog(self):
        fname = QFileDialog.getOpenFileName(
            self.mainW, 'Open CSV', os.getenv('HOME'), 'CSV(*.csv)')
        with open(fname[0], newline='') as csv_file:
            data = csv.reader(csv_file, delimiter=',', quotechar='"')
            self.importCSV(list(data))

    def select_file(self):
        filename, _ = QFileDialog.getOpenFileName(
            self.mainW,
            'Select a CSV file to open…',
            QtCore.QDir.homePath(),
            'CSV Files (*.csv) ;; All Files (*)'
        )
        if filename:
            self.model = CsvTableModel(filename)
            #self.model.deleteCol(1, 3, None)
            self.model.removeColumnd(1, None)
            self.mainW.ui.tableViewImport.setModel(self.model)
            self.mainW.ui.tableViewImport.setSortingEnabled(True)
            # self.mainW.ui.tableViewImport.hideColumn(0)  # Hide ID
            # self.mainW.ui.tableViewImport.hideColumn(1)  # Hide ID

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
