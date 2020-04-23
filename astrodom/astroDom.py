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
from PyQt5 import QtSql
from datetime import date

from .mainWindow import *


class AstroDom():
    directory = os.path.dirname(__file__)
    with open(os.path.join(directory, 'config', 'config.json'), 'r') as config:
        config = json.load(config)
   
    logDir = os.path.join(directory, 'logs')
    if not os.path.exists(logDir):
        os.makedirs(logDir)
    
    logging.basicConfig(
        filename = os.path.join(logDir, str(date.today())+'.log'),
        level=config['debug'],
        datefmt='%Y-%m-%d %H:%M:%S',
        format='%(asctime)s %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    def __init__(self):

        # Read configuration from json file
        with open(os.path.join(self.directory, 'config', 'configFields.json'), 'r') as configFields:
            self.conf = json.load(configFields)
            self.logger.debug('Read Config Fits File '+str(configFields))
            
        with open(os.path.join(self.directory, 'config', 'configFilters.json'), 'r') as configFileFilters:
            self.confFilters = json.load(configFileFilters)
            self.logger.debug('Read Config Filters File ' +
                              str(configFileFilters))

        self.BLOCKSIZE = 1024768
        self.DBDRIVER = "QSQLITE"
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
        self.logger.info('Set up db connection ' + self.DBDRIVER)

        self.db = QtSql.QSqlDatabase.addDatabase(self.DBDRIVER)
        self.db.setDatabaseName(os.path.join(
            self.directory, '', self.config["dbname"]+".db"))
        if not self.db.open():
            self.logger.critical('Failed to set up db connection')
            return False
        return True

    def setUpDb(self):
        separator = ','
        sqlString = separator.join(self.filterDictToList('fieldType'))
        tableCreate = "CREATE TABLE IF NOT EXISTS 'images' (" +\
            "[imageId] INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL," +\
            sqlString + ")"
        self.logger.debug('Try to create table: ' + tableCreate)
        ret = self.db.exec(tableCreate)
        if ret.lastError().number():
            self.logger.error(ret.lastError().number())
            self.logger.error(ret.lastError().text())

        self.logger.debug('Try to create index')
        ret = self.db.exec(
            "CREATE UNIQUE INDEX idx_images_hash ON images (hash);")
        if ret.lastError().text():
            self.logger.warning(str(ret.lastError().text()))

        self.logger.info('DB setup complete')
