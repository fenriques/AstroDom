import sys
import os
import json
import logging
import ntpath
import glob
from PyQt5.QtWidgets import QTableWidgetItem, QFileDialog, QMessageBox
from PyQt5 import QtSql, QtGui, QtCore
from PyQt5.QtCore import QByteArray


"""
Application settings are stored in 3 json files. 
- configFields.json stores FITS keyword that users can
customize. Moreover an optional default value allows
users to fill FITS header that are missing.
- configFilters: filter keyword could be stored in FITS
header with different names. In order to match them all,
a list of comma separated value is allowed
- config.json: additional AstroDom configuration
"""


class SettingsTab:
    logger = logging.getLogger(__name__)

    def selectionchange(self, currentProfile):
        self.setProfile(currentProfile)

    def setProfile(self, currentProfile):
        # open config-profile
        profileFile = "profile-" + currentProfile + ".json"
        with open(os.path.join("astrodom/config", profileFile), "r") as configFields:
            self.cProfile = json.load(configFields)
            self.logger.debug("Read Config Fits File " + str(configFields))

        # Profile name
        self.mainW.ui.lineEditProfileName.setText(currentProfile)

        # FITS Headers keywords
        self.mainW.ui.lineEditFitsFile.setText(self.cProfile["file"]["fitsHeader"])
        self.mainW.ui.lineEditFitsTarget.setText(self.cProfile["target"]["fitsHeader"])
        self.mainW.ui.lineEditFitsFrame.setText(self.cProfile["frame"]["fitsHeader"])
        self.mainW.ui.lineEditFitsFilter.setText(self.cProfile["filter"]["fitsHeader"])
        self.mainW.ui.lineEditFitsExposure.setText(
            self.cProfile["exposure"]["fitsHeader"]
        )
        self.mainW.ui.lineEditFitsTemp.setText(self.cProfile["temp"]["fitsHeader"])
        self.mainW.ui.lineEditFitsXbinning.setText(
            self.cProfile["xbinning"]["fitsHeader"]
        )
        self.mainW.ui.lineEditFitsYbinning.setText(
            self.cProfile["ybinning"]["fitsHeader"]
        )
        self.mainW.ui.lineEditFitsSitelat.setText(
            self.cProfile["sitelat"]["fitsHeader"]
        )
        self.mainW.ui.lineEditFitsSitelong.setText(
            self.cProfile["sitelong"]["fitsHeader"]
        )
        self.mainW.ui.lineEditFitsRa.setText(self.cProfile["ra"]["fitsHeader"])
        self.mainW.ui.lineEditFitsDec.setText(self.cProfile["dec"]["fitsHeader"])
        self.mainW.ui.lineEditFitsDate.setText(self.cProfile["date"]["fitsHeader"])
        self.mainW.ui.lineEditFitsGain.setText(self.cProfile["gain"]["fitsHeader"])
        self.mainW.ui.lineEditFitsOffset.setText(self.cProfile["offset"]["fitsHeader"])

        # FITS header defaults
        self.mainW.ui.lineEditFitsFileDefault.setText(
            self.cProfile["file"]["fitsDefault"]
        )
        self.mainW.ui.lineEditFitsTargetDefault.setText(
            self.cProfile["target"]["fitsDefault"]
        )
        self.mainW.ui.lineEditFitsFrameDefault.setText(
            self.cProfile["frame"]["fitsDefault"]
        )
        self.mainW.ui.lineEditFitsFilterDefault.setText(
            self.cProfile["filter"]["fitsDefault"]
        )
        self.mainW.ui.lineEditFitsExposureDefault.setText(
            self.cProfile["exposure"]["fitsDefault"]
        )
        self.mainW.ui.lineEditFitsTempDefault.setText(
            self.cProfile["temp"]["fitsDefault"]
        )
        self.mainW.ui.lineEditFitsXbinningDefault.setText(
            self.cProfile["xbinning"]["fitsDefault"]
        )
        self.mainW.ui.lineEditFitsYbinningDefault.setText(
            self.cProfile["ybinning"]["fitsDefault"]
        )
        self.mainW.ui.lineEditFitsSitelatDefault.setText(
            self.cProfile["sitelat"]["fitsDefault"]
        )
        self.mainW.ui.lineEditFitsSitelongDefault.setText(
            self.cProfile["sitelong"]["fitsDefault"]
        )
        self.mainW.ui.lineEditFitsRaDefault.setText(self.cProfile["ra"]["fitsDefault"])
        self.mainW.ui.lineEditFitsDecDefault.setText(
            self.cProfile["dec"]["fitsDefault"]
        )
        self.mainW.ui.lineEditFitsDateDefault.setText(
            self.cProfile["date"]["fitsDefault"]
        )
        self.mainW.ui.lineEditFitsGainDefault.setText(
            self.cProfile["gain"]["fitsDefault"]
        )
        self.mainW.ui.lineEditFitsOffsetDefault.setText(
            self.cProfile["offset"]["fitsDefault"]
        )
        # Hide
        self.mainW.ui.checkBoxFitsFile.setChecked(bool(self.app.conf["file"]["hide"]))
        self.mainW.ui.checkBoxFitsTarget.setChecked(
            bool(self.app.conf["target"]["hide"])
        )
        self.mainW.ui.checkBoxFitsFrame.setChecked(bool(self.app.conf["frame"]["hide"]))
        self.mainW.ui.checkBoxFitsFilter.setChecked(
            bool(self.app.conf["filter"]["hide"])
        )
        self.mainW.ui.checkBoxFitsExposure.setChecked(
            bool(self.app.conf["exposure"]["hide"])
        )
        self.mainW.ui.checkBoxFitsTemp.setChecked(bool(self.app.conf["temp"]["hide"]))
        self.mainW.ui.checkBoxFitsXbinning.setChecked(
            bool(self.app.conf["xbinning"]["hide"])
        )
        self.mainW.ui.checkBoxFitsYbinning.setChecked(
            bool(self.app.conf["ybinning"]["hide"])
        )
        self.mainW.ui.checkBoxFitsSitelat.setChecked(
            bool(self.app.conf["sitelat"]["hide"])
        )
        self.mainW.ui.checkBoxFitsSitelong.setChecked(
            bool(self.app.conf["sitelong"]["hide"])
        )
        self.mainW.ui.checkBoxFitsRa.setChecked(bool(self.app.conf["ra"]["hide"]))
        self.mainW.ui.checkBoxFitsDec.setChecked(bool(self.app.conf["dec"]["hide"]))
        self.mainW.ui.checkBoxFitsDate.setChecked(bool(self.app.conf["date"]["hide"]))
        self.mainW.ui.checkBoxFitsGain.setChecked(bool(self.app.conf["gain"]["hide"]))
        self.mainW.ui.checkBoxFitsOffset.setChecked(
            bool(self.app.conf["offset"]["hide"])
        )

        self.mainW.ui.comboBoxCoordFormat.setCurrentText(
            self.cProfile["coordFormat"]["description"]
        )

    def __init__(self, mainW, app):
        super().__init__()
        self.mainW = mainW
        self.app = app

        # load profile
        profileFiles = glob.glob("astrodom/config/profile-*.json")
        for i, f in enumerate(profileFiles):
            f = ntpath.basename(f)
            f = os.path.splitext(f)[0]
            f = f.replace("profile-", "")
            self.mainW.ui.comboBoxProfile.addItem(f, i)

        self.mainW.ui.comboBoxProfile.setCurrentText(self.app.config["profile"])
        self.currentProfile = self.mainW.ui.comboBoxProfile.currentText()
        self.setProfile(self.currentProfile)

        # Filters Keywords
        self.mainW.ui.lineEditFilterL.setText(",".join(self.app.confFilters["L"]))
        self.mainW.ui.lineEditFilterR.setText(",".join(self.app.confFilters["R"]))
        self.mainW.ui.lineEditFilterG.setText(",".join(self.app.confFilters["G"]))
        self.mainW.ui.lineEditFilterB.setText(",".join(self.app.confFilters["B"]))
        self.mainW.ui.lineEditFilterHa.setText(",".join(self.app.confFilters["Ha"]))
        self.mainW.ui.lineEditFilterSii.setText(",".join(self.app.confFilters["Sii"]))
        self.mainW.ui.lineEditFilterOiii.setText(",".join(self.app.confFilters["Oiii"]))
        self.mainW.ui.lineEditFilterLpr.setText(",".join(self.app.confFilters["LPR"]))

        # Config main settings
        self.mainW.ui.lineEditDbname.setText(self.app.config["dbname"])
        self.mainW.ui.comboBoxDebug.setItemText(10, "DEBUG")
        self.mainW.ui.comboBoxDebug.setCurrentText(self.app.config["debug"])

        self.mainW.ui.comboBoxMonthsFilter.setCurrentText(
            self.app.config["monthsFilter"]
        )
        self.mainW.ui.spinBoxDefaultTimeStart.setValue(
            self.app.config["defaultTimeStart"]
        )
        self.mainW.ui.spinBoxDefaultTimeEnd.setValue(self.app.config["defaultTimeEnd"])
        self.mainW.ui.spinBoxPrecision.setValue(self.app.config["precision"])

    def selectDb(self):
        dbName, _ = QFileDialog.getOpenFileName(
            self.mainW,
            "Select a SQLite file to open…",
            os.path.join(self.app.directory, "config"),
            "SQLite Files (*.db) ;; All Files (*)",
        )
        if dbName:
            with open(dbName) as fh:
                dbName = os.path.splitext(ntpath.basename(dbName))[0]
                self.mainW.ui.lineEditDbname.setText(dbName)
                self.logger.info(f"Selected {dbName}")

    def saveProfile(self):

        self.app.conf["file"]["fitsHeader"] = self.mainW.ui.lineEditFitsFile.text()
        self.app.conf["target"]["fitsHeader"] = self.mainW.ui.lineEditFitsTarget.text()
        self.app.conf["frame"]["fitsHeader"] = self.mainW.ui.lineEditFitsFrame.text()
        self.app.conf["filter"]["fitsHeader"] = self.mainW.ui.lineEditFitsFilter.text()
        self.app.conf["exposure"][
            "fitsHeader"
        ] = self.mainW.ui.lineEditFitsExposure.text()
        self.app.conf["temp"]["fitsHeader"] = self.mainW.ui.lineEditFitsTemp.text()
        self.app.conf["xbinning"][
            "fitsHeader"
        ] = self.mainW.ui.lineEditFitsXbinning.text()
        self.app.conf["ybinning"][
            "fitsHeader"
        ] = self.mainW.ui.lineEditFitsYbinning.text()
        self.app.conf["sitelat"][
            "fitsHeader"
        ] = self.mainW.ui.lineEditFitsSitelat.text()
        self.app.conf["sitelong"][
            "fitsHeader"
        ] = self.mainW.ui.lineEditFitsSitelong.text()
        self.app.conf["ra"]["fitsHeader"] = self.mainW.ui.lineEditFitsRa.text()
        self.app.conf["dec"]["fitsHeader"] = self.mainW.ui.lineEditFitsDec.text()
        self.app.conf["date"]["fitsHeader"] = self.mainW.ui.lineEditFitsDate.text()
        self.app.conf["gain"]["fitsHeader"] = self.mainW.ui.lineEditFitsGain.text()
        self.app.conf["offset"]["fitsHeader"] = self.mainW.ui.lineEditFitsOffset.text()

        self.app.conf["file"][
            "fitsDefault"
        ] = self.mainW.ui.lineEditFitsFileDefault.text()
        self.app.conf["target"][
            "fitsDefault"
        ] = self.mainW.ui.lineEditFitsTargetDefault.text()
        self.app.conf["frame"][
            "fitsDefault"
        ] = self.mainW.ui.lineEditFitsFrameDefault.text()
        self.app.conf["filter"][
            "fitsDefault"
        ] = self.mainW.ui.lineEditFitsFilterDefault.text()
        self.app.conf["exposure"][
            "fitsDefault"
        ] = self.mainW.ui.lineEditFitsExposureDefault.text()
        self.app.conf["temp"][
            "fitsDefault"
        ] = self.mainW.ui.lineEditFitsTempDefault.text()
        self.app.conf["xbinning"][
            "fitsDefault"
        ] = self.mainW.ui.lineEditFitsXbinningDefault.text()
        self.app.conf["ybinning"][
            "fitsDefault"
        ] = self.mainW.ui.lineEditFitsYbinningDefault.text()
        self.app.conf["sitelat"][
            "fitsDefault"
        ] = self.mainW.ui.lineEditFitsSitelatDefault.text()
        self.app.conf["sitelong"][
            "fitsDefault"
        ] = self.mainW.ui.lineEditFitsSitelongDefault.text()
        self.app.conf["ra"]["fitsDefault"] = self.mainW.ui.lineEditFitsRaDefault.text()
        self.app.conf["dec"][
            "fitsDefault"
        ] = self.mainW.ui.lineEditFitsDecDefault.text()
        self.app.conf["date"][
            "fitsDefault"
        ] = self.mainW.ui.lineEditFitsDateDefault.text()
        self.app.conf["gain"][
            "fitsDefault"
        ] = self.mainW.ui.lineEditFitsGainDefault.text()
        self.app.conf["offset"][
            "fitsDefault"
        ] = self.mainW.ui.lineEditFitsOffsetDefault.text()

        self.app.conf["coordFormat"][
            "description"
        ] = self.mainW.ui.comboBoxCoordFormat.currentText()
        # CheckBox hide

        self.app.conf["file"]["hide"] = (
            1 if self.mainW.ui.checkBoxFitsFile.isChecked() else 0
        )
        self.app.conf["target"]["hide"] = (
            1 if self.mainW.ui.checkBoxFitsTarget.isChecked() else 0
        )
        self.app.conf["frame"]["hide"] = (
            1 if self.mainW.ui.checkBoxFitsFrame.isChecked() else 0
        )
        self.app.conf["filter"]["hide"] = (
            1 if self.mainW.ui.checkBoxFitsFilter.isChecked() else 0
        )
        self.app.conf["exposure"]["hide"] = (
            1 if self.mainW.ui.checkBoxFitsExposure.isChecked() else 0
        )
        self.app.conf["temp"]["hide"] = (
            1 if self.mainW.ui.checkBoxFitsTemp.isChecked() else 0
        )
        self.app.conf["xbinning"]["hide"] = (
            1 if self.mainW.ui.checkBoxFitsXbinning.isChecked() else 0
        )
        self.app.conf["ybinning"]["hide"] = (
            1 if self.mainW.ui.checkBoxFitsYbinning.isChecked() else 0
        )
        self.app.conf["sitelat"]["hide"] = (
            1 if self.mainW.ui.checkBoxFitsSitelat.isChecked() else 0
        )
        self.app.conf["sitelong"]["hide"] = (
            1 if self.mainW.ui.checkBoxFitsSitelong.isChecked() else 0
        )
        self.app.conf["ra"]["hide"] = (
            1 if self.mainW.ui.checkBoxFitsRa.isChecked() else 0
        )
        self.app.conf["dec"]["hide"] = (
            1 if self.mainW.ui.checkBoxFitsDec.isChecked() else 0
        )
        self.app.conf["date"]["hide"] = (
            1 if self.mainW.ui.checkBoxFitsDate.isChecked() else 0
        )
        self.app.conf["gain"]["hide"] = (
            1 if self.mainW.ui.checkBoxFitsGain.isChecked() else 0
        )
        self.app.conf["offset"]["hide"] = (
            1 if self.mainW.ui.checkBoxFitsOffset.isChecked() else 0
        )

        fileName = self.mainW.ui.lineEditProfileName.text()
        if fileName == "":
            fileName = self.app.conf["profile"]
        fileName = "profile-" + fileName + ".json"
       
        # Clear the tableview state else it prevents hide/show
        # columns set here to work properly.
        self.app.settings.setValue("readStateOnStart","False")

        with open(os.path.join(self.app.directory, "config", fileName), "w") as outfile:
            json.dump(self.app.conf, outfile)
            self.logger.debug(self.app.conf)

        self.saveConfig()

    def saveFilter(self):

        self.app.confFilters["L"] = self.mainW.ui.lineEditFilterL.text().split(",")
        self.app.confFilters["R"] = self.mainW.ui.lineEditFilterR.text().split(",")
        self.app.confFilters["G"] = self.mainW.ui.lineEditFilterG.text().split(",")
        self.app.confFilters["B"] = self.mainW.ui.lineEditFilterB.text().split(",")
        self.app.confFilters["Ha"] = self.mainW.ui.lineEditFilterHa.text().split(",")
        self.app.confFilters["Sii"] = self.mainW.ui.lineEditFilterSii.text().split(",")
        self.app.confFilters["Oiii"] = self.mainW.ui.lineEditFilterOiii.text().split(
            ","
        )
        self.app.confFilters["LPR"] = self.mainW.ui.lineEditFilterLpr.text().split(",")
        with open(
            os.path.join(self.app.directory, "config", "configFilters.json"), "w"
        ) as outfile2:
            json.dump(self.app.confFilters, outfile2)
            self.logger.debug(self.app.confFilters)

    def saveConfig(self):

        if len(self.mainW.ui.lineEditDbname.text()) == 0:
            QMessageBox.about(
                None,
                "Message",
                "Enter a name to create a new database or choose an existing one.",
            )
            return
        
        self.app.config["dbname"] = self.mainW.ui.lineEditDbname.text()
        self.app.config["debug"] = self.mainW.ui.comboBoxDebug.currentText()
        self.app.config["profile"] = self.mainW.ui.lineEditProfileName.text()
        self.mainW.changeProfileSig.emit(self.mainW.ui.lineEditProfileName.text())
        self.mainW.changeDbSig.emit(self.mainW.ui.lineEditDbname.text())

        self.app.config[
            "monthsFilter"
        ] = self.mainW.ui.comboBoxMonthsFilter.currentText()

        self.app.config[
            "defaultTimeStart"
        ] = self.mainW.ui.spinBoxDefaultTimeStart.value()

        self.app.config["defaultTimeEnd"] = self.mainW.ui.spinBoxDefaultTimeEnd.value()
        self.app.config["precision"] = self.mainW.ui.spinBoxPrecision.value()
        with open(
            os.path.join(self.app.directory, "config", "config.json"), "w"
        ) as outfile3:
            json.dump(self.app.config, outfile3)
            self.logger.debug(self.app.config)

        # Connect to selected database
        self.app.db.close()
        self.app.db.setDatabaseName(
            os.path.join(
                self.app.directory, "config", self.app.config["dbname"] + ".db"
            )
        )

        if not self.app.db.open():
            self.logger.critical("Failed to set up db connection")
        self.app.setUpDb()

        # Force image list to reload data
        self.mainW.imageSourceModel.select()
        while self.mainW.imageSourceModel.canFetchMore():
            self.mainW.imageSourceModel.fetchMore()
        self.mainW.filterRegExpChanged()
