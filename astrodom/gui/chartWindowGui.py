# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'chartWindow.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog2(object):
    def setupUi(self, Dialog2):
        Dialog2.setObjectName("Dialog2")
        Dialog2.resize(1276, 1184)
        self.graphWidget1 = PlotWidget(Dialog2)
        self.graphWidget1.setGeometry(QtCore.QRect(7, 80, 400, 200))
        self.graphWidget1.setObjectName("graphWidget1")
        self.graphWidget2 = PlotWidget(Dialog2)
        self.graphWidget2.setGeometry(QtCore.QRect(437, 80, 400, 200))
        self.graphWidget2.setObjectName("graphWidget2")
        self.graphWidget3 = PlotWidget(Dialog2)
        self.graphWidget3.setGeometry(QtCore.QRect(870, 80, 400, 200))
        self.graphWidget3.setObjectName("graphWidget3")
        self.graphWidget4 = PlotWidget(Dialog2)
        self.graphWidget4.setGeometry(QtCore.QRect(7, 300, 400, 200))
        self.graphWidget4.setObjectName("graphWidget4")
        self.graphWidget5 = PlotWidget(Dialog2)
        self.graphWidget5.setGeometry(QtCore.QRect(437, 300, 400, 200))
        self.graphWidget5.setObjectName("graphWidget5")
        self.graphWidget6 = PlotWidget(Dialog2)
        self.graphWidget6.setGeometry(QtCore.QRect(870, 300, 400, 200))
        self.graphWidget6.setObjectName("graphWidget6")
        self.graphWidget8 = PlotWidget(Dialog2)
        self.graphWidget8.setGeometry(QtCore.QRect(437, 520, 400, 200))
        self.graphWidget8.setObjectName("graphWidget8")
        self.graphWidget9 = PlotWidget(Dialog2)
        self.graphWidget9.setGeometry(QtCore.QRect(870, 520, 400, 200))
        self.graphWidget9.setObjectName("graphWidget9")
        self.graphWidget7 = PlotWidget(Dialog2)
        self.graphWidget7.setGeometry(QtCore.QRect(7, 520, 400, 200))
        self.graphWidget7.setObjectName("graphWidget7")
        self.graphWidget11 = PlotWidget(Dialog2)
        self.graphWidget11.setGeometry(QtCore.QRect(437, 740, 400, 200))
        self.graphWidget11.setObjectName("graphWidget11")
        self.graphWidget10 = PlotWidget(Dialog2)
        self.graphWidget10.setGeometry(QtCore.QRect(7, 740, 400, 200))
        self.graphWidget10.setObjectName("graphWidget10")
        self.graphWidget12 = PlotWidget(Dialog2)
        self.graphWidget12.setGeometry(QtCore.QRect(870, 740, 400, 200))
        self.graphWidget12.setObjectName("graphWidget12")
        self.graphWidget13 = PlotWidget(Dialog2)
        self.graphWidget13.setGeometry(QtCore.QRect(7, 960, 400, 200))
        self.graphWidget13.setObjectName("graphWidget13")
        self.graphWidget14 = PlotWidget(Dialog2)
        self.graphWidget14.setGeometry(QtCore.QRect(437, 960, 400, 200))
        self.graphWidget14.setObjectName("graphWidget14")
        self.graphWidget15 = PlotWidget(Dialog2)
        self.graphWidget15.setGeometry(QtCore.QRect(870, 960, 400, 200))
        self.graphWidget15.setObjectName("graphWidget15")
        self.groupBox = QtWidgets.QGroupBox(Dialog2)
        self.groupBox.setGeometry(QtCore.QRect(20, 9, 491, 61))
        self.groupBox.setObjectName("groupBox")
        self.labelColorL = QtWidgets.QLabel(self.groupBox)
        self.labelColorL.setGeometry(QtCore.QRect(10, 30, 91, 18))
        self.labelColorL.setObjectName("labelColorL")
        self.labelColorR = QtWidgets.QLabel(self.groupBox)
        self.labelColorR.setGeometry(QtCore.QRect(110, 30, 51, 18))
        self.labelColorR.setObjectName("labelColorR")
        self.labelColorHa = QtWidgets.QLabel(self.groupBox)
        self.labelColorHa.setGeometry(QtCore.QRect(260, 30, 61, 18))
        self.labelColorHa.setObjectName("labelColorHa")
        self.labelColorOiii = QtWidgets.QLabel(self.groupBox)
        self.labelColorOiii.setGeometry(QtCore.QRect(330, 30, 41, 18))
        self.labelColorOiii.setObjectName("labelColorOiii")
        self.labelColorSii = QtWidgets.QLabel(self.groupBox)
        self.labelColorSii.setGeometry(QtCore.QRect(370, 30, 41, 18))
        self.labelColorSii.setObjectName("labelColorSii")
        self.labelColorN = QtWidgets.QLabel(self.groupBox)
        self.labelColorN.setGeometry(QtCore.QRect(400, 30, 81, 18))
        self.labelColorN.setObjectName("labelColorN")
        self.labelColorG = QtWidgets.QLabel(self.groupBox)
        self.labelColorG.setGeometry(QtCore.QRect(150, 30, 51, 18))
        self.labelColorG.setObjectName("labelColorG")
        self.labelColorB = QtWidgets.QLabel(self.groupBox)
        self.labelColorB.setGeometry(QtCore.QRect(210, 30, 51, 18))
        self.labelColorB.setObjectName("labelColorB")
        self.graphWidget6.raise_()
        self.graphWidget9.raise_()
        self.graphWidget1.raise_()
        self.graphWidget2.raise_()
        self.graphWidget3.raise_()
        self.graphWidget4.raise_()
        self.graphWidget5.raise_()
        self.graphWidget8.raise_()
        self.graphWidget7.raise_()
        self.graphWidget11.raise_()
        self.graphWidget10.raise_()
        self.graphWidget12.raise_()
        self.graphWidget13.raise_()
        self.graphWidget14.raise_()
        self.graphWidget15.raise_()
        self.groupBox.raise_()

        self.retranslateUi(Dialog2)
        QtCore.QMetaObject.connectSlotsByName(Dialog2)

    def retranslateUi(self, Dialog2):
        _translate = QtCore.QCoreApplication.translate
        Dialog2.setWindowTitle(_translate("Dialog2", "Dialog"))
        self.groupBox.setTitle(_translate("Dialog2", "Filter Colors"))
        self.labelColorL.setText(_translate("Dialog2", "Luminance"))
        self.labelColorR.setText(_translate("Dialog2", "Red"))
        self.labelColorHa.setText(_translate("Dialog2", "Halpha"))
        self.labelColorOiii.setText(_translate("Dialog2", "Oiii"))
        self.labelColorSii.setText(_translate("Dialog2", "Sii"))
        self.labelColorN.setText(_translate("Dialog2", "Other/NA"))
        self.labelColorG.setText(_translate("Dialog2", "Green"))
        self.labelColorB.setText(_translate("Dialog2", "Blue"))
from pyqtgraph import PlotWidget