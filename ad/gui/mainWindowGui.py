# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1651, 872)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setMinimumSize(QtCore.QSize(1651, 872))
        Dialog.setMaximumSize(QtCore.QSize(1651, 872))
        Dialog.setSizeGripEnabled(False)
        self.tabWidget = QtWidgets.QTabWidget(Dialog)
        self.tabWidget.setGeometry(QtCore.QRect(5, 10, 1631, 851))
        self.tabWidget.setObjectName("tabWidget")
        self.tabImages = QtWidgets.QWidget()
        self.tabImages.setObjectName("tabImages")
        self.pushButtonGraph = QtWidgets.QPushButton(self.tabImages)
        self.pushButtonGraph.setGeometry(QtCore.QRect(1090, 40, 95, 26))
        self.pushButtonGraph.setObjectName("pushButtonGraph")
        self.tableViewImages = QtWidgets.QTableView(self.tabImages)
        self.tableViewImages.setGeometry(QtCore.QRect(10, 80, 1611, 701))
        self.tableViewImages.setObjectName("tableViewImages")
        self.lineEditTarget = QtWidgets.QLineEdit(self.tabImages)
        self.lineEditTarget.setGeometry(QtCore.QRect(72, 11, 91, 26))
        self.lineEditTarget.setObjectName("lineEditTarget")
        self.labelTarget = QtWidgets.QLabel(self.tabImages)
        self.labelTarget.setGeometry(QtCore.QRect(13, 15, 61, 18))
        self.labelTarget.setObjectName("labelTarget")
        self.labelFilter = QtWidgets.QLabel(self.tabImages)
        self.labelFilter.setGeometry(QtCore.QRect(14, 43, 51, 18))
        self.labelFilter.setObjectName("labelFilter")
        self.lineEditFilter = QtWidgets.QLineEdit(self.tabImages)
        self.lineEditFilter.setGeometry(QtCore.QRect(72, 40, 91, 26))
        self.lineEditFilter.setObjectName("lineEditFilter")
        self.labelFrame = QtWidgets.QLabel(self.tabImages)
        self.labelFrame.setGeometry(QtCore.QRect(192, 14, 74, 18))
        self.labelFrame.setObjectName("labelFrame")
        self.labelExposure = QtWidgets.QLabel(self.tabImages)
        self.labelExposure.setGeometry(QtCore.QRect(192, 43, 74, 18))
        self.labelExposure.setObjectName("labelExposure")
        self.lineEditFrame = QtWidgets.QLineEdit(self.tabImages)
        self.lineEditFrame.setGeometry(QtCore.QRect(265, 10, 91, 26))
        self.lineEditFrame.setObjectName("lineEditFrame")
        self.lineEditExposure = QtWidgets.QLineEdit(self.tabImages)
        self.lineEditExposure.setGeometry(QtCore.QRect(305, 39, 50, 26))
        self.lineEditExposure.setObjectName("lineEditExposure")
        self.comboBoxExposure = QtWidgets.QComboBox(self.tabImages)
        self.comboBoxExposure.setGeometry(QtCore.QRect(265, 39, 40, 26))
        self.comboBoxExposure.setObjectName("comboBoxExposure")
        self.comboBoxExposure.addItem("")
        self.comboBoxExposure.addItem("")
        self.comboBoxExposure.addItem("")
        self.labelAlt = QtWidgets.QLabel(self.tabImages)
        self.labelAlt.setGeometry(QtCore.QRect(384, 43, 31, 20))
        self.labelAlt.setObjectName("labelAlt")
        self.labelAz = QtWidgets.QLabel(self.tabImages)
        self.labelAz.setGeometry(QtCore.QRect(384, 13, 31, 20))
        self.labelAz.setObjectName("labelAz")
        self.comboBoxAz = QtWidgets.QComboBox(self.tabImages)
        self.comboBoxAz.setGeometry(QtCore.QRect(415, 10, 40, 26))
        self.comboBoxAz.setObjectName("comboBoxAz")
        self.comboBoxAz.addItem("")
        self.comboBoxAz.addItem("")
        self.comboBoxAz.addItem("")
        self.lineEditAz = QtWidgets.QLineEdit(self.tabImages)
        self.lineEditAz.setGeometry(QtCore.QRect(455, 10, 50, 26))
        self.lineEditAz.setObjectName("lineEditAz")
        self.lineEditAlt = QtWidgets.QLineEdit(self.tabImages)
        self.lineEditAlt.setGeometry(QtCore.QRect(455, 39, 50, 26))
        self.lineEditAlt.setObjectName("lineEditAlt")
        self.comboBoxAlt = QtWidgets.QComboBox(self.tabImages)
        self.comboBoxAlt.setGeometry(QtCore.QRect(415, 39, 40, 26))
        self.comboBoxAlt.setObjectName("comboBoxAlt")
        self.comboBoxAlt.addItem("")
        self.comboBoxAlt.addItem("")
        self.comboBoxAlt.addItem("")
        self.labelEccentricity = QtWidgets.QLabel(self.tabImages)
        self.labelEccentricity.setGeometry(QtCore.QRect(530, 42, 51, 20))
        self.labelEccentricity.setObjectName("labelEccentricity")
        self.comboBoxFwhm = QtWidgets.QComboBox(self.tabImages)
        self.comboBoxFwhm.setGeometry(QtCore.QRect(582, 9, 40, 26))
        self.comboBoxFwhm.setObjectName("comboBoxFwhm")
        self.comboBoxFwhm.addItem("")
        self.comboBoxFwhm.addItem("")
        self.comboBoxFwhm.addItem("")
        self.comboBoxEccentricity = QtWidgets.QComboBox(self.tabImages)
        self.comboBoxEccentricity.setGeometry(QtCore.QRect(582, 38, 40, 26))
        self.comboBoxEccentricity.setObjectName("comboBoxEccentricity")
        self.comboBoxEccentricity.addItem("")
        self.comboBoxEccentricity.addItem("")
        self.comboBoxEccentricity.addItem("")
        self.labelFwhm = QtWidgets.QLabel(self.tabImages)
        self.labelFwhm.setGeometry(QtCore.QRect(530, 12, 51, 20))
        self.labelFwhm.setObjectName("labelFwhm")
        self.labelNoise = QtWidgets.QLabel(self.tabImages)
        self.labelNoise.setGeometry(QtCore.QRect(710, 42, 51, 20))
        self.labelNoise.setObjectName("labelNoise")
        self.comboBoxSnrweight = QtWidgets.QComboBox(self.tabImages)
        self.comboBoxSnrweight.setGeometry(QtCore.QRect(760, 9, 40, 26))
        self.comboBoxSnrweight.setObjectName("comboBoxSnrweight")
        self.comboBoxSnrweight.addItem("")
        self.comboBoxSnrweight.addItem("")
        self.comboBoxSnrweight.addItem("")
        self.comboBoxNoise = QtWidgets.QComboBox(self.tabImages)
        self.comboBoxNoise.setGeometry(QtCore.QRect(760, 38, 40, 26))
        self.comboBoxNoise.setObjectName("comboBoxNoise")
        self.comboBoxNoise.addItem("")
        self.comboBoxNoise.addItem("")
        self.comboBoxNoise.addItem("")
        self.labelSnrweight = QtWidgets.QLabel(self.tabImages)
        self.labelSnrweight.setGeometry(QtCore.QRect(710, 12, 51, 20))
        self.labelSnrweight.setObjectName("labelSnrweight")
        self.dateEditStartDate = QtWidgets.QDateEdit(self.tabImages)
        self.dateEditStartDate.setGeometry(QtCore.QRect(930, 10, 121, 27))
        self.dateEditStartDate.setCalendarPopup(True)
        self.dateEditStartDate.setObjectName("dateEditStartDate")
        self.labelStartDate = QtWidgets.QLabel(self.tabImages)
        self.labelStartDate.setGeometry(QtCore.QRect(891, 15, 51, 18))
        self.labelStartDate.setObjectName("labelStartDate")
        self.labelEndDate = QtWidgets.QLabel(self.tabImages)
        self.labelEndDate.setGeometry(QtCore.QRect(891, 44, 51, 18))
        self.labelEndDate.setObjectName("labelEndDate")
        self.dateEditEndDate = QtWidgets.QDateEdit(self.tabImages)
        self.dateEditEndDate.setGeometry(QtCore.QRect(930, 39, 121, 27))
        self.dateEditEndDate.setCalendarPopup(True)
        self.dateEditEndDate.setObjectName("dateEditEndDate")
        self.doubleSpinBoxNoise = QtWidgets.QDoubleSpinBox(self.tabImages)
        self.doubleSpinBoxNoise.setGeometry(QtCore.QRect(802, 37, 60, 28))
        self.doubleSpinBoxNoise.setObjectName("doubleSpinBoxNoise")
        self.doubleSpinBoxSnrweight = QtWidgets.QDoubleSpinBox(self.tabImages)
        self.doubleSpinBoxSnrweight.setGeometry(QtCore.QRect(802, 8, 60, 28))
        self.doubleSpinBoxSnrweight.setObjectName("doubleSpinBoxSnrweight")
        self.doubleSpinBoxFwhm = QtWidgets.QDoubleSpinBox(self.tabImages)
        self.doubleSpinBoxFwhm.setGeometry(QtCore.QRect(625, 8, 60, 28))
        self.doubleSpinBoxFwhm.setObjectName("doubleSpinBoxFwhm")
        self.doubleSpinBoxEccentricity = QtWidgets.QDoubleSpinBox(self.tabImages)
        self.doubleSpinBoxEccentricity.setGeometry(QtCore.QRect(625, 37, 60, 28))
        self.doubleSpinBoxEccentricity.setObjectName("doubleSpinBoxEccentricity")
        self.lineEditMeanNoise = QtWidgets.QLineEdit(self.tabImages)
        self.lineEditMeanNoise.setGeometry(QtCore.QRect(921, 787, 50, 26))
        self.lineEditMeanNoise.setToolTip("")
        self.lineEditMeanNoise.setToolTipDuration(1)
        self.lineEditMeanNoise.setReadOnly(True)
        self.lineEditMeanNoise.setObjectName("lineEditMeanNoise")
        self.labelMeanNoise = QtWidgets.QLabel(self.tabImages)
        self.labelMeanNoise.setGeometry(QtCore.QRect(876, 791, 51, 18))
        self.labelMeanNoise.setObjectName("labelMeanNoise")
        self.labelMeanSnr = QtWidgets.QLabel(self.tabImages)
        self.labelMeanSnr.setGeometry(QtCore.QRect(725, 791, 51, 18))
        self.labelMeanSnr.setObjectName("labelMeanSnr")
        self.lineEditMeanSnr = QtWidgets.QLineEdit(self.tabImages)
        self.lineEditMeanSnr.setGeometry(QtCore.QRect(760, 787, 50, 26))
        self.lineEditMeanSnr.setToolTip("")
        self.lineEditMeanSnr.setReadOnly(True)
        self.lineEditMeanSnr.setObjectName("lineEditMeanSnr")
        self.lineEditMeanFwhm = QtWidgets.QLineEdit(self.tabImages)
        self.lineEditMeanFwhm.setGeometry(QtCore.QRect(389, 787, 50, 26))
        self.lineEditMeanFwhm.setToolTip("")
        self.lineEditMeanFwhm.setReadOnly(True)
        self.lineEditMeanFwhm.setObjectName("lineEditMeanFwhm")
        self.labelMeanFwhm = QtWidgets.QLabel(self.tabImages)
        self.labelMeanFwhm.setGeometry(QtCore.QRect(339, 791, 61, 20))
        self.labelMeanFwhm.setStyleSheet("text-decoration: overline;")
        self.labelMeanFwhm.setObjectName("labelMeanFwhm")
        self.labelMeanEccentricity = QtWidgets.QLabel(self.tabImages)
        self.labelMeanEccentricity.setGeometry(QtCore.QRect(509, 790, 91, 20))
        self.labelMeanEccentricity.setObjectName("labelMeanEccentricity")
        self.lineEditMeanEccentricity = QtWidgets.QLineEdit(self.tabImages)
        self.lineEditMeanEccentricity.setGeometry(QtCore.QRect(602, 787, 50, 26))
        self.lineEditMeanEccentricity.setToolTip("")
        self.lineEditMeanEccentricity.setReadOnly(True)
        self.lineEditMeanEccentricity.setObjectName("lineEditMeanEccentricity")
        self.lineEditMeanAlt = QtWidgets.QLineEdit(self.tabImages)
        self.lineEditMeanAlt.setGeometry(QtCore.QRect(217, 787, 50, 26))
        self.lineEditMeanAlt.setToolTip("")
        self.lineEditMeanAlt.setReadOnly(True)
        self.lineEditMeanAlt.setObjectName("lineEditMeanAlt")
        self.labelMeanAlt = QtWidgets.QLabel(self.tabImages)
        self.labelMeanAlt.setGeometry(QtCore.QRect(189, 790, 31, 20))
        self.labelMeanAlt.setObjectName("labelMeanAlt")
        self.labelTotExposure = QtWidgets.QLabel(self.tabImages)
        self.labelTotExposure.setGeometry(QtCore.QRect(14, 790, 81, 20))
        self.labelTotExposure.setObjectName("labelTotExposure")
        self.lineEditTotExposure = QtWidgets.QLineEdit(self.tabImages)
        self.lineEditTotExposure.setGeometry(QtCore.QRect(99, 787, 70, 26))
        self.lineEditTotExposure.setToolTip("")
        self.lineEditTotExposure.setReadOnly(True)
        self.lineEditTotExposure.setObjectName("lineEditTotExposure")
        self.lineEditSigmaNoise = QtWidgets.QLineEdit(self.tabImages)
        self.lineEditSigmaNoise.setGeometry(QtCore.QRect(973, 787, 50, 26))
        self.lineEditSigmaNoise.setToolTip("")
        self.lineEditSigmaNoise.setReadOnly(True)
        self.lineEditSigmaNoise.setObjectName("lineEditSigmaNoise")
        self.lineEditSigmaFwhm = QtWidgets.QLineEdit(self.tabImages)
        self.lineEditSigmaFwhm.setGeometry(QtCore.QRect(441, 787, 50, 26))
        self.lineEditSigmaFwhm.setToolTip("")
        self.lineEditSigmaFwhm.setReadOnly(True)
        self.lineEditSigmaFwhm.setObjectName("lineEditSigmaFwhm")
        self.lineEditSigmaEccentricity = QtWidgets.QLineEdit(self.tabImages)
        self.lineEditSigmaEccentricity.setGeometry(QtCore.QRect(654, 787, 50, 26))
        self.lineEditSigmaEccentricity.setToolTip("")
        self.lineEditSigmaEccentricity.setReadOnly(True)
        self.lineEditSigmaEccentricity.setObjectName("lineEditSigmaEccentricity")
        self.lineEditSigmaAlt = QtWidgets.QLineEdit(self.tabImages)
        self.lineEditSigmaAlt.setGeometry(QtCore.QRect(269, 787, 50, 26))
        self.lineEditSigmaAlt.setToolTip("")
        self.lineEditSigmaAlt.setReadOnly(True)
        self.lineEditSigmaAlt.setObjectName("lineEditSigmaAlt")
        self.lineEditSigmaSnr = QtWidgets.QLineEdit(self.tabImages)
        self.lineEditSigmaSnr.setGeometry(QtCore.QRect(812, 787, 50, 26))
        self.lineEditSigmaSnr.setToolTip("")
        self.lineEditSigmaSnr.setToolTipDuration(1)
        self.lineEditSigmaSnr.setReadOnly(True)
        self.lineEditSigmaSnr.setObjectName("lineEditSigmaSnr")
        self.lineEditTotImages = QtWidgets.QLineEdit(self.tabImages)
        self.lineEditTotImages.setGeometry(QtCore.QRect(46, 787, 51, 26))
        self.lineEditTotImages.setToolTip("")
        self.lineEditTotImages.setReadOnly(True)
        self.lineEditTotImages.setObjectName("lineEditTotImages")
        self.tabWidget.addTab(self.tabImages, "")
        self.tabImport = QtWidgets.QWidget()
        self.tabImport.setObjectName("tabImport")
        self.groupBox = QtWidgets.QGroupBox(self.tabImport)
        self.groupBox.setGeometry(QtCore.QRect(10, 15, 151, 91))
        self.groupBox.setObjectName("groupBox")
        self.pushButtonSaveDB = QtWidgets.QPushButton(self.groupBox)
        self.pushButtonSaveDB.setGeometry(QtCore.QRect(30, 60, 90, 26))
        icon = QtGui.QIcon.fromTheme("save")
        self.pushButtonSaveDB.setIcon(icon)
        self.pushButtonSaveDB.setObjectName("pushButtonSaveDB")
        self.pushButtonImportFitsDir = QtWidgets.QPushButton(self.groupBox)
        self.pushButtonImportFitsDir.setGeometry(QtCore.QRect(30, 30, 90, 26))
        self.pushButtonImportFitsDir.setObjectName("pushButtonImportFitsDir")
        self.groupBox_2 = QtWidgets.QGroupBox(self.tabImport)
        self.groupBox_2.setGeometry(QtCore.QRect(180, 15, 151, 91))
        self.groupBox_2.setObjectName("groupBox_2")
        self.pushButtonLoadCSV = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButtonLoadCSV.setGeometry(QtCore.QRect(30, 30, 90, 26))
        self.pushButtonLoadCSV.setObjectName("pushButtonLoadCSV")
        self.pushButtonUpdateDB = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButtonUpdateDB.setGeometry(QtCore.QRect(30, 60, 90, 26))
        self.pushButtonUpdateDB.setObjectName("pushButtonUpdateDB")
        self.tableViewImport = QtWidgets.QTableView(self.tabImport)
        self.tableViewImport.setGeometry(QtCore.QRect(10, 120, 1611, 691))
        self.tableViewImport.setObjectName("tableViewImport")
        self.pushButtonDeleteRows = QtWidgets.QPushButton(self.tabImport)
        self.pushButtonDeleteRows.setGeometry(QtCore.QRect(370, 40, 101, 26))
        self.pushButtonDeleteRows.setObjectName("pushButtonDeleteRows")
        self.tabWidget.addTab(self.tabImport, "")
        self.tabSettings = QtWidgets.QWidget()
        self.tabSettings.setObjectName("tabSettings")
        self.groupBox_3 = QtWidgets.QGroupBox(self.tabSettings)
        self.groupBox_3.setGeometry(QtCore.QRect(20, 20, 261, 641))
        self.groupBox_3.setObjectName("groupBox_3")
        self.lineEditFitsFile = QtWidgets.QLineEdit(self.groupBox_3)
        self.lineEditFitsFile.setGeometry(QtCore.QRect(123, 30, 121, 26))
        self.lineEditFitsFile.setObjectName("lineEditFitsFile")
        self.labelFitsFile = QtWidgets.QLabel(self.groupBox_3)
        self.labelFitsFile.setGeometry(QtCore.QRect(10, 34, 91, 20))
        self.labelFitsFile.setObjectName("labelFitsFile")
        self.labelFitsTarget = QtWidgets.QLabel(self.groupBox_3)
        self.labelFitsTarget.setGeometry(QtCore.QRect(10, 74, 91, 20))
        self.labelFitsTarget.setObjectName("labelFitsTarget")
        self.lineEditFitsTarget = QtWidgets.QLineEdit(self.groupBox_3)
        self.lineEditFitsTarget.setGeometry(QtCore.QRect(123, 70, 121, 26))
        self.lineEditFitsTarget.setText("")
        self.lineEditFitsTarget.setObjectName("lineEditFitsTarget")
        self.labelFitsFrame = QtWidgets.QLabel(self.groupBox_3)
        self.labelFitsFrame.setGeometry(QtCore.QRect(10, 114, 91, 20))
        self.labelFitsFrame.setObjectName("labelFitsFrame")
        self.lineEditFitsFrame = QtWidgets.QLineEdit(self.groupBox_3)
        self.lineEditFitsFrame.setGeometry(QtCore.QRect(123, 110, 121, 26))
        self.lineEditFitsFrame.setText("")
        self.lineEditFitsFrame.setObjectName("lineEditFitsFrame")
        self.lineEditFitsFilter = QtWidgets.QLineEdit(self.groupBox_3)
        self.lineEditFitsFilter.setGeometry(QtCore.QRect(123, 151, 121, 26))
        self.lineEditFitsFilter.setText("")
        self.lineEditFitsFilter.setObjectName("lineEditFitsFilter")
        self.labelFitsFilter = QtWidgets.QLabel(self.groupBox_3)
        self.labelFitsFilter.setGeometry(QtCore.QRect(10, 155, 91, 20))
        self.labelFitsFilter.setObjectName("labelFitsFilter")
        self.labelFitsExposure = QtWidgets.QLabel(self.groupBox_3)
        self.labelFitsExposure.setGeometry(QtCore.QRect(10, 194, 91, 20))
        self.labelFitsExposure.setObjectName("labelFitsExposure")
        self.lineEditFitsExposure = QtWidgets.QLineEdit(self.groupBox_3)
        self.lineEditFitsExposure.setGeometry(QtCore.QRect(123, 190, 121, 26))
        self.lineEditFitsExposure.setText("")
        self.lineEditFitsExposure.setObjectName("lineEditFitsExposure")
        self.labelFitsTemp = QtWidgets.QLabel(self.groupBox_3)
        self.labelFitsTemp.setGeometry(QtCore.QRect(10, 234, 91, 20))
        self.labelFitsTemp.setObjectName("labelFitsTemp")
        self.lineEditFitsTemp = QtWidgets.QLineEdit(self.groupBox_3)
        self.lineEditFitsTemp.setGeometry(QtCore.QRect(123, 230, 121, 26))
        self.lineEditFitsTemp.setText("")
        self.lineEditFitsTemp.setObjectName("lineEditFitsTemp")
        self.labelFitsXbinning = QtWidgets.QLabel(self.groupBox_3)
        self.labelFitsXbinning.setGeometry(QtCore.QRect(10, 274, 91, 20))
        self.labelFitsXbinning.setObjectName("labelFitsXbinning")
        self.lineEditFitsXbinning = QtWidgets.QLineEdit(self.groupBox_3)
        self.lineEditFitsXbinning.setGeometry(QtCore.QRect(123, 270, 121, 26))
        self.lineEditFitsXbinning.setText("")
        self.lineEditFitsXbinning.setObjectName("lineEditFitsXbinning")
        self.labelFitsYbinning = QtWidgets.QLabel(self.groupBox_3)
        self.labelFitsYbinning.setGeometry(QtCore.QRect(10, 314, 91, 20))
        self.labelFitsYbinning.setObjectName("labelFitsYbinning")
        self.lineEditFitsYbinning = QtWidgets.QLineEdit(self.groupBox_3)
        self.lineEditFitsYbinning.setGeometry(QtCore.QRect(123, 310, 121, 26))
        self.lineEditFitsYbinning.setText("")
        self.lineEditFitsYbinning.setObjectName("lineEditFitsYbinning")
        self.lineEditFitsSitelat = QtWidgets.QLineEdit(self.groupBox_3)
        self.lineEditFitsSitelat.setGeometry(QtCore.QRect(123, 350, 121, 26))
        self.lineEditFitsSitelat.setText("")
        self.lineEditFitsSitelat.setObjectName("lineEditFitsSitelat")
        self.labelFitsSitelat = QtWidgets.QLabel(self.groupBox_3)
        self.labelFitsSitelat.setGeometry(QtCore.QRect(10, 354, 91, 20))
        self.labelFitsSitelat.setObjectName("labelFitsSitelat")
        self.lineEditFitsSitelong = QtWidgets.QLineEdit(self.groupBox_3)
        self.lineEditFitsSitelong.setGeometry(QtCore.QRect(123, 388, 121, 26))
        self.lineEditFitsSitelong.setText("")
        self.lineEditFitsSitelong.setObjectName("lineEditFitsSitelong")
        self.labelFitsSitelong = QtWidgets.QLabel(self.groupBox_3)
        self.labelFitsSitelong.setGeometry(QtCore.QRect(10, 392, 91, 20))
        self.labelFitsSitelong.setObjectName("labelFitsSitelong")
        self.labelFitsRa = QtWidgets.QLabel(self.groupBox_3)
        self.labelFitsRa.setGeometry(QtCore.QRect(10, 434, 91, 20))
        self.labelFitsRa.setObjectName("labelFitsRa")
        self.lineEditFitsRa = QtWidgets.QLineEdit(self.groupBox_3)
        self.lineEditFitsRa.setGeometry(QtCore.QRect(123, 430, 121, 26))
        self.lineEditFitsRa.setText("")
        self.lineEditFitsRa.setObjectName("lineEditFitsRa")
        self.labelFitsDec = QtWidgets.QLabel(self.groupBox_3)
        self.labelFitsDec.setGeometry(QtCore.QRect(10, 474, 91, 20))
        self.labelFitsDec.setObjectName("labelFitsDec")
        self.lineEditFitsDec = QtWidgets.QLineEdit(self.groupBox_3)
        self.lineEditFitsDec.setGeometry(QtCore.QRect(123, 470, 121, 26))
        self.lineEditFitsDec.setText("")
        self.lineEditFitsDec.setObjectName("lineEditFitsDec")
        self.labelFitsDate = QtWidgets.QLabel(self.groupBox_3)
        self.labelFitsDate.setGeometry(QtCore.QRect(10, 514, 91, 20))
        self.labelFitsDate.setObjectName("labelFitsDate")
        self.lineEditFitsDate = QtWidgets.QLineEdit(self.groupBox_3)
        self.lineEditFitsDate.setGeometry(QtCore.QRect(123, 510, 121, 26))
        self.lineEditFitsDate.setText("")
        self.lineEditFitsDate.setObjectName("lineEditFitsDate")
        self.lineEditFitsGain = QtWidgets.QLineEdit(self.groupBox_3)
        self.lineEditFitsGain.setGeometry(QtCore.QRect(123, 548, 121, 26))
        self.lineEditFitsGain.setText("")
        self.lineEditFitsGain.setObjectName("lineEditFitsGain")
        self.labelFitsGain = QtWidgets.QLabel(self.groupBox_3)
        self.labelFitsGain.setGeometry(QtCore.QRect(10, 552, 91, 20))
        self.labelFitsGain.setObjectName("labelFitsGain")
        self.lineEditFitsOffset = QtWidgets.QLineEdit(self.groupBox_3)
        self.lineEditFitsOffset.setGeometry(QtCore.QRect(123, 586, 121, 26))
        self.lineEditFitsOffset.setText("")
        self.lineEditFitsOffset.setObjectName("lineEditFitsOffset")
        self.labelFitsOffset = QtWidgets.QLabel(self.groupBox_3)
        self.labelFitsOffset.setGeometry(QtCore.QRect(10, 590, 91, 20))
        self.labelFitsOffset.setObjectName("labelFitsOffset")
        self.groupBox_4 = QtWidgets.QGroupBox(self.tabSettings)
        self.groupBox_4.setGeometry(QtCore.QRect(340, 430, 261, 121))
        self.groupBox_4.setObjectName("groupBox_4")
        self.labelDbname = QtWidgets.QLabel(self.groupBox_4)
        self.labelDbname.setGeometry(QtCore.QRect(7, 61, 91, 20))
        self.labelDbname.setObjectName("labelDbname")
        self.lineEditDbname = QtWidgets.QLineEdit(self.groupBox_4)
        self.lineEditDbname.setGeometry(QtCore.QRect(120, 57, 121, 26))
        self.lineEditDbname.setText("")
        self.lineEditDbname.setObjectName("lineEditDbname")
        self.groupBox_5 = QtWidgets.QGroupBox(self.tabSettings)
        self.groupBox_5.setGeometry(QtCore.QRect(340, 20, 261, 381))
        self.groupBox_5.setObjectName("groupBox_5")
        self.labelFilterR = QtWidgets.QLabel(self.groupBox_5)
        self.labelFilterR.setGeometry(QtCore.QRect(7, 74, 91, 20))
        self.labelFilterR.setObjectName("labelFilterR")
        self.labelFilterL = QtWidgets.QLabel(self.groupBox_5)
        self.labelFilterL.setGeometry(QtCore.QRect(7, 34, 91, 20))
        self.labelFilterL.setObjectName("labelFilterL")
        self.labelFilterHa = QtWidgets.QLabel(self.groupBox_5)
        self.labelFilterHa.setGeometry(QtCore.QRect(7, 194, 91, 20))
        self.labelFilterHa.setObjectName("labelFilterHa")
        self.lineEditFilterLpr = QtWidgets.QLineEdit(self.groupBox_5)
        self.lineEditFilterLpr.setGeometry(QtCore.QRect(120, 310, 121, 26))
        self.lineEditFilterLpr.setText("")
        self.lineEditFilterLpr.setObjectName("lineEditFilterLpr")
        self.labelFilterOiii = QtWidgets.QLabel(self.groupBox_5)
        self.labelFilterOiii.setGeometry(QtCore.QRect(7, 234, 91, 20))
        self.labelFilterOiii.setObjectName("labelFilterOiii")
        self.labelFilterLpr = QtWidgets.QLabel(self.groupBox_5)
        self.labelFilterLpr.setGeometry(QtCore.QRect(7, 314, 91, 20))
        self.labelFilterLpr.setObjectName("labelFilterLpr")
        self.lineEditFilterR = QtWidgets.QLineEdit(self.groupBox_5)
        self.lineEditFilterR.setGeometry(QtCore.QRect(120, 70, 121, 26))
        self.lineEditFilterR.setText("")
        self.lineEditFilterR.setObjectName("lineEditFilterR")
        self.lineEditFilterL = QtWidgets.QLineEdit(self.groupBox_5)
        self.lineEditFilterL.setGeometry(QtCore.QRect(120, 30, 121, 26))
        self.lineEditFilterL.setObjectName("lineEditFilterL")
        self.lineEditFilterOiii = QtWidgets.QLineEdit(self.groupBox_5)
        self.lineEditFilterOiii.setGeometry(QtCore.QRect(120, 230, 121, 26))
        self.lineEditFilterOiii.setText("")
        self.lineEditFilterOiii.setObjectName("lineEditFilterOiii")
        self.lineEditFilterG = QtWidgets.QLineEdit(self.groupBox_5)
        self.lineEditFilterG.setGeometry(QtCore.QRect(120, 110, 121, 26))
        self.lineEditFilterG.setText("")
        self.lineEditFilterG.setObjectName("lineEditFilterG")
        self.labelFilterB = QtWidgets.QLabel(self.groupBox_5)
        self.labelFilterB.setGeometry(QtCore.QRect(7, 155, 91, 20))
        self.labelFilterB.setObjectName("labelFilterB")
        self.labelFilterG = QtWidgets.QLabel(self.groupBox_5)
        self.labelFilterG.setGeometry(QtCore.QRect(7, 114, 91, 20))
        self.labelFilterG.setObjectName("labelFilterG")
        self.labelFilterSii = QtWidgets.QLabel(self.groupBox_5)
        self.labelFilterSii.setGeometry(QtCore.QRect(7, 274, 91, 20))
        self.labelFilterSii.setObjectName("labelFilterSii")
        self.lineEditFilterSii = QtWidgets.QLineEdit(self.groupBox_5)
        self.lineEditFilterSii.setGeometry(QtCore.QRect(120, 270, 121, 26))
        self.lineEditFilterSii.setText("")
        self.lineEditFilterSii.setObjectName("lineEditFilterSii")
        self.lineEditFilterB = QtWidgets.QLineEdit(self.groupBox_5)
        self.lineEditFilterB.setGeometry(QtCore.QRect(120, 151, 121, 26))
        self.lineEditFilterB.setText("")
        self.lineEditFilterB.setObjectName("lineEditFilterB")
        self.lineEditFilterHa = QtWidgets.QLineEdit(self.groupBox_5)
        self.lineEditFilterHa.setGeometry(QtCore.QRect(120, 190, 121, 26))
        self.lineEditFilterHa.setText("")
        self.lineEditFilterHa.setObjectName("lineEditFilterHa")
        self.pushButtonSaveSettings = QtWidgets.QPushButton(self.tabSettings)
        self.pushButtonSaveSettings.setGeometry(QtCore.QRect(504, 606, 95, 26))
        self.pushButtonSaveSettings.setObjectName("pushButtonSaveSettings")
        self.pushButton = QtWidgets.QPushButton(self.tabSettings)
        self.pushButton.setGeometry(QtCore.QRect(340, 606, 95, 26))
        self.pushButton.setObjectName("pushButton")
        self.tabWidget.addTab(self.tabSettings, "")

        self.retranslateUi(Dialog)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.pushButtonGraph.setText(_translate("Dialog", "Charts"))
        self.labelTarget.setText(_translate("Dialog", "Target"))
        self.labelFilter.setText(_translate("Dialog", "Filter"))
        self.labelFrame.setText(_translate("Dialog", "Frame"))
        self.labelExposure.setText(_translate("Dialog", "Exposure"))
        self.comboBoxExposure.setItemText(0, _translate("Dialog", "="))
        self.comboBoxExposure.setItemText(1, _translate("Dialog", "<"))
        self.comboBoxExposure.setItemText(2, _translate("Dialog", ">"))
        self.labelAlt.setText(_translate("Dialog", "ALT"))
        self.labelAz.setText(_translate("Dialog", "AZ"))
        self.comboBoxAz.setItemText(0, _translate("Dialog", "="))
        self.comboBoxAz.setItemText(1, _translate("Dialog", "<"))
        self.comboBoxAz.setItemText(2, _translate("Dialog", ">"))
        self.comboBoxAlt.setItemText(0, _translate("Dialog", "="))
        self.comboBoxAlt.setItemText(1, _translate("Dialog", "<"))
        self.comboBoxAlt.setItemText(2, _translate("Dialog", ">"))
        self.labelEccentricity.setText(_translate("Dialog", "Eccent"))
        self.comboBoxFwhm.setItemText(0, _translate("Dialog", "="))
        self.comboBoxFwhm.setItemText(1, _translate("Dialog", "<"))
        self.comboBoxFwhm.setItemText(2, _translate("Dialog", ">"))
        self.comboBoxEccentricity.setItemText(0, _translate("Dialog", "="))
        self.comboBoxEccentricity.setItemText(1, _translate("Dialog", "<"))
        self.comboBoxEccentricity.setItemText(2, _translate("Dialog", ">"))
        self.labelFwhm.setText(_translate("Dialog", "FWHM"))
        self.labelNoise.setText(_translate("Dialog", "Noise"))
        self.comboBoxSnrweight.setItemText(0, _translate("Dialog", "="))
        self.comboBoxSnrweight.setItemText(1, _translate("Dialog", "<"))
        self.comboBoxSnrweight.setItemText(2, _translate("Dialog", ">"))
        self.comboBoxNoise.setItemText(0, _translate("Dialog", "="))
        self.comboBoxNoise.setItemText(1, _translate("Dialog", "<"))
        self.comboBoxNoise.setItemText(2, _translate("Dialog", ">"))
        self.labelSnrweight.setText(_translate("Dialog", "SNR"))
        self.dateEditStartDate.setDisplayFormat(_translate("Dialog", "dd/MM/yyyy"))
        self.labelStartDate.setText(_translate("Dialog", "Start"))
        self.labelEndDate.setText(_translate("Dialog", "End"))
        self.dateEditEndDate.setDisplayFormat(_translate("Dialog", "dd/MM/yyyy"))
        self.lineEditMeanNoise.setWhatsThis(_translate("Dialog", "Noise Mean Value"))
        self.labelMeanNoise.setText(_translate("Dialog", "Noise"))
        self.labelMeanSnr.setText(_translate("Dialog", "SNR"))
        self.lineEditMeanSnr.setWhatsThis(_translate("Dialog", "Snr Weight Mean Value"))
        self.lineEditMeanFwhm.setWhatsThis(_translate("Dialog", "Fwhm Mean Value"))
        self.labelMeanFwhm.setText(_translate("Dialog", "FWHM"))
        self.labelMeanEccentricity.setText(_translate("Dialog", "Eccentricity"))
        self.lineEditMeanEccentricity.setWhatsThis(_translate("Dialog", "Eccentricity Mean Value"))
        self.lineEditMeanAlt.setWhatsThis(_translate("Dialog", "Alt Mean Value"))
        self.labelMeanAlt.setText(_translate("Dialog", "Alt"))
        self.labelTotExposure.setText(_translate("Dialog", "Tot"))
        self.lineEditTotExposure.setWhatsThis(_translate("Dialog", "Total Hours"))
        self.lineEditSigmaNoise.setWhatsThis(_translate("Dialog", "Noise Standard Dev"))
        self.lineEditSigmaFwhm.setWhatsThis(_translate("Dialog", "Fwhm Standard Dev"))
        self.lineEditSigmaEccentricity.setWhatsThis(_translate("Dialog", "Eccentricity Standard Dev"))
        self.lineEditSigmaAlt.setWhatsThis(_translate("Dialog", "Alt Standard Dev"))
        self.lineEditSigmaSnr.setWhatsThis(_translate("Dialog", "Snr Weight Standard Dev"))
        self.lineEditTotImages.setWhatsThis(_translate("Dialog", "Total Hours"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabImages), _translate("Dialog", "Images"))
        self.groupBox.setTitle(_translate("Dialog", "File operations"))
        self.pushButtonSaveDB.setText(_translate("Dialog", "Save DB"))
        self.pushButtonImportFitsDir.setText(_translate("Dialog", "Scan Dir"))
        self.groupBox_2.setTitle(_translate("Dialog", "PixInsight Import"))
        self.pushButtonLoadCSV.setText(_translate("Dialog", "Load CSV"))
        self.pushButtonUpdateDB.setText(_translate("Dialog", "Update DB"))
        self.pushButtonDeleteRows.setText(_translate("Dialog", "Delete row"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabImport), _translate("Dialog", "Import"))
        self.groupBox_3.setTitle(_translate("Dialog", "FITS Header Keywords"))
        self.labelFitsFile.setText(_translate("Dialog", "File Name"))
        self.labelFitsTarget.setText(_translate("Dialog", "Target"))
        self.labelFitsFrame.setText(_translate("Dialog", "Frame Type"))
        self.labelFitsFilter.setText(_translate("Dialog", "Filter"))
        self.labelFitsExposure.setText(_translate("Dialog", "Exposure"))
        self.labelFitsTemp.setText(_translate("Dialog", "CCD Temp"))
        self.labelFitsXbinning.setText(_translate("Dialog", "X Bin"))
        self.labelFitsYbinning.setText(_translate("Dialog", "Y Bin"))
        self.labelFitsSitelat.setText(_translate("Dialog", "Site Lat"))
        self.labelFitsSitelong.setText(_translate("Dialog", "Site Long"))
        self.labelFitsRa.setText(_translate("Dialog", "RA"))
        self.labelFitsDec.setText(_translate("Dialog", "DEC"))
        self.labelFitsDate.setText(_translate("Dialog", "Obs Date"))
        self.labelFitsGain.setText(_translate("Dialog", "Gain"))
        self.labelFitsOffset.setText(_translate("Dialog", "Offset"))
        self.groupBox_4.setTitle(_translate("Dialog", "DataBase"))
        self.labelDbname.setText(_translate("Dialog", "DB Name"))
        self.groupBox_5.setTitle(_translate("Dialog", "Filter Keywords"))
        self.labelFilterR.setText(_translate("Dialog", "Red"))
        self.labelFilterL.setText(_translate("Dialog", "Luminance"))
        self.labelFilterHa.setText(_translate("Dialog", "Halpha"))
        self.labelFilterOiii.setText(_translate("Dialog", "Oiii"))
        self.labelFilterLpr.setText(_translate("Dialog", "LPR"))
        self.labelFilterB.setText(_translate("Dialog", "Blue"))
        self.labelFilterG.setText(_translate("Dialog", "Green"))
        self.labelFilterSii.setText(_translate("Dialog", "Sii"))
        self.pushButtonSaveSettings.setText(_translate("Dialog", "Save"))
        self.pushButton.setText(_translate("Dialog", "Default"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabSettings), _translate("Dialog", "Settings"))
