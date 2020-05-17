import sys
import os
import ntpath
import numpy as np
import logging

from PyQt5.QtWidgets import QDialog, QApplication, QTableWidgetItem, QFileDialog

from .chartWindow import *
from .imageDetailWindow import *
from .SortFilterProxyModel import *
from .fitsHeaderTab import *
from .settingsTab import *
from .importFitsTab import *
from .importCsvTab import *
from .imageListTab import *
from .gui.mainWindowGui import *

"""
AstroDom main window. It contains three different
tabs that are implemented as separate xxxTab classes.
More or less all gui controls and connects are set 
here.
"""


class MainWindow(QDialog):
    logger = logging.getLogger(__name__)

    model = None
    imageListModel = None
    changeProfileSig = QtCore.pyqtSignal(str)
    changeDbSig = QtCore.pyqtSignal(str)

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.show()

        self.imageListModel = SortFilterProxyModel(self.ui)
        self.imageListTab = ImageListTab(self, app)
        self.importFitsTab = ImportFitsTab(self, app)
        self.importCsvTab = ImportCsvTab(self, app)
        self.settingsTab = SettingsTab(self, app)
        self.fitsHeaderTab = FitsHeaderTab(self, app)

        self.setWindowTitle("AstroDom " + self.app.version)

        # Import dir thread
        self.importDir = ImportDir(self.app)
        self.importDirThread = qtc.QThread()
        self.importDir.moveToThread(self.importDirThread)
        self.importDir.finished.connect(self.importDirThread.quit)
        self.ui.pushButtonLoadFits.clicked.connect(self.importDirThread.start)
        self.ui.pushButtonLoadFits.clicked.connect(self.importDir.worker)
        self.importDir.match_found.connect(self.importFitsTab.addResultsToModel)

        # Import Tab connects
        self.ui.pushButtonSaveFits.clicked.connect(self.importFitsTab.saveFits)
        self.ui.pushButtonDeleteFitsRow.clicked.connect(self.importFitsTab.deleteRows)
        self.ui.pushButtonChooseCsv.clicked.connect(self.importCsvTab.importCsvFile)
        self.ui.pushButtonSaveCsv.clicked.connect(self.importCsvTab.saveCsv)
        self.ui.pushButtonDeleteCsvRow.clicked.connect(self.importCsvTab.deleteRows)

        self.ui.groupBoxFitsImport.setTitle(
            "Fits file import (profile: " + self.app.config["profile"] + ")"
        )
        self.ui.groupBoxFitsHeader.setTitle(
            "Fits file header parser (profile: " + self.app.config["profile"] + ")"
        )
        self.changeProfileSig.connect(self.changeGroupBoxTitle)
        self.ui.labelCurrentDb.setText("Current Database: " + self.app.config["dbname"])
        self.changeDbSig.connect(self.changeLabelDb)
        # Setting tab
        self.ui.lineEditModuleDir.setText(self.app.astrodomDir)
        self.ui.pushButtonSaveFilter.clicked.connect(self.settingsTab.saveFilter)
        self.ui.pushButtonSaveConfig.clicked.connect(self.settingsTab.saveConfig)
        self.ui.pushButtonSaveProfile.clicked.connect(self.settingsTab.saveProfile)
        self.ui.pushButtonSelectDb.clicked.connect(self.settingsTab.selectDb)
        self.ui.comboBoxProfile.currentTextChanged.connect(
            self.settingsTab.selectionchange
        )
        # Settings input validation
        self.ui.lineEditDbname.textChanged[str].connect(
            lambda: self.ui.pushButtonSaveConfig.setEnabled(
                self.ui.lineEditDbname.text() != ""
            )
        )
        self.ui.lineEditFitsFile.textChanged[str].connect(
            lambda: self.ui.pushButtonSaveProfile.setEnabled(
                self.ui.lineEditFitsFile.text() != ""
            )
        )
        self.ui.lineEditFitsTarget.textChanged[str].connect(
            lambda: self.ui.pushButtonSaveProfile.setEnabled(
                self.ui.lineEditFitsTarget.text() != ""
            )
        )
        self.ui.lineEditFitsFrame.textChanged[str].connect(
            lambda: self.ui.pushButtonSaveProfile.setEnabled(
                self.ui.lineEditFitsFrame.text() != ""
            )
        )
        self.ui.lineEditFitsFilter.textChanged[str].connect(
            lambda: self.ui.pushButtonSaveProfile.setEnabled(
                self.ui.lineEditFitsFilter.text() != ""
            )
        )
        self.ui.lineEditFitsExposure.textChanged[str].connect(
            lambda: self.ui.pushButtonSaveProfile.setEnabled(
                self.ui.lineEditFitsExposure.text() != ""
            )
        )
        self.ui.lineEditFitsTemp.textChanged[str].connect(
            lambda: self.ui.pushButtonSaveProfile.setEnabled(
                self.ui.lineEditFitsTemp.text() != ""
            )
        )
        self.ui.lineEditFitsXbinning.textChanged[str].connect(
            lambda: self.ui.pushButtonSaveProfile.setEnabled(
                self.ui.lineEditFitsXbinning.text() != ""
            )
        )
        self.ui.lineEditFitsYbinning.textChanged[str].connect(
            lambda: self.ui.pushButtonSaveProfile.setEnabled(
                self.ui.lineEditFitsYbinning.text() != ""
            )
        )
        self.ui.lineEditFitsSitelat.textChanged[str].connect(
            lambda: self.ui.pushButtonSaveProfile.setEnabled(
                self.ui.lineEditFitsSitelat.text() != ""
            )
        )
        self.ui.lineEditFitsSitelong.textChanged[str].connect(
            lambda: self.ui.pushButtonSaveProfile.setEnabled(
                self.ui.lineEditFitsSitelong.text() != ""
            )
        )
        self.ui.lineEditFitsRa.textChanged[str].connect(
            lambda: self.ui.pushButtonSaveProfile.setEnabled(
                self.ui.lineEditFitsRa.text() != ""
            )
        )
        self.ui.lineEditFitsDec.textChanged[str].connect(
            lambda: self.ui.pushButtonSaveProfile.setEnabled(
                self.ui.lineEditFitsDec.text() != ""
            )
        )
        self.ui.lineEditFitsDate.textChanged[str].connect(
            lambda: self.ui.pushButtonSaveProfile.setEnabled(
                self.ui.lineEditFitsDate.text() != ""
            )
        )
        self.ui.lineEditFitsGain.textChanged[str].connect(
            lambda: self.ui.pushButtonSaveProfile.setEnabled(
                self.ui.lineEditFitsGain.text() != ""
            )
        )
        self.ui.lineEditFitsOffset.textChanged[str].connect(
            lambda: self.ui.pushButtonSaveProfile.setEnabled(
                self.ui.lineEditFitsOffset.text() != ""
            )
        )
        self.ui.lineEditProfileName.textChanged[str].connect(
            lambda: self.ui.pushButtonSaveProfile.setEnabled(
                self.ui.lineEditProfileName.text() != ""
            )
        )

        # Fits Header Tab Connects
        self.ui.pushButtonFitsHeader.clicked.connect(self.fitsHeaderTab.readHeaders)

        # Button icons
        self.ui.pushButtonGraph.setIcon(QtGui.QIcon("astrodom/icons/chart-up.png"))
        self.ui.pushButtonDeleteFitsRow.setIcon(QtGui.QIcon("astrodom/icons/cross.png"))
        self.ui.pushButtonDeleteCsvRow.setIcon(QtGui.QIcon("astrodom/icons/cross.png"))
        self.ui.pushButtonSaveFits.setIcon(QtGui.QIcon("astrodom/icons/disk.png"))
        self.ui.pushButtonSaveCsv.setIcon(QtGui.QIcon("astrodom/icons/disk.png"))
        self.ui.pushButtonLoadFits.setIcon(QtGui.QIcon("astrodom/icons/gear.png"))
        self.ui.pushButtonSaveConfig.setIcon(QtGui.QIcon("astrodom/icons/disk.png"))
        self.ui.pushButtonSaveProfile.setIcon(QtGui.QIcon("astrodom/icons/disk.png"))
        self.ui.pushButtonSaveFilter.setIcon(QtGui.QIcon("astrodom/icons/disk.png"))
        self.ui.pushButtonChooseFitsDir.setIcon(
            QtGui.QIcon("astrodom/icons/folder-open.png")
        )
        self.ui.pushButtonChooseCsv.setIcon(
            QtGui.QIcon("astrodom/icons/folder-open.png")
        )
        self.ui.pushButtonSelectDb.setIcon(
            QtGui.QIcon("astrodom/icons/folder-open.png")
        )
        self.ui.pushButtonFitsHeader.setIcon(
            QtGui.QIcon("astrodom/icons/folder-open.png")
        )

        # Disable some Fits buttons
        self.ui.pushButtonLoadFits.setDisabled(True)
        self.ui.pushButtonDeleteFitsRow.setDisabled(True)
        self.ui.lineEditFitsDir.textChanged.connect(
            lambda: self.ui.pushButtonLoadFits.setEnabled(True)
        )
        self.ui.lineEditFitsDir.textChanged.connect(
            lambda: self.ui.pushButtonSaveFits.setDisabled(True)
        )
        self.ui.lineEditFitsDir.textChanged.connect(
            lambda: self.ui.pushButtonDeleteFitsRow.setDisabled(True)
        )
        self.ui.pushButtonSaveFits.setDisabled(True)
        self.importDir.finished.connect(
            lambda: self.ui.pushButtonSaveFits.setEnabled(True)
        )
        self.importDir.finished.connect(
            lambda: self.ui.pushButtonLoadFits.setDisabled(True)
        )
        self.importDir.finished.connect(
            lambda: self.ui.pushButtonDeleteFitsRow.setEnabled(True)
        )
        self.ui.pushButtonChooseFitsDir.clicked.connect(
            self.importFitsTab.importFitsDir
        )

        # Disable some Csv import buttons
        self.ui.pushButtonSaveCsv.setDisabled(True)
        self.ui.pushButtonDeleteCsvRow.setDisabled(True)
        self.ui.lineEditCsv.textChanged.connect(
            lambda: self.ui.pushButtonSaveCsv.setEnabled(True)
        )
        self.ui.lineEditCsv.textChanged.connect(
            lambda: self.ui.pushButtonDeleteCsvRow.setEnabled(True)
        )

        self.ui.pushButtonGraph.clicked.connect(self.dialogChart)
        self.ui.lineEditTarget.textChanged.connect(self.filterRegExpChanged)
        self.ui.lineEditFilter.textChanged.connect(self.filterRegExpChanged)
        self.ui.lineEditFrame.textChanged.connect(self.filterRegExpChanged)
        self.ui.lineEditExposure.textChanged.connect(self.filterRegExpChanged)
        self.ui.comboBoxExposure.currentIndexChanged.connect(self.filterRegExpChanged)
        self.ui.lineEditAlt.textChanged.connect(self.filterRegExpChanged)
        self.ui.comboBoxAlt.currentIndexChanged.connect(self.filterRegExpChanged)
        self.ui.lineEditAz.textChanged.connect(self.filterRegExpChanged)
        self.ui.comboBoxAlt.currentIndexChanged.connect(self.filterRegExpChanged)
        self.ui.doubleSpinBoxFwhm.valueChanged.connect(self.filterRegExpChanged)
        self.ui.comboBoxFwhm.currentIndexChanged.connect(self.filterRegExpChanged)
        self.ui.doubleSpinBoxEccentricity.valueChanged.connect(self.filterRegExpChanged)
        self.ui.comboBoxEccentricity.currentIndexChanged.connect(
            self.filterRegExpChanged
        )
        self.ui.doubleSpinBoxSnrweight.valueChanged.connect(self.filterRegExpChanged)
        self.ui.comboBoxSnrweight.currentIndexChanged.connect(self.filterRegExpChanged)
        self.ui.doubleSpinBoxNoise.valueChanged.connect(self.filterRegExpChanged)
        self.ui.comboBoxNoise.currentIndexChanged.connect(self.filterRegExpChanged)

        m = int(self.ui.comboBoxMonthsFilter.currentText())
        dsh = self.ui.spinBoxDefaultTimeStart.value()
        dst = QtCore.QDateTime(
            QtCore.QDate.currentDate().addMonths(-m), QtCore.QTime(dsh, 0, 0)
        )
        self.ui.dateEditStartDate.setDateTime(dst)
        self.ui.dateEditStartDate.dateTimeChanged.connect(self.filterRegExpChanged)
        deh = self.ui.spinBoxDefaultTimeEnd.value()
        det = QtCore.QDateTime(
            QtCore.QDate.currentDate().addDays(1), QtCore.QTime(deh, 0, 0)
        )
        self.ui.dateEditEndDate.setDateTime(det)
        self.ui.dateEditEndDate.dateTimeChanged.connect(self.filterRegExpChanged)
        self.filterRegExpChanged()
        self.ui.pushButtonLastNight.clicked.connect(self.lastNight)

        self.ui.tableViewImages.doubleClicked.connect(self.imageDetail)

    def imageDetail(self, modelIndex):
        self.imageDetailWindow = ImageDetailWindow(self.imageListModel)
        self.imageDetailWindow.plot(modelIndex)

    def dialogChart(self):
        self.chartWindow = ChartWindow(self.app)
        self.chartWindow.plot(self.imageListModel)

    def closeEvent(self, event):
        try:
            self.imageDetailWindow.close()
        except Exception as e:
            self.logger.debug(f"Closing not existing window {e}")
        try:
            self.chartWindow.close()
        except Exception as e:
            self.logger.debug(f"Closing not existing window {e}")
        self.close()
        event.accept()

    # Slot that updates profile name when a new profile is selected and saved

    def changeGroupBoxTitle(self, title):
        self.ui.groupBoxFitsImport.setTitle("Fits file import (profile: " + title + ")")
        self.ui.groupBoxFitsHeader.setTitle(
            "Fits file header parser (profile: " + title + ")"
        )

    def changeLabelDb(self, title):
        self.ui.labelCurrentDb.setText("Current Database: " + title)

    """
    if 'selected night' button is pressed, start/end date filters are
    set on that night. The selected hour (selH) is used as reference:
    if selH gt than start obs time (dsh) next night is selected,
    else previous night. To avoid gaps, selH is used instead of the
    end obs time (deh)  
    """

    def lastNight(self):
        index = self.ui.tableViewImages.selectionModel().currentIndex()
        if index.row() < 0:
            QMessageBox.about(
                None,
                "Message",
                "Select one record in the table  and press 'select night' button."
                "Astrodom will filter data for that night.",
            )
        selDateString = index.sibling(index.row(), 16).data()
        selQDT = QtCore.QDateTime.fromString(selDateString, "yyyy-MM-ddThh:mm:ss")
        selDT = selQDT.date()
        selH = selQDT.time().hour()
        dsh = self.ui.spinBoxDefaultTimeStart.value()
        deh = self.ui.spinBoxDefaultTimeEnd.value()

        if selH >= dsh:
            dst = QtCore.QDateTime(selDT, QtCore.QTime(dsh, 0, 0))
            det = QtCore.QDateTime(selDT.addDays(1), QtCore.QTime(deh, 0, 0))
        else:
            dst = QtCore.QDateTime(selDT.addDays(-1), QtCore.QTime(dsh, 0, 0))
            det = QtCore.QDateTime(selDT, QtCore.QTime(selH, 0, 0))

        self.ui.dateEditStartDate.setDateTime(dst)
        self.ui.dateEditStartDate.dateTimeChanged.connect(self.filterRegExpChanged)
        self.ui.dateEditEndDate.setDateTime(det)
        self.ui.dateEditEndDate.dateTimeChanged.connect(self.filterRegExpChanged)
        self.filterRegExpChanged()

    def filterRegExpChanged(self):
        regExp = QRegExp("*", Qt.CaseInsensitive, QRegExp.Wildcard)
        self.imageListModel.setFilterRegExp(regExp)

        # Here Mean, Tot and Sigmas are computed
        exposureM = np.array([])
        altM = np.array([])
        fwhmM = np.array([])
        eccentricityM = np.array([])
        snrWeightM = np.array([])
        noiseM = np.array([])

        rowCount = self.imageListModel.rowCount()
        for i in range(rowCount):

            exposureM = np.append(
                exposureM, self.imageListModel.data(self.imageListModel.index(i, 6))
            )
            altM = np.append(
                altM, self.imageListModel.data(self.imageListModel.index(i, 14))
            )
            fwhmM = np.append(
                fwhmM, self.imageListModel.data(self.imageListModel.index(i, 25))
            )
            eccentricityM = np.append(
                eccentricityM,
                self.imageListModel.data(self.imageListModel.index(i, 26)),
            )
            snrWeightM = np.append(
                snrWeightM, self.imageListModel.data(self.imageListModel.index(i, 27))
            )
            noiseM = np.append(
                noiseM, self.imageListModel.data(self.imageListModel.index(i, 28))
            )

        self.ui.lineEditTotImages.setText(str(rowCount))
        exposure = str(np.round(np.sum(exposureM, axis=0) / 3600, 1))
        self.ui.lineEditTotExposure.setText(exposure + "hrs")

        alt = str(np.round(np.mean(altM, axis=0), 2))
        self.ui.lineEditMeanAlt.setText(alt)
        altSigma = str(np.round(np.std(altM, axis=0), 2))
        self.ui.lineEditSigmaAlt.setText(altSigma)

        fwhm = str(np.round(np.mean(fwhmM, axis=0), 2))
        self.ui.lineEditMeanFwhm.setText(fwhm)
        fwhmSigma = str(np.round(np.std(fwhmM, axis=0), 2))
        self.ui.lineEditSigmaFwhm.setText(fwhmSigma)

        eccentricity = str(np.round(np.mean(eccentricityM, axis=0), 2))
        self.ui.lineEditMeanEccentricity.setText(eccentricity)
        eccentricitySigma = str(np.round(np.std(eccentricityM, axis=0), 2))
        self.ui.lineEditSigmaEccentricity.setText(eccentricitySigma)

        snrWeight = str(np.round(np.mean(snrWeightM, axis=0), 2))
        self.ui.lineEditMeanSnr.setText(snrWeight)
        snrWeightSigma = str(np.round(np.std(snrWeightM, axis=0), 2))
        self.ui.lineEditSigmaSnr.setText(snrWeightSigma)

        noise = str(np.round(np.mean(noiseM, axis=0), 2))
        self.ui.lineEditMeanNoise.setText(noise)
        noiseSigma = str(np.round(np.std(noiseM, axis=0), 2))
        self.ui.lineEditSigmaNoise.setText(noiseSigma)
