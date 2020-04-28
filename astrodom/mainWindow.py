import sys
import os
import ntpath
import numpy as np
import logging

from PyQt5.QtWidgets import QDialog, QApplication, QTableWidgetItem, QFileDialog

from .chartWindow import *
from .imageDetailWindow import *
from .SortFilterProxyModel import *
from .settingsTab import *
from .importTab import *
from .imageListTab import *
from .gui.mainWindowGui import *


class MainWindow(QDialog):
    logger = logging.getLogger(__name__)

    model = None
    imageListModel = None

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.show()

        self.imageListModel = SortFilterProxyModel(self.ui)
        self.imageListTab = ImageListTab(self, app)
        self.importTab = ImportTab(self, app)
        self.settingsTab = SettingsTab(self, app)

        self.setWindowTitle("AstroDom")

        # Import dir thread
        self.importDir = ImportDir(self.app)
        self.importDirThread = qtc.QThread()
        self.importDir.moveToThread(self.importDirThread)
        self.importDir.finished.connect(self.importDirThread.quit)
        self.ui.pushButtonLoadFits.clicked.connect(
            self.importDirThread.start)
        self.ui.pushButtonLoadFits.clicked.connect(
            self.importDir.do_search)
        self.importDir.match_found.connect(self.importTab.addResultsToModel)

        self.ui.pushButtonChooseCsv.clicked.connect(
            self.importTab.importCsvFile)
        self.ui.pushButtonSaveFits.clicked.connect(self.importTab.saveFits)
        self.ui.pushButtonSaveCsv.clicked.connect(self.importTab.saveCsv)
        self.ui.pushButtonDeleteFitsRow.clicked.connect(
            self.importTab.deleteRows)
        self.ui.pushButtonDeleteCsvRow.clicked.connect(
            self.importTab.deleteRows)
        self.ui.pushButtonSaveSettings.clicked.connect(self.settingsTab.saveSettings)

        # Button icons
        self.ui.pushButtonGraph.setIcon(QtGui.QIcon('astrodom/icons/chart-up.png'))
        self.ui.pushButtonDeleteFitsRow.setIcon(QtGui.QIcon('astrodom/icons/cross.png'))
        self.ui.pushButtonDeleteCsvRow.setIcon(QtGui.QIcon('astrodom/icons/cross.png'))
        self.ui.pushButtonSaveFits.setIcon(QtGui.QIcon('astrodom/icons/disk.png'))
        self.ui.pushButtonSaveCsv.setIcon(QtGui.QIcon('astrodom/icons/disk.png'))
        self.ui.pushButtonLoadFits.setIcon(QtGui.QIcon('astrodom/icons/gear.png'))
        self.ui.pushButtonSaveSettings.setIcon(QtGui.QIcon('astrodom/icons/disk.png'))
        self.ui.pushButtonChooseFitsDir.setIcon(QtGui.QIcon('astrodom/icons/folder-open.png'))
        self.ui.pushButtonChooseCsv.setIcon(QtGui.QIcon('astrodom/icons/folder-open.png'))


        # Disable some Fits buttons
        self.ui.pushButtonLoadFits.setDisabled(True)
        self.ui.pushButtonDeleteFitsRow.setDisabled(True)
        self.ui.lineEditFitsDir.textChanged.connect(
            lambda: self.ui.pushButtonLoadFits.setEnabled(True))
        self.ui.lineEditFitsDir.textChanged.connect(
            lambda: self.ui.pushButtonSaveFits.setDisabled(True))
        self.ui.lineEditFitsDir.textChanged.connect(
            lambda: self.ui.pushButtonDeleteFitsRow.setDisabled(True))
        self.ui.pushButtonSaveFits.setDisabled(True)
        self.importDir.finished.connect(
            lambda: self.ui.pushButtonSaveFits.setEnabled(True))
        self.importDir.finished.connect(
            lambda: self.ui.pushButtonLoadFits.setDisabled(True))
        self.importDir.finished.connect(
            lambda: self.ui.pushButtonDeleteFitsRow.setEnabled(True))
        self.ui.pushButtonChooseFitsDir.clicked.connect(
            self.importTab.importFitsDir)

        # Disable some Csv import buttons
        self.ui.pushButtonSaveCsv.setDisabled(True)
        self.ui.pushButtonDeleteCsvRow.setDisabled(True)
        self.ui.lineEditCsv.textChanged.connect(
            lambda: self.ui.pushButtonSaveCsv.setEnabled(True))
        self.ui.lineEditCsv.textChanged.connect(
            lambda: self.ui.pushButtonDeleteCsvRow.setEnabled(True))

        self.ui.pushButtonGraph.clicked.connect(self.dialogChart)
        self.ui.lineEditTarget.textChanged.connect(
            self.filterRegExpChanged)
        self.ui.lineEditFilter.textChanged.connect(
            self.filterRegExpChanged)
        self.ui.lineEditFrame.textChanged.connect(
            self.filterRegExpChanged)
        self.ui.lineEditExposure.textChanged.connect(
            self.filterRegExpChanged)
        self.ui.comboBoxExposure.currentIndexChanged.connect(
            self.filterRegExpChanged)
        self.ui.lineEditAlt.textChanged.connect(
            self.filterRegExpChanged)
        self.ui.comboBoxAlt.currentIndexChanged.connect(
            self.filterRegExpChanged)
        self.ui.lineEditAz.textChanged.connect(
            self.filterRegExpChanged)
        self.ui.comboBoxAlt.currentIndexChanged.connect(
            self.filterRegExpChanged)
        self.ui.doubleSpinBoxFwhm.valueChanged.connect(
            self.filterRegExpChanged)
        self.ui.comboBoxFwhm.currentIndexChanged.connect(
            self.filterRegExpChanged)
        self.ui.doubleSpinBoxEccentricity.valueChanged.connect(
            self.filterRegExpChanged)
        self.ui.comboBoxEccentricity.currentIndexChanged.connect(
            self.filterRegExpChanged)
        self.ui.doubleSpinBoxSnrweight.valueChanged.connect(
            self.filterRegExpChanged)
        self.ui.comboBoxSnrweight.currentIndexChanged.connect(
            self.filterRegExpChanged)
        self.ui.doubleSpinBoxNoise.valueChanged.connect(
            self.filterRegExpChanged)
        self.ui.comboBoxNoise.currentIndexChanged.connect(
            self.filterRegExpChanged)
        
        dsh = self.ui.spinBoxDefaultTimeStart.value()
        dst = QtCore.QDateTime(QtCore.QDate.currentDate().addMonths(-3), QtCore.QTime(dsh,0,0))
        self.ui.dateEditStartDate.setDateTime(dst)
        self.ui.dateEditStartDate.dateTimeChanged.connect(
            self.filterRegExpChanged)
        deh = self.ui.spinBoxDefaultTimeEnd.value()
        det = QtCore.QDateTime(QtCore.QDate.currentDate().addDays(1), QtCore.QTime(deh,0,0))
        self.ui.dateEditEndDate.setDateTime(det)
        self.ui.dateEditEndDate.dateTimeChanged.connect(
            self.filterRegExpChanged)
        self.filterRegExpChanged()

        self.ui.tableViewImages.doubleClicked.connect(
            self.imageDetail)

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
        
    def filterRegExpChanged(self):
        regExp = QRegExp('*', Qt.CaseInsensitive, QRegExp.Wildcard)
        self.imageListModel.setFilterRegExp(regExp)
        exposureM = np.array([])
        altM = np.array([])
        fwhmM = np.array([])
        eccentricityM = np.array([])
        snrWeightM = np.array([])
        noiseM = np.array([])

        rowCount = self.imageListModel.rowCount()
        for i in range(rowCount):

            exposureM = np.append(exposureM, self.imageListModel.data(
                self.imageListModel.index(i, 6)))
            altM = np.append(altM, self.imageListModel.data(
                self.imageListModel.index(i, 14)))
            fwhmM = np.append(fwhmM, self.imageListModel.data(
                self.imageListModel.index(i, 25)))
            eccentricityM = np.append(
                eccentricityM, self.imageListModel.data(self.imageListModel.index(i, 26)))
            snrWeightM = np.append(
                snrWeightM, self.imageListModel.data(self.imageListModel.index(i, 27)))
            noiseM = np.append(
                noiseM, self.imageListModel.data(self.imageListModel.index(i, 28)))

        self.ui.lineEditTotImages.setText(str(rowCount))
        exposure = str(np.round(np.sum(exposureM, axis=0)/3600, 1))
        self.ui.lineEditTotExposure.setText(exposure+"hrs")

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
