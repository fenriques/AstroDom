import sys
import os
import csv
import hashlib
import ntpath
import logging
import re

from pathlib import Path
from os.path import expanduser
from astropy.io import fits
from .astropyCalc import AstropyCalc
from PyQt5 import QtWidgets
from PyQt5 import QtSql, QtGui, QtCore
from datetime import datetime

from .importTableModel import *

"""
This class manages imports: first step is to import
FITS files and their headers scanning dirs. Then we
can add information like FWHM, noise etc importing
a CSV file as the output from SubFrameSelector from
Pixinsight. There are read and save method for both
operations (FITS import and CSV import).
The models (both FITS and CSV) are managed by 
ImportTableModel.
"""


class ImportFitsTab:
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

    # Slot used by ImportDir parser class
    def addResultsToModel(self, row):
        self._data.append(row)
        self.model.layoutChanged.emit()

    # Slot for printing log message in the main thread
    def printLogMessage(self, msg, record):
        color = self.app.COLORS.get(record.levelno, "black")
        s = '<pre><font color="%s">%s</font></pre>' % (color, msg)
        self.mainW.ui.plainTextEditLogFits.appendHtml(s)

    # Directory parser (main thread)
    def importFitsDir(self):

        # Choose dir and filter .fits files
        input_dir = QtWidgets.QFileDialog.getExistingDirectory(
            None, "Select a folder:", expanduser("~")
        )
        fileList = list(Path(input_dir).rglob("*.[Ff][Ii][Tt]*"))

        self.mainW.ui.lineEditFitsDir.setText(input_dir)
        self.mainW.importDir.set_file(fileList)
        self._headers = self.app.filterDictToList("fitsHeader", "description")
        self._data = []

        # Populate tableview
        self.model = ImportTableModel(self._data, self._headers)
        self.mainW.ui.tableViewImportFits.setSortingEnabled(True)
        self.mainW.ui.tableViewImportFits.setAlternatingRowColors(True)
        self.mainW.ui.tableViewImportFits.setModel(self.model)

    def deleteRows(self):
        selected = self.mainW.ui.tableViewImportFits.selectedIndexes()
        if selected:
            self.model.removeRows(selected[0].row(), 1, None)

    # Saves each row in the tableview into the database
    def saveFits(self):

        separator = ","
        fieldInsert = self.app.filterDictToList("fitsHeader", "keys")
        fitsDefault = self.app.filterDictToList("fitsDefault", "keys")
        sqlInsert = separator.join(fieldInsert)

        rows = self.model.rowCount(self.mainW.ui.tableViewImportFits.rootIndex())
        targetOverride = self.mainW.ui.lineEditOverrideTarget.text()
        self.logger.info(f"Start saving {rows} files")
        for row in range(rows):
            emptyCellCheck = True
            query = "INSERT INTO images ( " + sqlInsert + ") VALUES("

            for col, val in enumerate(fieldInsert):
                currentIndex = self.model.index(row, col)
                item = self.model.data(currentIndex, QtCore.Qt.DisplayRole)
                if len(str(item)) > 0:
                    # Override target name if asked to
                    if col == 2 and targetOverride:
                        item = targetOverride
                        self.model.setData(
                            self.model.index(row, col), item, QtCore.Qt.EditRole
                        )
                    query += "'" + str(item) + "',"
                    if col == 0:
                        fileName = str(item)
                else:
                    # if no value is read in FIT header try default value
                    if val in fitsDefault:
                        self.logger.error(
                            "Should not be in here because default values are already set"
                        )
                        item = self.app.conf[val]["fitsDefault"]
                        query += "'" + str(item) + "',"
                    else:
                        emptyCellCheck = False

            if emptyCellCheck == False:
                self.logger.error(f"File not inserted: {fileName}")
                continue
            query = query[:-1]
            query += ");"
            try:
                ret = self.app.db.exec(query)
                if ret.lastError().number() == 19:
                    self.model.setData(
                        self.model.index(row, 1),
                        "Error: FITS file already exists in database",
                        QtCore.Qt.EditRole,
                    )
                    error = ret.lastError().text()
                    self.logger.error(f"{error}")
                    self.logger.error(f"{query}")
                elif ret.lastError().number() > 0:
                    error = ret.lastError().text()
                    self.logger.error(f"{error}")
                    self.logger.error(f"{query}")
                else:
                    self.model.setData(
                        self.model.index(row, 1),
                        "OK: FITS file saved",
                        QtCore.Qt.EditRole,
                    )
                    self.logger.info(f"Saved file {fileName}")
                    self.logger.debug(f"FITS file saved with query {query}")

            except Exception as e:
                self.logger.error(f"Insert error {e}")

            self.model.layoutChanged.emit()
        self.logger.info(f"Saving completed")
        # Force image list reload data
        self.mainW.imageSourceModel.select()
        while self.mainW.imageSourceModel.canFetchMore():
            self.mainW.imageSourceModel.fetchMore()
        self.mainW.filterRegExpChanged()


