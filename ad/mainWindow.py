import sys
import os
import ntpath
import numpy as np

from PyQt5.QtWidgets import QDialog, QApplication, QTableWidgetItem, QFileDialog
from .imageListTab import *
from .importTab import *
from .settingsTab import *
from .gui.mainWindowGui import *
from .SortFilterProxyModel import *
from .chartWindow import *


class MainWindow(QDialog):

    model = None
    model = None

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
        self.ui.pushButtonLoadCSV.clicked.connect(self.importTab.select_file)
        self.ui.pushButtonSaveDB.clicked.connect(self.importTab.saveDB)
        self.ui.pushButtonUpdateDB.clicked.connect(self.importTab.updateDB)
        self.ui.pushButtonImportFitsDir.clicked.connect(
            self.importTab.importFitsDir)
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
        self.ui.dateEditStartDate.setDateTime(
            QtCore.QDateTime.currentDateTime().addMonths(-3))
        self.ui.dateEditStartDate.dateChanged.connect(
            self.filterRegExpChanged)
        self.ui.dateEditEndDate.setDateTime(
            QtCore.QDateTime.currentDateTime().addDays(1))
        self.ui.dateEditEndDate.dateChanged.connect(
            self.filterRegExpChanged)
        self.filterRegExpChanged()

    def dialogChart(self):
        self.chartWindow = ChartWindow(self.app)

        self.chartWindow.plot(self.imageListModel)

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

        exposure = str(np.round(np.sum(exposureM, axis=0)/3600, 1))
        self.ui.lineEditTotExposure.setText(exposure)

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
