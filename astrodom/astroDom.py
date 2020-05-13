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
            self.logger.debug("Read Config Filters File " + str(configFileFilters))

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
        self.setUpDb()
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
                            returnList.append(dictInfo[returnDifferentParameter])
                    else:
                        returnList.append(dictInfo[subKey])
        return returnList

    def createConnection(self):
        self.logger.info("Set up db connection " + self.DBDRIVER)

        self.db = QtSql.QSqlDatabase.addDatabase(self.DBDRIVER)
        self.db.setDatabaseName(
            os.path.join(self.directory, "config", self.config["dbname"] + ".db")
        )
        if not self.db.open():
            self.logger.critical("Failed to set up db connection")
            return False
        return True

    # the database structure is stored in a json config file
    def setUpDb(self):
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
        ret = self.db.exec("CREATE UNIQUE INDEX idx_images_hash ON images (hash);")
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
