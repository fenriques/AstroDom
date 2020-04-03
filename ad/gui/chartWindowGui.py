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
        Dialog2.resize(1283, 1101)
        self.graphWidget1 = PlotWidget(Dialog2)
        self.graphWidget1.setGeometry(QtCore.QRect(7, 10, 400, 200))
        self.graphWidget1.setObjectName("graphWidget1")
        self.graphWidget2 = PlotWidget(Dialog2)
        self.graphWidget2.setGeometry(QtCore.QRect(437, 10, 400, 200))
        self.graphWidget2.setObjectName("graphWidget2")
        self.graphWidget3 = PlotWidget(Dialog2)
        self.graphWidget3.setGeometry(QtCore.QRect(870, 10, 400, 200))
        self.graphWidget3.setObjectName("graphWidget3")
        self.graphWidget4 = PlotWidget(Dialog2)
        self.graphWidget4.setGeometry(QtCore.QRect(7, 230, 400, 200))
        self.graphWidget4.setObjectName("graphWidget4")
        self.graphWidget5 = PlotWidget(Dialog2)
        self.graphWidget5.setGeometry(QtCore.QRect(437, 230, 400, 200))
        self.graphWidget5.setObjectName("graphWidget5")
        self.graphWidget6 = PlotWidget(Dialog2)
        self.graphWidget6.setGeometry(QtCore.QRect(870, 230, 400, 200))
        self.graphWidget6.setObjectName("graphWidget6")
        self.graphWidget8 = PlotWidget(Dialog2)
        self.graphWidget8.setGeometry(QtCore.QRect(437, 450, 400, 200))
        self.graphWidget8.setObjectName("graphWidget8")
        self.graphWidget9 = PlotWidget(Dialog2)
        self.graphWidget9.setGeometry(QtCore.QRect(870, 450, 400, 200))
        self.graphWidget9.setObjectName("graphWidget9")
        self.graphWidget7 = PlotWidget(Dialog2)
        self.graphWidget7.setGeometry(QtCore.QRect(7, 450, 400, 200))
        self.graphWidget7.setObjectName("graphWidget7")
        self.graphWidget11 = PlotWidget(Dialog2)
        self.graphWidget11.setGeometry(QtCore.QRect(437, 670, 400, 200))
        self.graphWidget11.setObjectName("graphWidget11")
        self.graphWidget10 = PlotWidget(Dialog2)
        self.graphWidget10.setGeometry(QtCore.QRect(7, 670, 400, 200))
        self.graphWidget10.setObjectName("graphWidget10")
        self.graphWidget12 = PlotWidget(Dialog2)
        self.graphWidget12.setGeometry(QtCore.QRect(870, 670, 400, 200))
        self.graphWidget12.setObjectName("graphWidget12")
        self.graphWidget13 = PlotWidget(Dialog2)
        self.graphWidget13.setGeometry(QtCore.QRect(7, 890, 400, 200))
        self.graphWidget13.setObjectName("graphWidget13")
        self.graphWidget14 = PlotWidget(Dialog2)
        self.graphWidget14.setGeometry(QtCore.QRect(437, 890, 400, 200))
        self.graphWidget14.setObjectName("graphWidget14")
        self.graphWidget15 = PlotWidget(Dialog2)
        self.graphWidget15.setGeometry(QtCore.QRect(870, 890, 400, 200))
        self.graphWidget15.setObjectName("graphWidget15")
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

        self.retranslateUi(Dialog2)
        QtCore.QMetaObject.connectSlotsByName(Dialog2)

    def retranslateUi(self, Dialog2):
        _translate = QtCore.QCoreApplication.translate
        Dialog2.setWindowTitle(_translate("Dialog2", "Dialog"))
from pyqtgraph import PlotWidget
