# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'saveWidgetUI.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_saveForm(object):
    def setupUi(self, saveForm):
        saveForm.setObjectName("saveForm")
        saveForm.resize(97, 189)
        self.gridLayout = QtWidgets.QGridLayout(saveForm)
        self.gridLayout.setObjectName("gridLayout")
        self.fName = QtWidgets.QLineEdit(saveForm)
        self.fName.setObjectName("fName")
        self.gridLayout.addWidget(self.fName, 0, 0, 1, 1)
        self.dName = QtWidgets.QLineEdit(saveForm)
        self.dName.setObjectName("dName")
        self.gridLayout.addWidget(self.dName, 1, 0, 1, 1)
        self.saveButton = QtWidgets.QPushButton(saveForm)
        self.saveButton.setMinimumSize(QtCore.QSize(64, 64))
        self.saveButton.setObjectName("saveButton")
        self.gridLayout.addWidget(self.saveButton, 2, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 24, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 3, 0, 1, 1)

        self.retranslateUi(saveForm)
        QtCore.QMetaObject.connectSlotsByName(saveForm)

    def retranslateUi(self, saveForm):
        _translate = QtCore.QCoreApplication.translate
        saveForm.setWindowTitle(_translate("saveForm", "Form"))
        self.fName.setPlaceholderText(_translate("saveForm", "Failas?"))
        self.dName.setPlaceholderText(_translate("saveForm", "Data?"))
        self.saveButton.setText(_translate("saveForm", "Saugoti"))