"""
ImportDir is the thread reading FITS files. Should be
moved to a separate files but is kept here just for
convenience. Thread is created in mainWindow.py
"""


class ImportDir(QtCore.QObject):
    logger = logging.getLogger(__name__)

    # notifies main thread when a full row is read
    match_found = QtCore.pyqtSignal(list)
    # notifies when import finished
    finished = QtCore.pyqtSignal()

    def __init__(self, app):
        super().__init__()
        self.app = app

    def set_file(self, fileList):
        self.fileList = fileList

    @qtc.pyqtSlot()
    def worker(self):
        self._worker(self.fileList)
        self.finished.emit()

    def _worker(self, fileList):

        dbFitsParameters = {}
        fitsKeyList = self.app.filterDictToList("fitsHeader", "keys")
        fitsDefault = self.app.filterDictToList("fitsDefault", "keys")

        for i, f in enumerate(fileList):
            self.logger.info(f"{i+1}-Start reading file {f}")
            row = []

            # Parse FITS header for given file
            fitsFileParameters = self.parseFitsHeader(f)

            # Create a row with all requested fits header values from file
            for dbFitsParameters in fitsKeyList:
                oneitem = str(
                    fitsFileParameters[self.app.conf[dbFitsParameters]["fitsHeader"]]
                )
                row.insert(self.app.conf[dbFitsParameters]["order"], oneitem)

            # Then some values in the row are added or overwritten
            row[fitsKeyList.index("file")] = str(f)
            row[fitsKeyList.index("hash")] = self.hashFile(f)

            # RA/DEC coord conversion
            AstropyCalcObj = AstropyCalc(self.app)
            c = AstropyCalcObj.coordConversion(
                row[fitsKeyList.index("ra")], row[fitsKeyList.index("dec")]
            )
            if c:
                row[fitsKeyList.index("ra")] = str(round(c.ra.degree, 3))
                row[fitsKeyList.index("dec")] = str(round(c.dec.degree, 3))

            # Strip subseconds
            dateobs = row[fitsKeyList.index("date")]
            dateobs = dateobs.split(".")[0]
            row[fitsKeyList.index("date")] = dateobs

            # Calculate Alt, Az coordinates
            strAlt = "0"
            strAz = "0"

            s = AstropyCalcObj.longLatConversion(
                row[fitsKeyList.index("sitelong")], row[fitsKeyList.index("sitelat")]
            )
            if s:
                row[fitsKeyList.index("sitelong")] = str(round(s.ra.degree, 3))
                row[fitsKeyList.index("sitelat")] = str(round(s.dec.degree, 3))
                altAz = AstropyCalcObj.getAltAzCoord(
                    c.ra.degree,
                    c.dec.degree,
                    row[fitsKeyList.index("date")],
                    s.ra.degree,
                    s.dec.degree,
                )
                if altAz:
                    strAlt = str("{0.alt:.4f}".format(altAz))[:-4]
                    strAz = str("{0.az:.4f}".format(altAz))[:-4]

            row[fitsKeyList.index("alt")] = strAlt
            row[fitsKeyList.index("az")] = strAz

            # if no value is read in FIT header try default value
            for keyD, valD in enumerate(fitsDefault):

                if len(row[fitsKeyList.index(valD)]) == 0:
                    defaultValue = self.app.conf[valD]["fitsDefault"]
                    defaultField = self.app.conf[valD]["description"]
                    self.logger.warning(
                        f"Inserted default value {defaultValue} for {defaultField} keyword"
                    )
                    row[fitsKeyList.index(valD)] = defaultValue

            # check for null value that prevents db insert
            for k, v in enumerate(row):
                if not v:
                    self.logger.error(
                        f"Null value for {fitsKeyList[k]} keyword: in Settings "
                        "fix keyword name or set a default value else the file "
                        "cannot be inserted into the database"
                    )

            self.logger.debug(row)
            self.logger.info(f"{i+1}-End reading file {f}")
            self.match_found.emit(row)

    def parseFitsHeader(self, fitsFile):
        returnParameter = {}
        hdu = fits.open(fitsFile)
        hdu.verify("silentfix")
        hdr = hdu[0].header
        for param in self.app.filterDictToList("fitsHeader"):
            if param in hdr:
                returnParameter[param] = hdr[param]
            else:
                returnParameter[param] = ""
        return returnParameter

    def hashFile(self, fileName):
        with open(fileName, "rb") as afile:
            hasher = hashlib.md5()
            buf = afile.read(self.app.BLOCKSIZE)
            for i in range(5):
                hasher.update(buf)
                buf = afile.read(self.app.BLOCKSIZE)
        hash = hasher.hexdigest()
        return hash


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
