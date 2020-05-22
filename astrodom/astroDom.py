# -----------------------------------------------------------
# Astronomy Domine:
#
# (C) 2020 Ferrante Enriques, ferrante.enriques@gmail.com
# Released under MIT License
# -----------------------------------------------------------

import sys
import os
import json
import logging
import codecs
from PyQt5 import QtSql
from PyQt5.QtCore import QSettings
from datetime import date

from .mainWindow import *

"""
AstroDom application class. It inizializes logs,
sets up database connection, reads config files,
eventually creates a new db, defines some useful
methods and calls the mainWindow GUI. In children
classes it is referenced as 'app'.
"""


class AstroDom:
    astrodomDir = os.getcwd()
    directory = os.path.dirname(__file__)
    with open(os.path.join(directory, "config", "config.json"), "r") as config:
        config = json.load(config)

    logDir = os.path.join(directory, "logs")
    if not os.path.exists(logDir):
        os.makedirs(logDir)

    logging.basicConfig(
        filename=os.path.join(logDir, str(date.today()) + ".log"),
        level=config["debug"],
        datefmt="%Y-%m-%d %H:%M:%S",
        format="%(asctime)s %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)

    def __init__(self):

        # Read configurations from json file
        profileFile = "profile-" + self.config["profile"] + ".json"
        with open(
            os.path.join(self.directory, "config", profileFile), "r"
        ) as configFields:
            self.conf = json.load(configFields)
            self.logger.debug("Read Config Fits File " + str(configFields))

        with open(
            os.path.join(self.directory, "config", "configFilters.json"), "r"
        ) as configFileFilters:
            self.confFilters = json.load(configFileFilters)
            self.logger.debug("Read Config Filters File " +
                              str(configFileFilters))

        self.settings = QSettings("fenriques", "AstroDom")

        # For hashing files
        self.BLOCKSIZE = 1024768

        self.DBDRIVER = "QSQLITE"
        self.COLORS = {
            logging.DEBUG: "black",
            logging.INFO: "#4af",
            logging.WARNING: "orange",
            logging.ERROR: "red",
            logging.CRITICAL: "purple",
        }
        self.version = self.get_version("__init__.py")
        # Create db connection
        if not self.createConnection():
            QMessageBox.about(None, "Message", "Cannot connect to database.")
            exit(0)
        self.setUpDbStructure()
        self.mainWindow = MainWindow(self)

    # Mainly used to extract a list from configurations
    def filterDictToList(self, filter, returnDifferentParameter=None):
        returnList = []
        for key, dictInfo in self.conf.items():
            for subKey in dictInfo:
                if subKey == filter and dictInfo[subKey] != "":
                    if returnDifferentParameter:
                        if returnDifferentParameter == "keys":
                            returnList.append(key)
                        else:
                            returnList.append(
                                dictInfo[returnDifferentParameter])
                    else:
                        returnList.append(dictInfo[subKey])
        return returnList

    def createConnection(self):
        # If there's no database, create one.
        if len(self.config["dbname"]) == 0:
            dbName, ok = DbDialog.getDataBaseName()
            if not ok or len(dbName) == 0:
                return False
            self.config["dbname"] = dbName
            with open(
                os.path.join(self.directory, "config", "config.json"), "w"
            ) as outfile3:
                json.dump(self.config, outfile3)
                self.logger.debug(self.config)

        # Establish connection
        self.logger.info("Set up db connection " + self.DBDRIVER)
        self.db = QtSql.QSqlDatabase.addDatabase(self.DBDRIVER)
        self.db.setDatabaseName(
            os.path.join(self.directory, "config",
                         self.config["dbname"] + ".db")
        )
        if not self.db.open():
            self.logger.critical("Failed to set up db connection")
            return False
        return True

    # the database structure is stored in a json config file
    def setUpDbStructure(self):
        separator = ","
        sqlString = separator.join(self.filterDictToList("fieldType"))
        tableCreate = (
            "CREATE TABLE IF NOT EXISTS 'images' ("
            + "[imageId] INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,"
            + sqlString
            + ")"
        )
        self.logger.debug("Try to create table: " + tableCreate)
        ret = self.db.exec(tableCreate)
        if ret.lastError().number():
            self.logger.error(ret.lastError().number())
            self.logger.error(ret.lastError().text())

        self.logger.debug("Try to create index")
        ret = self.db.exec(
            "CREATE UNIQUE INDEX idx_images_hash ON images (hash);")
        if ret.lastError().text():
            self.logger.warning(str(ret.lastError().text()))

        self.logger.info("DB setup complete")

    def read(self, rel_path):
        here = os.path.abspath(os.path.dirname(__file__))
        with codecs.open(os.path.join(here, rel_path), "r") as fp:
            return fp.read()

    def get_version(self, rel_path):
        for line in self.read(rel_path).splitlines():
            if line.startswith("__version__"):
                # __version__ = "0.9"
                delim = '"' if '"' in line else "'"
                return line.split(delim)[1]
        else:
            raise RuntimeError("Unable to find version string.")


class DbDialog(QDialog):
    def __init__(self, parent=None):
        super(DbDialog, self).__init__(parent)

        layout = QVBoxLayout(self)
        self.setWindowTitle("Message")
        self.labelMsg = QLabel()
        self.labelMsg.setText(
            "Please choose a name for the storage.\nFor example 'MyAstroImages', 'Images6-2020', 'IC434' ")
        layout.addWidget(self.labelMsg)
        self.lineEditDbName = QLineEdit()
        layout.addWidget(self.lineEditDbName)

        # OK and Cancel buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    # get current date and time from the dialog
    def dbName(self):
        return self.lineEditDbName.text()

    # static method to create the dialog and return (date, time, accepted)
    @staticmethod
    def getDataBaseName(parent=None):
        dialog = DbDialog(parent)
        result = dialog.exec_()
        dbName = dialog.dbName()
        return (dbName, result == QDialog.Accepted)
