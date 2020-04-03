# -----------------------------------------------------------
# Astronomy Domine:
#
# (C) 2020 Ferrante Enriques, ferrante.enriques@gmail.com
# Released under GNU Public License (GPL)
# -----------------------------------------------------------

import sys
import os
import json
from PyQt5 import QtSql

from .mainWindow import *


class astroDom():

    def __init__(self):
        self.directory = os.path.dirname(__file__)

        # Read configuration from json file
        with open(os.path.join(self.directory, 'config', 'config.json'), 'r') as configFile:
            self.conf = json.load(configFile)
        with open(os.path.join(self.directory, 'config', 'configFilters.json'), 'r') as configFileFilters:
            self.confFilters = json.load(configFileFilters)
        with open(os.path.join(self.directory, 'config', 'configDb.json'), 'r') as configDb:
            self.confDb = json.load(configDb)

        self.BLOCKSIZE = 1024768
        # Create db connection
        if not self.createConnection():
            sys.exit(-1)

        self.setUpDb()
        self.mainWindow = MainWindow(self)

    def filterDictToList(self, filter, returnDifferentParameter=None):
        returnList = []
        for key, dictInfo in self.conf.items():
            for subKey in dictInfo:
                if subKey == filter and dictInfo[subKey] != '':
                    if returnDifferentParameter:
                        if returnDifferentParameter == 'keys':
                            returnList.append(key)
                        else:
                            returnList.append(
                                dictInfo[returnDifferentParameter])
                    else:
                        returnList.append(dictInfo[subKey])
        return returnList

    def createConnection(self):
        self.db = QtSql.QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName(os.path.join(
            self.directory, '', self.confDb["dbname"]+".db"))
        if not self.db.open():
            QtWidgets.QMessageBox.critical(
                None,
                QtWidgets.qApp.tr("Cannot open database"),
                QtWidgets.qApp.tr(
                    "Unable to establish a database connection.\n"
                    "Click Cancel to exit."
                ),
                QtWidgets.QMessageBox.Cancel,
            )
            return False
        return True

    def setUpDb(self):
        separator = ','
        sqlString = separator.join(self.filterDictToList('fieldType'))
        tableCreate = "CREATE TABLE IF NOT EXISTS 'images' (" +\
            "[imageId] INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL," +\
            sqlString + ")"
        self.db.exec(tableCreate)
        self.db.exec("CREATE UNIQUE INDEX idx_images_hash ON images (hash);")
