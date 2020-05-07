from PyQt5.QtCore import QDate, QDateTime, QRegExp, QSortFilterProxyModel, Qt, QTime
from datetime import datetime

"""
This class is called from imageList tableview/model and  extends 
QSortFilterProxyModel. FilterAcceptRow determines which record
is shown or not based on filters. It parses each row of the
model and determines if the data contained in each field of
the row is matching its filter. 
"""


class SortFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, ui):
        super().__init__()
        self.ui = ui

    def filterAcceptsRow(self, sourceRow, sourceParent):
        indexFile = self.sourceModel().index(sourceRow, 1, sourceParent)
        dataFile = self.sourceModel().data(indexFile)

        indexTarget = self.sourceModel().index(sourceRow, 3, sourceParent)
        dataTarget = self.sourceModel().data(indexTarget)
        regExpTarget = QRegExp(
            self.ui.lineEditTarget.text(), Qt.CaseInsensitive, QRegExp.RegExp
        )

        indexFilter = self.sourceModel().index(sourceRow, 5, sourceParent)
        dataFilter = self.sourceModel().data(indexFilter)
        regExpFilter = QRegExp(
            self.ui.lineEditFilter.text(), Qt.CaseInsensitive, QRegExp.RegExp
        )

        indexFrame = self.sourceModel().index(sourceRow, 4, sourceParent)
        dataFrame = self.sourceModel().data(indexFrame)
        regExpFrame = QRegExp(
            self.ui.lineEditFrame.text(), Qt.CaseInsensitive, QRegExp.RegExp
        )

        indexExposure = self.sourceModel().index(sourceRow, 6, sourceParent)
        if self.sourceModel().data(indexExposure):
            dataExposure = int(self.sourceModel().data(indexExposure))
        operatorExposure = self.ui.comboBoxExposure.itemText(
            self.ui.comboBoxExposure.currentIndex()
        )

        indexFwhm = self.sourceModel().index(sourceRow, 25, sourceParent)
        dataFwhm = self.sourceModel().data(indexFwhm)
        operatorFwhm = self.ui.comboBoxFwhm.itemText(
            self.ui.comboBoxFwhm.currentIndex()
        )

        indexEccentricity = self.sourceModel().index(sourceRow, 26, sourceParent)
        dataEccentricity = self.sourceModel().data(indexEccentricity)
        operatorEccentricity = self.ui.comboBoxEccentricity.itemText(
            self.ui.comboBoxEccentricity.currentIndex()
        )

        indexSnrweight = self.sourceModel().index(sourceRow, 27, sourceParent)
        dataSnrweight = self.sourceModel().data(indexSnrweight)
        operatorSnrweight = self.ui.comboBoxSnrweight.itemText(
            self.ui.comboBoxSnrweight.currentIndex()
        )

        indexNoise = self.sourceModel().index(sourceRow, 28, sourceParent)
        dataNoise = self.sourceModel().data(indexNoise)
        operatorNoise = self.ui.comboBoxNoise.itemText(
            self.ui.comboBoxNoise.currentIndex()
        )

        indexAlt = self.sourceModel().index(sourceRow, 14, sourceParent)
        dataAlt = self.sourceModel().data(indexAlt)
        operatorAlt = self.ui.comboBoxAlt.itemText(self.ui.comboBoxAlt.currentIndex())

        indexAz = self.sourceModel().index(sourceRow, 15, sourceParent)
        dataAz = self.sourceModel().data(indexAz)
        operatorAz = self.ui.comboBoxAz.itemText(self.ui.comboBoxAz.currentIndex())

        indexDate = self.sourceModel().index(sourceRow, 16, sourceParent)
        dataDate = self.sourceModel().data(indexDate)
        if dataDate:

            dataDate = datetime.strptime(dataDate, "%Y-%m-%dT%H:%M:%S")
        bReturn = True

        if regExpTarget.indexIn(dataTarget) < 0:
            bReturn = False
        if regExpFilter.indexIn(dataFilter) < 0:
            bReturn = False
        if regExpFrame.indexIn(dataFrame) < 0:
            bReturn = False

        if self.ui.lineEditExposure.text() and bReturn == True:
            if (
                operatorExposure == "="
                and int(self.ui.lineEditExposure.text()) == dataExposure
            ):
                bReturn = True
            elif (
                operatorExposure == "<"
                and int(self.ui.lineEditExposure.text()) > dataExposure
            ):
                bReturn = True
            elif (
                operatorExposure == ">"
                and int(self.ui.lineEditExposure.text()) < dataExposure
            ):
                bReturn = True
            else:
                bReturn = False

        if self.ui.doubleSpinBoxEccentricity.value() and bReturn == True:
            if (
                operatorEccentricity == "="
                and self.ui.doubleSpinBoxEccentricity.value() == dataEccentricity
            ):
                bReturn = True
            elif (
                operatorEccentricity == "<"
                and self.ui.doubleSpinBoxEccentricity.value() > dataEccentricity
            ):
                bReturn = True
            elif (
                operatorEccentricity == ">"
                and self.ui.doubleSpinBoxEccentricity.value() < dataEccentricity
            ):
                bReturn = True
            else:
                bReturn = False

        if self.ui.doubleSpinBoxFwhm.value() and bReturn == True:
            if operatorFwhm == "=" and self.ui.doubleSpinBoxFwhm.value() == dataFwhm:
                bReturn = True
            elif operatorFwhm == "<" and self.ui.doubleSpinBoxFwhm.value() > dataFwhm:
                bReturn = True
            elif operatorFwhm == ">" and self.ui.doubleSpinBoxFwhm.value() < dataFwhm:
                bReturn = True
            else:
                bReturn = False

        if self.ui.doubleSpinBoxSnrweight.value() and bReturn == True:
            if (
                operatorSnrweight == "="
                and self.ui.doubleSpinBoxSnrweight.value() == dataSnrweight
            ):
                bReturn = True
            elif (
                operatorSnrweight == "<"
                and self.ui.doubleSpinBoxSnrweight.value() > dataSnrweight
            ):
                bReturn = True
            elif (
                operatorSnrweight == ">"
                and self.ui.doubleSpinBoxSnrweight.value() < dataSnrweight
            ):
                bReturn = True
            else:
                bReturn = False

        if self.ui.doubleSpinBoxNoise.value() and bReturn == True:
            if operatorNoise == "=" and self.ui.doubleSpinBoxNoise.value() == dataNoise:
                bReturn = True
            elif (
                operatorNoise == "<" and self.ui.doubleSpinBoxNoise.value() > dataNoise
            ):
                bReturn = True
            elif (
                operatorNoise == ">" and self.ui.doubleSpinBoxNoise.value() < dataNoise
            ):
                bReturn = True
            else:
                bReturn = False

        if self.ui.lineEditAz.text() and bReturn == True:
            if operatorAz == "=" and int(self.ui.lineEditAz.text()) == dataAz:
                bReturn = True
            elif operatorAz == "<" and int(self.ui.lineEditAz.text()) > dataAz:
                bReturn = True
            elif operatorAz == ">" and int(self.ui.lineEditAz.text()) < dataAz:
                bReturn = True
            else:
                bReturn = False

        if self.ui.lineEditAlt.text() and bReturn == True:
            if operatorAlt == "=" and int(self.ui.lineEditAlt.text()) == dataAlt:
                bReturn = True
            elif operatorAlt == "<" and int(self.ui.lineEditAlt.text()) > dataAlt:
                bReturn = True
            elif operatorAlt == ">" and int(self.ui.lineEditAlt.text()) < dataAlt:
                bReturn = True
            else:
                bReturn = False

        if (
            self.ui.dateEditStartDate.dateTime()
            and self.ui.dateEditEndDate.dateTime()
            and dataDate
            and bReturn == True
        ):
            if (
                self.ui.dateEditStartDate.dateTime() < dataDate
                and self.ui.dateEditEndDate.dateTime() > dataDate
            ):
                bReturn = True
            else:
                bReturn = False

        return bReturn
