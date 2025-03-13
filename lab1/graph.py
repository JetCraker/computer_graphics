# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'graph.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QLabel, QLineEdit,
    QMainWindow, QPushButton, QSizePolicy, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(819, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.widget = QWidget(self.centralwidget)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(20, 20, 551, 511))
        self.widget.setStyleSheet(u"backgroud-color: rgb(255, 255, 255)\n"
"")
        self.X1_label = QLabel(self.centralwidget)
        self.X1_label.setObjectName(u"X1_label")
        self.X1_label.setGeometry(QRect(600, 120, 16, 16))
        self.Y1_label = QLabel(self.centralwidget)
        self.Y1_label.setObjectName(u"Y1_label")
        self.Y1_label.setGeometry(QRect(690, 120, 16, 16))
        self.X1_lineEdit = QLineEdit(self.centralwidget)
        self.X1_lineEdit.setObjectName(u"X1_lineEdit")
        self.X1_lineEdit.setGeometry(QRect(620, 120, 51, 22))
        self.Y1_lineEdit = QLineEdit(self.centralwidget)
        self.Y1_lineEdit.setObjectName(u"Y1_lineEdit")
        self.Y1_lineEdit.setGeometry(QRect(710, 120, 51, 22))
        self.Y2_label = QLabel(self.centralwidget)
        self.Y2_label.setObjectName(u"Y2_label")
        self.Y2_label.setGeometry(QRect(690, 150, 16, 16))
        self.X2_label = QLabel(self.centralwidget)
        self.X2_label.setObjectName(u"X2_label")
        self.X2_label.setGeometry(QRect(600, 150, 16, 16))
        self.X2_lineEdit = QLineEdit(self.centralwidget)
        self.X2_lineEdit.setObjectName(u"X2_lineEdit")
        self.X2_lineEdit.setGeometry(QRect(620, 150, 51, 22))
        self.Y2_lineEdit = QLineEdit(self.centralwidget)
        self.Y2_lineEdit.setObjectName(u"Y2_lineEdit")
        self.Y2_lineEdit.setGeometry(QRect(710, 150, 51, 22))
        self.color_label = QLabel(self.centralwidget)
        self.color_label.setObjectName(u"color_label")
        self.color_label.setGeometry(QRect(580, 230, 51, 31))
        self.Color_lineEdit = QLineEdit(self.centralwidget)
        self.Color_lineEdit.setObjectName(u"Color_lineEdit")
        self.Color_lineEdit.setGeometry(QRect(630, 220, 111, 41))
        self.CreateButton = QPushButton(self.centralwidget)
        self.CreateButton.setObjectName(u"CreateButton")
        self.CreateButton.setGeometry(QRect(620, 340, 141, 61))
        self.comboBox = QComboBox(self.centralwidget)
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.setObjectName(u"comboBox")
        self.comboBox.setGeometry(QRect(630, 280, 111, 41))
        self.ClearButton = QPushButton(self.centralwidget)
        self.ClearButton.setObjectName(u"ClearButton")
        self.ClearButton.setGeometry(QRect(620, 410, 141, 61))
        self.error_label = QLabel(self.centralwidget)
        self.error_label.setObjectName(u"error_label")
        self.error_label.setGeometry(QRect(620, 480, 181, 31))
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.X1_label.setText(QCoreApplication.translate("MainWindow", u"X1", None))
        self.Y1_label.setText(QCoreApplication.translate("MainWindow", u"Y1", None))
        self.Y2_label.setText(QCoreApplication.translate("MainWindow", u"Y2", None))
        self.X2_label.setText(QCoreApplication.translate("MainWindow", u"X2", None))
        self.color_label.setText(QCoreApplication.translate("MainWindow", u"Color:", None))
        self.CreateButton.setText(QCoreApplication.translate("MainWindow", u"Create", None))
        self.comboBox.setItemText(0, "")
        self.comboBox.setItemText(1, QCoreApplication.translate("MainWindow", u"Without anything", None))
        self.comboBox.setItemText(2, QCoreApplication.translate("MainWindow", u"Circles", None))
        self.comboBox.setItemText(3, QCoreApplication.translate("MainWindow", u"Squares", None))

        self.ClearButton.setText(QCoreApplication.translate("MainWindow", u"Clear", None))
        self.error_label.setText("")
    # retranslateUi

