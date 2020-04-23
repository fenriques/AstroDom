import sys
import os
import json
import logging
from PyQt5.QtWidgets import QTableWidgetItem, QFileDialog, QMessageBox
from PyQt5 import QtSql, QtGui


class SettingsTab():
    logger = logging.getLogger(__name__)

    def __init__(self, mainW, app):
        super().__init__()
        self.mainW = mainW
        self.app = app

        self.mainW.ui.pushButtonSaveSettings.clicked.connect(self.saveSettings)
        # FITS Headers keywords
        self.mainW.ui.lineEditFitsFile.setText(
            self.app.conf['file']['fitsHeader'])
        self.mainW.ui.lineEditFitsTarget.setText(
            self.app.conf['target']['fitsHeader'])
        self.mainW.ui.lineEditFitsFrame.setText(
            self.app.conf['frame']['fitsHeader'])
        self.mainW.ui.lineEditFitsFilter.setText(
            self.app.conf['filter']['fitsHeader'])
        self.mainW.ui.lineEditFitsExposure.setText(
            self.app.conf['exposure']['fitsHeader'])
        self.mainW.ui.lineEditFitsTemp.setText(
            self.app.conf['temp']['fitsHeader'])
        self.mainW.ui.lineEditFitsXbinning.setText(
            self.app.conf['xbinning']['fitsHeader'])
        self.mainW.ui.lineEditFitsYbinning.setText(
            self.app.conf['ybinning']['fitsHeader'])
        self.mainW.ui.lineEditFitsSitelat.setText(
            self.app.conf['sitelat']['fitsHeader'])
        self.mainW.ui.lineEditFitsSitelong.setText(
            self.app.conf['sitelong']['fitsHeader'])
        self.mainW.ui.lineEditFitsRa.setText(
            self.app.conf['ra']['fitsHeader'])
        self.mainW.ui.lineEditFitsDec.setText(
            self.app.conf['dec']['fitsHeader'])
        self.mainW.ui.lineEditFitsDate.setText(
            self.app.conf['date']['fitsHeader'])
        self.mainW.ui.lineEditFitsGain.setText(
            self.app.conf['gain']['fitsHeader'])
        self.mainW.ui.lineEditFitsOffset.setText(
            self.app.conf['offset']['fitsHeader'])
        # FITS header defaults
        self.mainW.ui.lineEditFitsFileDefault.setText(
            self.app.conf['file']['fitsDefault'])
        self.mainW.ui.lineEditFitsTargetDefault.setText(
            self.app.conf['target']['fitsDefault'])
        self.mainW.ui.lineEditFitsFrameDefault.setText(
            self.app.conf['frame']['fitsDefault'])
        self.mainW.ui.lineEditFitsFilterDefault.setText(
            self.app.conf['filter']['fitsDefault'])
        self.mainW.ui.lineEditFitsExposureDefault.setText(
            self.app.conf['exposure']['fitsDefault'])
        self.mainW.ui.lineEditFitsTempDefault.setText(
            self.app.conf['temp']['fitsDefault'])
        self.mainW.ui.lineEditFitsXbinningDefault.setText(
            self.app.conf['xbinning']['fitsDefault'])
        self.mainW.ui.lineEditFitsYbinningDefault.setText(
            self.app.conf['ybinning']['fitsDefault'])
        self.mainW.ui.lineEditFitsSitelatDefault.setText(
            self.app.conf['sitelat']['fitsDefault'])
        self.mainW.ui.lineEditFitsSitelongDefault.setText(
            self.app.conf['sitelong']['fitsDefault'])
        self.mainW.ui.lineEditFitsRaDefault.setText(
            self.app.conf['ra']['fitsDefault'])
        self.mainW.ui.lineEditFitsDecDefault.setText(
            self.app.conf['dec']['fitsDefault'])
        self.mainW.ui.lineEditFitsDateDefault.setText(
            self.app.conf['date']['fitsDefault'])
        self.mainW.ui.lineEditFitsGainDefault.setText(
            self.app.conf['gain']['fitsDefault'])
        self.mainW.ui.lineEditFitsOffsetDefault.setText(
            self.app.conf['offset']['fitsDefault'])
        # Filters Keywords
        self.mainW.ui.lineEditFilterL.setText(
            ','.join(self.app.confFilters['L']))
        self.mainW.ui.lineEditFilterR.setText(
            ','.join(self.app.confFilters['R']))
        self.mainW.ui.lineEditFilterG.setText(
            ','.join(self.app.confFilters['G']))
        self.mainW.ui.lineEditFilterB.setText(
            ','.join(self.app.confFilters['B']))
        self.mainW.ui.lineEditFilterHa.setText(
            ','.join(self.app.confFilters['Ha']))
        self.mainW.ui.lineEditFilterSii.setText(
            ','.join(self.app.confFilters['Sii']))
        self.mainW.ui.lineEditFilterOiii.setText(
            ','.join(self.app.confFilters['Oiii']))
        self.mainW.ui.lineEditFilterLpr.setText(
            ','.join(self.app.confFilters['LPR']))

        # Other settings
        self.mainW.ui.lineEditDbname.setText(self.app.config['dbname'])
        self.mainW.ui.comboBoxDebug.setItemText(10, "DEBUG")
        self.mainW.ui.comboBoxDebug.setCurrentText(
            self.app.config['debug'])

    def saveSettings(self):
        self.app.conf['file']['fitsHeader'] = self.mainW.ui.lineEditFitsFile.text()
        self.app.conf['target']['fitsHeader'] = self.mainW.ui.lineEditFitsTarget.text()
        self.app.conf['frame']['fitsHeader'] = self.mainW.ui.lineEditFitsFrame.text()
        self.app.conf['filter']['fitsHeader'] = self.mainW.ui.lineEditFitsFilter.text()
        self.app.conf['exposure']['fitsHeader'] = self.mainW.ui.lineEditFitsExposure.text()
        self.app.conf['temp']['fitsHeader'] = self.mainW.ui.lineEditFitsTemp.text()
        self.app.conf['xbinning']['fitsHeader'] = self.mainW.ui.lineEditFitsXbinning.text()
        self.app.conf['ybinning']['fitsHeader'] = self.mainW.ui.lineEditFitsYbinning.text()
        self.app.conf['sitelat']['fitsHeader'] = self.mainW.ui.lineEditFitsSitelat.text()
        self.app.conf['sitelong']['fitsHeader'] = self.mainW.ui.lineEditFitsSitelong.text()
        self.app.conf['ra']['fitsHeader'] = self.mainW.ui.lineEditFitsRa.text()
        self.app.conf['dec']['fitsHeader'] = self.mainW.ui.lineEditFitsDec.text()
        self.app.conf['date']['fitsHeader'] = self.mainW.ui.lineEditFitsDate.text()
        self.app.conf['gain']['fitsHeader'] = self.mainW.ui.lineEditFitsGain.text()
        self.app.conf['offset']['fitsHeader'] = self.mainW.ui.lineEditFitsOffset.text()

        self.app.conf['file']['fitsDefault'] = self.mainW.ui.lineEditFitsFileDefault.text()
        self.app.conf['target']['fitsDefault'] = self.mainW.ui.lineEditFitsTargetDefault.text()
        self.app.conf['frame']['fitsDefault'] = self.mainW.ui.lineEditFitsFrameDefault.text()
        self.app.conf['filter']['fitsDefault'] = self.mainW.ui.lineEditFitsFilterDefault.text()
        self.app.conf['exposure']['fitsDefault'] = self.mainW.ui.lineEditFitsExposureDefault.text()
        self.app.conf['temp']['fitsDefault'] = self.mainW.ui.lineEditFitsTempDefault.text()
        self.app.conf['xbinning']['fitsDefault'] = self.mainW.ui.lineEditFitsXbinningDefault.text()
        self.app.conf['ybinning']['fitsDefault'] = self.mainW.ui.lineEditFitsYbinningDefault.text()
        self.app.conf['sitelat']['fitsDefault'] = self.mainW.ui.lineEditFitsSitelatDefault.text()
        self.app.conf['sitelong']['fitsDefault'] = self.mainW.ui.lineEditFitsSitelongDefault.text()
        self.app.conf['ra']['fitsDefault'] = self.mainW.ui.lineEditFitsRaDefault.text()
        self.app.conf['dec']['fitsDefault'] = self.mainW.ui.lineEditFitsDecDefault.text()
        self.app.conf['date']['fitsDefault'] = self.mainW.ui.lineEditFitsDateDefault.text()
        self.app.conf['gain']['fitsDefault'] = self.mainW.ui.lineEditFitsGainDefault.text()
        self.app.conf['offset']['fitsDefault'] = self.mainW.ui.lineEditFitsOffsetDefault.text()

        with open(os.path.join(self.app.directory, 'config', 'configFields.json'), 'w') as outfile:
            json.dump(self.app.conf, outfile)
            self.logger.debug(self.app.conf)

        self.app.confFilters['L'] = self.mainW.ui.lineEditFilterL.text().split(
            ',')
        self.app.confFilters['R'] = self.mainW.ui.lineEditFilterR.text().split(
            ',')
        self.app.confFilters['G'] = self.mainW.ui.lineEditFilterG.text().split(
            ',')
        self.app.confFilters['B'] = self.mainW.ui.lineEditFilterB.text().split(
            ',')
        self.app.confFilters['Ha'] = self.mainW.ui.lineEditFilterHa.text().split(
            ',')
        self.app.confFilters['Sii'] = self.mainW.ui.lineEditFilterSii.text().split(
            ',')
        self.app.confFilters['Oiii'] = self.mainW.ui.lineEditFilterOiii.text().split(
            ',')
        self.app.confFilters['LPR'] = self.mainW.ui.lineEditFilterLpr.text().split(
            ',')
        with open(os.path.join(self.app.directory, 'config', 'configFilters.json'), 'w') as outfile2:
            json.dump(self.app.confFilters, outfile2)
            self.logger.debug(self.app.confFilters)

        self.app.config['dbname'] = self.mainW.ui.lineEditDbname.text()
        self.app.config['debug'] = self.mainW.ui.comboBoxDebug.currentText()
        with open(os.path.join(self.app.directory, 'config', 'config.json'), 'w') as outfile3:
            json.dump(self.app.config, outfile3)
            self.logger.debug(self.app.config)

        QMessageBox.about(
            None, "Message", "Configuration saved. Please close and restart AstroDom")
