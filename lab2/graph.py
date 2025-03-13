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
from PySide6.QtWidgets import (QApplication, QLabel, QLineEdit, QMainWindow,
    QPushButton, QSizePolicy, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1342, 825)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.widget = QWidget(self.centralwidget)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(0, 0, 1001, 821))
        self.widget.setStyleSheet(u"backgroud-color: rgb(255, 255, 255)\n"
"")
        self.X1_label = QLabel(self.centralwidget)
        self.X1_label.setObjectName(u"X1_label")
        self.X1_label.setGeometry(QRect(1080, 20, 16, 16))
        self.Y1_label = QLabel(self.centralwidget)
        self.Y1_label.setObjectName(u"Y1_label")
        self.Y1_label.setGeometry(QRect(1170, 20, 16, 16))
        self.X1_lineEdit = QLineEdit(self.centralwidget)
        self.X1_lineEdit.setObjectName(u"X1_lineEdit")
        self.X1_lineEdit.setGeometry(QRect(1100, 20, 51, 22))
        self.Y1_lineEdit = QLineEdit(self.centralwidget)
        self.Y1_lineEdit.setObjectName(u"Y1_lineEdit")
        self.Y1_lineEdit.setGeometry(QRect(1190, 20, 51, 22))
        self.color_label = QLabel(self.centralwidget)
        self.color_label.setObjectName(u"color_label")
        self.color_label.setGeometry(QRect(1060, 60, 51, 31))
        self.Color_lineEdit = QLineEdit(self.centralwidget)
        self.Color_lineEdit.setObjectName(u"Color_lineEdit")
        self.Color_lineEdit.setGeometry(QRect(1120, 50, 111, 41))
        self.CreateButton = QPushButton(self.centralwidget)
        self.CreateButton.setObjectName(u"CreateButton")
        self.CreateButton.setGeometry(QRect(1180, 160, 141, 61))
        self.ClearButton = QPushButton(self.centralwidget)
        self.ClearButton.setObjectName(u"ClearButton")
        self.ClearButton.setGeometry(QRect(1030, 230, 141, 61))
        self.error_label = QLabel(self.centralwidget)
        self.error_label.setObjectName(u"error_label")
        self.error_label.setGeometry(QRect(1100, 760, 181, 31))
        self.Bezier_curve_but = QPushButton(self.centralwidget)
        self.Bezier_curve_but.setObjectName(u"Bezier_curve_but")
        self.Bezier_curve_but.setGeometry(QRect(1030, 300, 141, 61))
        self.step_lineEdit = QLineEdit(self.centralwidget)
        self.step_lineEdit.setObjectName(u"step_lineEdit")
        self.step_lineEdit.setGeometry(QRect(1120, 100, 111, 41))
        self.color_label_2 = QLabel(self.centralwidget)
        self.color_label_2.setObjectName(u"color_label_2")
        self.color_label_2.setGeometry(QRect(1060, 100, 51, 31))
        self.bernstein_button = QPushButton(self.centralwidget)
        self.bernstein_button.setObjectName(u"bernstein_button")
        self.bernstein_button.setGeometry(QRect(1180, 230, 141, 61))
        self.NewCurveButton = QPushButton(self.centralwidget)
        self.NewCurveButton.setObjectName(u"NewCurveButton")
        self.NewCurveButton.setGeometry(QRect(1030, 160, 141, 61))
        self.Parametric_curve_but = QPushButton(self.centralwidget)
        self.Parametric_curve_but.setObjectName(u"Parametric_curve_but")
        self.Parametric_curve_but.setGeometry(QRect(1180, 300, 141, 61))
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.X1_label.setText(QCoreApplication.translate("MainWindow", u"X1", None))
        self.Y1_label.setText(QCoreApplication.translate("MainWindow", u"Y1", None))
        self.color_label.setText(QCoreApplication.translate("MainWindow", u"Color:", None))
        self.CreateButton.setText(QCoreApplication.translate("MainWindow", u"Point", None))
        self.ClearButton.setText(QCoreApplication.translate("MainWindow", u"Clear", None))
        self.error_label.setText("")
        self.Bezier_curve_but.setText(QCoreApplication.translate("MainWindow", u"Recursion", None))
        self.color_label_2.setText(QCoreApplication.translate("MainWindow", u"Step:", None))
        self.bernstein_button.setText(QCoreApplication.translate("MainWindow", u"Bernstein", None))
        self.NewCurveButton.setText(QCoreApplication.translate("MainWindow", u"Create new curve", None))
        self.Parametric_curve_but.setText(QCoreApplication.translate("MainWindow", u"Parametric", None))
    # retranslateUi

