# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
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
from PySide6.QtWidgets import (QApplication, QLabel, QMainWindow, QMenuBar,
    QPushButton, QSizePolicy, QStatusBar, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.CountUp = QPushButton(self.centralwidget)
        self.CountUp.setObjectName(u"CountUp")
        self.CountUp.setGeometry(QRect(510, 400, 141, 61))
        self.MyLabel = QLabel(self.centralwidget)
        self.MyLabel.setObjectName(u"MyLabel")
        self.MyLabel.setGeometry(QRect(110, 60, 451, 131))
        font = QFont()
        font.setPointSize(25)
        self.MyLabel.setFont(font)
        self.MyLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ResetCount = QPushButton(self.centralwidget)
        self.ResetCount.setObjectName(u"ResetCount")
        self.ResetCount.setGeometry(QRect(330, 400, 141, 61))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 36))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.CountUp.setText(QCoreApplication.translate("MainWindow", u"Count Up", None))
        self.MyLabel.setText(QCoreApplication.translate("MainWindow", u"\u3053\u308c\u306f\u30c6\u30ad\u30b9\u30c8\u3067\u3059", None))
        self.ResetCount.setText(QCoreApplication.translate("MainWindow", u"Reset Count", None))
    # retranslateUi

