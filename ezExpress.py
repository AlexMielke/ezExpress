# ----------------------------------------------------------------------------------------------------------------- #
# --- ezExpress v1.0.6                                                                                          --- #
# ---                                                                                                           --- #
# ---  ezExpress ist ein Programm zum Erstellen eines Einkaufszettels mit Artikeln eines Produktkataloges.      --- #
# ---  Ein Produktkatalog kann von Hand selber erstellt oder vom deutschen Internetanbieter                     --- #
# ---  https://www.discounter-preisvergleich.de/ per WebScraper erstellt werden. Beim letzteren stehen          --- #
# ---  mehrere deutsche Discounter zur Auswahl. Die Produktkataloge können nach Belieben verändert und          --- #
# ---  dann gespeichert werden. Ein Produktkatalog wird in einer selbsterschaffenen Baumstruktur erstellt       --- #
# ---  um eine Abhängigkeit von SQL und die damit verbundenen Software-/Netzwerkinstallationen zu vermeiden.    --- #
# ---  Der mit ezExpress erstellte Einkaufszettel kann ausgedruckt, als PDF-Datei gespeichert oder per Email    --- #
# ---  zum Beispiel an ein Mobiltelefon versendet werden. Die PDF-Dateien beinhalten Checkboxen, um somit       --- #
# ---  den Einkauf zu erleichtern.                                                                              --- #
# ---                                                                                                           --- #
# ---  Das Programm wurde in Python (Version 3.8.6) geschrieben. Folgende externe Bibliotheken wurden benutzt:  --- #
# ---                                                                                                           --- #
# ---  - Requests          (https://requests.readthedocs.io/de/latest/index.html)                               --- #
# ---                      (Lizenz: http://www.apache.org/licenses/LICENSE-2.0)                                 --- #
# ---  - BeautifulSoup4    (https://www.crummy.com/software/BeautifulSoup/)                                     --- #
# ---                      (Lizenz: https://opensource.org/licenses/MIT)                                        --- #
# ---  - cryptography      (https://github.com/pyca/cryptography)                                               --- #
# ---                      (Lizenz: http://www.apache.org/licenses/LICENSE-2.0)                                 --- #
# ---  - pdfgen            (https://github.com/shivanshs9/pdfgen-python)                                        --- #
# ---                      (Lizenz: https://opensource.org/licenses/MIT)                                        --- #
# ---  - PIL/Pillow        (https://python-pillow.org/)                                                         --- #
# ---                      (Lizenz: https://raw.githubusercontent.com/python-pillow/Pillow/master/LICENSE)      --- #
# ---  - pdf2image         (https://github.com/Belval/pdf2image)                                                --- #
# ---                      (Lizenz: https://opensource.org/licenses/MIT)                                        --- #
# ---  - PyQt5             (https://www.riverbankcomputing.com/software/pyqt/)                                  --- #
# ---                      (Lizenz: https://www.gnu.org/licenses/gpl-3.0.de.html)                               --- #
# ---  - lxml              (https://github.com/lxml/lxml)                                                       --- #
# ---                      (Lizenz: https://github.com/lxml/lxml/blob/master/LICENSES.txt)                      --- #
# ---                                                                                                           --- #
# ---  Lizenzinformation:                                                                                       --- #
# ---                                                                                                           --- #
# ---  Das Programm ezExpress wird under der Apache License, Version 2.0 veröffentlicht.                        --- #
# ---  (http://www.apache.org/licenses/LICENSE-2.0.html)                                                        --- #
# ---                                                                                                           --- #
# ---  Bei Fragen, gefundenen Fehlern oder Verbesserungsvorschlägen bitte eine Email schreiben.                 --- #
# ---                                                                                                           --- #
# ---  mailto: alexandermielke@t-online.de                                                                      --- #
# ---                                                                                                           --- #
# ---  Alexander Mielke, November 2020                                                                          --- #
# ---                                                                                                           --- #
# ----------------------------------------------------------------------------------------------------------------- #

import sys
import smtplib
import platform
import webbrowser
from os import chdir
from copy import deepcopy
from pickle import load, dump
from difflib import SequenceMatcher
from pathlib import Path
from datetime import datetime

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.encoders import encode_base64

import crypt
import create_PDF
from treenode import TreeNode

import requests
from bs4 import BeautifulSoup
from PIL.ImageQt import ImageQt
from pdf2image import convert_from_path

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter

###################################################################################
#       Global Classes & Variables                                                #
###################################################################################

Products = []
Katalog = []
KatalogFileList = []
CategoryList = []
currentArtikelList = []
ShoppingList = []
currentCatalogName = ''
lastCatalogName = ''
currentShoppingListName = ''
currentListIndex = 0
TotalPrice = 0.0
changeOccurred = False
catchangeOccurred = False
isCategoryView = False


class ShoppingListSettings:
    catfilename = ''
    zetfilename = ''
    iscatview = False
    pHeadline = 'Einkaufszettel'
    pdate = False
    pfilename = False
    ptempfilename = ''
    pdelete = False
    mfrom = ''
    mto = ''
    mserver = ''
    mport = 0
    mSSL = False
    musername = ''
    mpassword = 'gAAAAABfqWrlhBqcvpnO0sUrZCq8Y5ObBMDdGE88UaVZiWP694PKxWkKLp7MoFnGrgU_wmjW3X1d8caa5vzRKlkbDJ30c7PmNQ=='
    mmessage = ''
    mmessagedate = False
    msendfilename = ''
    mdate = False

###################################################################################
#       PyQt5 - QStyle - Cell Alignment                                           #
###################################################################################


class AlignLeftDelegate(QtWidgets.QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super(AlignLeftDelegate, self).initStyleOption(option, index)
        option.displayAlignment = QtCore.Qt.AlignLeft


class AlignRightDelegate(QtWidgets.QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super(AlignRightDelegate, self).initStyleOption(option, index)
        option.displayAlignment = QtCore.Qt.AlignRight


class AlignCenterDelegate(QtWidgets.QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super(AlignCenterDelegate, self).initStyleOption(option, index)
        option.displayAlignment = QtCore.Qt.AlignCenter


###################################################################################
#       PyQt5 - Einkaufszettel - MainWindow                                       #
###################################################################################


class Ui_Einkaufszettel(QtWidgets.QMainWindow):

    def setupUi(self, Einkaufszettel):
        global ShoppingList
        global isCategoryView
        Einkaufszettel.setObjectName("Einkaufszettel")
        Einkaufszettel.resize(1182, 981)
        Einkaufszettel.closeEvent = self.closeEvent
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Einkaufszettel.sizePolicy().hasHeightForWidth())
        Einkaufszettel.setSizePolicy(sizePolicy)
        #Einkaufszettel.setMinimumSize(QtCore.QSize(1182, 981))
        #Einkaufszettel.setMaximumSize(QtCore.QSize(1182, 981))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("resources/ico/Einkaufszettel.ico"),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Einkaufszettel.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(Einkaufszettel)
        self.centralwidget.setObjectName("centralwidget")

############################## GroupBox Left ############################

        self.cat = QtWidgets.QGroupBox(self.centralwidget)
        self.cat.setGeometry(QtCore.QRect(10, 10, 521, 911))
        self.cat.setObjectName("cat")

        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)

        self.label_cat = QtWidgets.QLabel(self.cat)
        self.label_cat.setGeometry(QtCore.QRect(11, 28, 131, 31))
        self.label_cat.setObjectName("label_cat")

        self.comboBox = QtWidgets.QComboBox(self.cat)
        self.comboBox.setGeometry(QtCore.QRect(150, 30, 361, 30))
        self.comboBox.setObjectName("comboBox")
        self.catview = QtWidgets.QListWidget(self.cat)
        self.catview.setGeometry(QtCore.QRect(10, 70, 501, 351))
        self.catview.setFont(font)
        self.catview.setObjectName("catview")
        self.catview.contextMenuEvent = self.KatalogcontextMenuEvent
        self.catview_show()

        rows = 0
        columns = 3
        self.artview = QtWidgets.QTableWidget(self.cat)
        self.artview.contextMenuEvent = self.ArtikelcontextMenuEvent
        self.artview.setGeometry(QtCore.QRect(10, 430, 501, 471))
        self.artview.setFont(font)
        self.artview.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.artview.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.artview.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.artview.setGridStyle(QtCore.Qt.DotLine)
        self.artview.setObjectName("artview")
        self.artview.horizontalHeader().setHighlightSections(False)
        self.artview.verticalHeader().setVisible(False)
        self.artview.verticalHeader().setHighlightSections(False)
        rdelegate = AlignRightDelegate(self.artview)
        ldelegate = AlignLeftDelegate(self.artview)
        cdelegate = AlignCenterDelegate(self.artview)
        self.artview.clearContents()
        self.artview.setRowCount(rows)
        self.artview.setColumnCount(columns)
        self.artview.verticalHeader().setVisible(False)
        self.artview.setHorizontalHeaderLabels(['Artikelbezeichnung', 'Verpackung', 'Preis'])
        self.artview.setColumnWidth(0, 310)
        self.artview.setColumnWidth(1, 88)
        self.artview.setColumnWidth(2, 84)
        self.artview.verticalHeader().setDefaultSectionSize(11)
        self.artview.setItemDelegateForColumn(0, ldelegate)
        self.artview.setItemDelegateForColumn(1, cdelegate)
        self.artview.setItemDelegateForColumn(2, rdelegate)
        self.artview.horizontalHeader().setStretchLastSection(True)

############################## GroupBox Right ###########################

        self.art = QtWidgets.QGroupBox(self.centralwidget)
        self.art.setGeometry(QtCore.QRect(541, 10, 631, 911))
        self.art.setObjectName("art")

        self.einkauf = QtWidgets.QTableWidget(self.art)
        self.einkauf.contextMenuEvent = self.EinkaufcontextMenuEvent
        rdelegate = AlignRightDelegate(self.einkauf)
        ldelegate = AlignLeftDelegate(self.einkauf)
        cdelegate = AlignCenterDelegate(self.einkauf)

        self.einkauf.setStyleSheet("""background-image: url("resources/logos/ezExpress.png"); background-position: center; background-repeat: no-repeat; background-attachment: fixed""")

        self.einkauf.setGeometry(QtCore.QRect(10, 30, 611, 821))
        self.einkauf.setFont(font)
        self.einkauf.setObjectName("einkauf")
        self.einkauf.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.einkauf.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.einkauf.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.einkauf.setGridStyle(QtCore.Qt.DotLine)
        self.einkauf.horizontalHeader().setHighlightSections(False)
        self.einkauf.verticalHeader().setVisible(False)
        self.einkauf.setRowCount(0)
        self.einkauf.setColumnCount(5)
        self.einkauf.verticalHeader().setVisible(False)
        self.einkauf.setHorizontalHeaderLabels(['M.', 'Artikelbezeichnung', 'Verpackung', 'Preis', 'Gesamt'])
        self.einkauf.setColumnWidth(0, 32)
        self.einkauf.setColumnWidth(1, 303)
        self.einkauf.setColumnWidth(2, 88)
        self.einkauf.setColumnWidth(3, 77)
        self.einkauf.setColumnWidth(4, 77)
        self.einkauf.verticalHeader().setDefaultSectionSize(11)
        self.einkauf.setItemDelegateForColumn(0, rdelegate)
        self.einkauf.setItemDelegateForColumn(1, ldelegate)
        self.einkauf.setItemDelegateForColumn(2, cdelegate)
        self.einkauf.setItemDelegateForColumn(3, rdelegate)
        self.einkauf.setItemDelegateForColumn(4, rdelegate)
        self.einkauf.horizontalHeader().setStretchLastSection(True)

        self.lineEdit_sum = QtWidgets.QLineEdit(self.art)
        self.lineEdit_sum.setEnabled(False)
        self.lineEdit_sum.setGeometry(QtCore.QRect(500, 860, 113, 32))
        self.lineEdit_sum.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.lineEdit_sum.setMaxLength(20)
        self.lineEdit_sum.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.lineEdit_sum.setObjectName("lineEdit_sum")

        self.label_sum = QtWidgets.QLabel(self.art)
        self.label_sum.setGeometry(QtCore.QRect(390, 860, 121, 31))
        self.label_sum.setObjectName("label_sum")

        if platform.system() == 'Linux':
            dir = str(Path.cwd())+'/resources/ico/'
        elif platform.system() == 'Windows':
            dir = str(Path.cwd())+'\\resources\ico\\'
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(dir+"plus.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(dir+"minus.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(dir+"delete.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(dir+"up.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(dir+"down.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(dir+"sort_cat.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(dir+"append.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(dir+"search.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.button_append = QtWidgets.QPushButton(self.art)
        self.button_append.setGeometry(QtCore.QRect(10, 860, 41, 41))
        self.button_append.setText(" ")
        self.button_append.setIcon(icon7)
        self.button_append.setIconSize(QtCore.QSize(30, 30))
        self.button_append.setObjectName("button_append")

        self.button_search = QtWidgets.QPushButton(self.art)
        self.button_search.setGeometry(QtCore.QRect(60, 860, 41, 41))
        self.button_search.setText("")
        self.button_search.setIcon(icon8)
        self.button_search.setIconSize(QtCore.QSize(30, 30))
        self.button_search.setObjectName("button_search")

        self.button_plus = QtWidgets.QPushButton(self.art)
        self.button_plus.setGeometry(QtCore.QRect(110, 860, 41, 41))
        self.button_plus.setText("")
        self.button_plus.setIcon(icon1)
        self.button_plus.setIconSize(QtCore.QSize(24, 24))
        self.button_plus.setObjectName("button_plus")

        self.button_minus = QtWidgets.QPushButton(self.art)
        self.button_minus.setGeometry(QtCore.QRect(150, 860, 41, 41))
        self.button_minus.setText("")
        self.button_minus.setIcon(icon2)
        self.button_minus.setIconSize(QtCore.QSize(24, 24))
        self.button_minus.setObjectName("button_minus")

        self.button_delete = QtWidgets.QPushButton(self.art)
        self.button_delete.setGeometry(QtCore.QRect(200, 860, 41, 41))
        self.button_delete.setText("")
        self.button_delete.setIcon(icon3)
        self.button_delete.setIconSize(QtCore.QSize(20, 20))
        self.button_delete.setObjectName("button_delete")

################################## Main #################################

        Einkaufszettel.setCentralWidget(self.centralwidget)

        self.menubar = QtWidgets.QMenuBar(Einkaufszettel)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1057, 30))
        self.menubar.setObjectName("menubar")
        self.menuEinkaufszettel = QtWidgets.QMenu(self.menubar)
        self.menuEinkaufszettel.setObjectName("menuEinkaufszettel")
        self.menuKategorien = QtWidgets.QMenu(self.menubar)
        self.menuKategorien.setObjectName("menuKategorien")
        self.menuAnsicht = QtWidgets.QMenu(self.menubar)
        self.menuAnsicht.setObjectName("menuAnsicht")
        self.menuHilfe = QtWidgets.QMenu(self.menubar)
        self.menuHilfe.setObjectName("menuHilfe")
        Einkaufszettel.setMenuBar(self.menubar)

        self.action_new = QtWidgets.QAction(Einkaufszettel)
        self.action_new.setObjectName("action_new")
        self.action_open = QtWidgets.QAction(Einkaufszettel)
        self.action_open.setObjectName("action_open")
        self.action_save = QtWidgets.QAction(Einkaufszettel)
        self.action_save.setObjectName("action_save")
        self.action_saveunder = QtWidgets.QAction(Einkaufszettel)
        self.action_saveunder.setObjectName("action_saveunder")
        self.action_print = QtWidgets.QAction(Einkaufszettel)
        self.action_print.setObjectName("action_print")
        self.action_savePDF = QtWidgets.QAction(Einkaufszettel)
        self.action_savePDF.setObjectName("action_savePDF")
        self.action_sendMail = QtWidgets.QAction(Einkaufszettel)
        self.action_sendMail.setObjectName("action_sendMail")
        self.action_settings = QtWidgets.QAction(Einkaufszettel)
        self.action_settings.setObjectName("action_settings")
        self.action_quit = QtWidgets.QAction(Einkaufszettel)
        self.action_quit.setObjectName("action_quit")

        self.action_setListView = QtWidgets.QAction(Einkaufszettel)
        self.action_setListView.setCheckable(True)
        self.action_setListView.setObjectName("action_setListView")
        self.action_setCatView = QtWidgets.QAction(Einkaufszettel)
        self.action_setCatView.setCheckable(True)
        self.action_setCatView.setObjectName("action_setCatView")
        if isCategoryView:
            self.action_setCatView.setChecked(True)
            self.action_setListView.setChecked(False)
        else:
            self.action_setCatView.setChecked(False)
            self.action_setListView.setChecked(True)
        self.action_search = QtWidgets.QAction(Einkaufszettel)
        self.action_search.setObjectName("action_search")

        self.action_opencat = QtWidgets.QAction(Einkaufszettel)
        self.action_opencat.setObjectName("action_opencat")
        self.action_changecat = QtWidgets.QAction(Einkaufszettel)
        self.action_changecat.setObjectName("action_changecat")
        self.action_makecat = QtWidgets.QAction(Einkaufszettel)
        self.action_makecat.setObjectName("action_makecat")

        self.action_help = QtWidgets.QAction(Einkaufszettel)
        self.action_help.setObjectName("action_help")
        self.action_about = QtWidgets.QAction(Einkaufszettel)
        self.action_about.setObjectName("action_about")

        self.menuEinkaufszettel.addAction(self.action_new)
        self.menuEinkaufszettel.addAction(self.action_open)
        self.menuEinkaufszettel.addAction(self.action_save)
        self.menuEinkaufszettel.addAction(self.action_saveunder)
        self.menuEinkaufszettel.addSeparator()
        self.menuEinkaufszettel.addAction(self.action_print)
        self.menuEinkaufszettel.addAction(self.action_savePDF)
        self.menuEinkaufszettel.addAction(self.action_sendMail)
        self.menuEinkaufszettel.addSeparator()
        self.menuEinkaufszettel.addAction(self.action_settings)
        self.menuEinkaufszettel.addSeparator()
        self.menuEinkaufszettel.addAction(self.action_quit)

        self.menuAnsicht.addAction(self.action_search)
        self.menuAnsicht.addSeparator()
        self.menuAnsicht.addAction(self.action_setListView)
        self.menuAnsicht.addAction(self.action_setCatView)
        self.menuKategorien.addAction(self.action_opencat)
        self.menuKategorien.addAction(self.action_makecat)
        self.menuKategorien.addAction(self.action_changecat)
        self.menuHilfe.addAction(self.action_help)
        self.menuHilfe.addAction(self.action_about)
        self.menubar.addAction(self.menuEinkaufszettel.menuAction())
        self.menubar.addAction(self.menuAnsicht.menuAction())
        self.menubar.addAction(self.menuKategorien.menuAction())
        self.menubar.addAction(self.menuHilfe.menuAction())

        self.statusbar = QtWidgets.QStatusBar(Einkaufszettel)
        self.statusbar.setObjectName("statusbar")
        self.statusbar.setSizeGripEnabled(False)
        Einkaufszettel.setStatusBar(self.statusbar)

        self.retranslateUi(Einkaufszettel)

############################## Signals & Slots ##########################

        self.action_new.triggered.connect(self.Einkaufszettel_new)
        self.action_open.triggered.connect(self.openfile)
        self.action_save.triggered.connect(self.fastsavefile)
        self.action_saveunder.triggered.connect(self.savefile)
        self.action_print.triggered.connect(self.Einkaufszettel_print)
        self.action_savePDF.triggered.connect(self.Einkaufszettel_save2PDF)
        self.action_sendMail.triggered.connect(self.Einkaufszettel_sendMail)
        self.action_settings.triggered.connect(show_Settings)
        self.action_quit.triggered.connect(Einkaufszettel.close)

        self.action_search.triggered.connect(show_SearchEngine)

        self.action_setListView.triggered.connect(self.setCheckListView)
        self.action_setCatView.triggered.connect(self.setCheckCatView)

        self.action_opencat.triggered.connect(self.opencatfile)
        self.action_makecat.triggered.connect(show_PreislistenWebScraper)
        self.action_changecat.triggered.connect(show_ChangeCat)

        self.action_about.triggered.connect(lambda: About_Dialog.show())

        if platform.system() == 'Linux':
            datei = str(Path.cwd())+'/resources/info/help.html'
        elif platform.system() == 'Windows':
            datei = str(Path.cwd())+'\\resources\info\\help.html'

        self.action_help.triggered.connect(lambda: webbrowser.open(datei))

        self.artview.doubleClicked.connect(self.Add_to_Einkaufszettel)

        self.catview.clicked.connect(self.artview_showliste)
        self.catview.doubleClicked.connect(self.catview_folding)

        self.button_append.clicked.connect(self.Add_to_Einkaufszettel)
        self.button_search.clicked.connect(show_SearchEngine)
        self.button_plus.clicked.connect(self.Einkaufszettel_add)
        self.button_minus.clicked.connect(self.Einkaufszettel_sub)
        self.button_delete.clicked.connect(self.Einkaufszettel_del)
        self.comboBox.currentIndexChanged.connect(self.Combobox_Change)

        QtCore.QMetaObject.connectSlotsByName(Einkaufszettel)
        self.Einkaufszettel_show()

############################### Translations ############################

    def retranslateUi(self, Einkaufszettel):
        global currentCatalogName
        _translate = QtCore.QCoreApplication.translate
        Einkaufszettel.setWindowTitle(_translate("Einkaufszettel", "ezExpress - ©2020 Alexander Mielke"))
        self.cat.setTitle(_translate("Einkaufszettel", "Produktkatalog"))
        self.catview.setStatusTip(_translate("Einkaufszettel", "Produktkategorien"))
        self.artview.setStatusTip(_translate("Einkaufszettel", "Artikelliste"))
        self.art.setTitle(_translate("Einkaufszettel", "Einkaufszettel"))
        self.einkauf.setStatusTip(_translate("Einkaufszettel", "Aktueller Einkaufszettel"))

        self.lineEdit_sum.setText(_translate("Einkaufszettel", "0,00 €"))
        self.label_sum.setText(_translate("Einkaufszettel", "Gesamtpreis :"))
        self.label_cat.setText(_translate("Einkaufszettel", "aktueller Katalog :"))

        self.menuEinkaufszettel.setTitle(_translate("Einkaufszettel", "Einkaufszettel"))
        self.menuAnsicht.setTitle(_translate("Einkaufszettel", "Bearbeiten"))
        self.menuKategorien.setTitle(_translate("Einkaufszettel", "Produktkatalog"))
        self.menuHilfe.setTitle(_translate("Einkaufszettel", "Hilfe"))

        self.action_new.setText(_translate("Einkaufszettel", "Neu"))
        self.action_new.setStatusTip(_translate("Einkaufszettel", "Neuen Einkaufszettel erstellen"))
        self.action_new.setShortcut(_translate("Einkaufszettel", "Ctrl+N"))
        self.action_open.setText(_translate("Einkaufszettel", "Öffnen"))
        self.action_open.setStatusTip(_translate("Einkaufszettel", "Einen gespeicherten Einkaufszettel öffnen"))
        self.action_open.setShortcut(_translate("Einkaufszettel", "Ctrl+O"))
        self.action_save.setText(_translate("Einkaufszettel", "Speichern"))
        self.action_save.setStatusTip(_translate("Einkaufszettel", "Den aktuellen Einkaufszettel speichern"))
        self.action_save.setShortcut(_translate("Einkaufszettel", "Ctrl+S"))
        self.action_saveunder.setText(_translate("Einkaufszettel", "Speichern unter..."))
        self.action_saveunder.setStatusTip(_translate("Einkaufszettel", "Den aktuellen Einkaufszettel unter neuem Namen speichern"))
        self.action_saveunder.setShortcut(_translate("Einkaufszettel", "Ctrl+U"))
        self.action_print.setText(_translate("Einkaufszettel", "Drucken..."))
        self.action_print.setStatusTip(_translate("Einkaufszettel", "Den aktuellen Einkaufszettel ausdrucken"))
        self.action_print.setShortcut(_translate("Einkaufszettel", "Ctrl+P"))
        self.action_savePDF.setText(_translate("Einkaufszettel", "Exportieren als PDF..."))
        self.action_savePDF.setStatusTip(_translate("Einkaufszettel", "Den aktuellen Einkaufszettel als PDF-Datei exportieren"))
        self.action_sendMail.setText(_translate("Einkaufszettel", "Per E-Mail versenden"))
        self.action_sendMail.setStatusTip(_translate("Einkaufszettel", "Den aktuellen Einkaufszettel per E-Mail versenden"))
        self.action_settings.setText(_translate("Einkaufszettel", "Einstellungen..."))
        self.action_settings.setStatusTip(_translate("Einkaufszettel", "Grundlegende Programmeinstellungen ändern"))
        self.action_quit.setText(_translate("Einkaufszettel", "Beenden"))
        self.action_quit.setStatusTip(_translate("Einkaufszettel", "Programm beenden"))
        self.action_quit.setShortcut(_translate("Einkaufszettel", "Alt+X"))

        self.action_search.setText(_translate("Einkaufszettel", "Artikel suchen..."))
        self.action_search.setStatusTip(_translate("Einkaufszettel", "Im aktuellen Produktkatalog nach Artikeln suchen"))
        self.action_search.setShortcut(_translate("Einkaufszettel", "Ctrl+F"))
        self.action_setCatView.setText(_translate("Einkaufszettel", "Kategorieansicht"))
        self.action_setCatView.setStatusTip(_translate("Einkaufszettel", "Im Einkaufszettel die zugehörigen Kategorien anzeigen"))
        self.action_setListView.setText(_translate("Einkaufszettel", "Listenansicht"))
        self.action_setListView.setStatusTip(_translate("Einkaufszettel", "Den Einkaufszettel als normale Liste anzeigen"))

        self.action_opencat.setText(_translate("Einkaufszettel", "Importieren..."))
        self.action_opencat.setStatusTip(_translate("Einkaufszettel", "Einen Produktkatalog importieren"))
        self.action_opencat.setShortcut(_translate("Einkaufszettel", "Ctrl+I"))
        self.action_makecat.setText(_translate("Einkaufszettel", "WebScraper..."))
        self.action_makecat.setStatusTip(_translate("Einkaufszettel", "Produktkataloge aus dem Internet beziehen"))
        self.action_makecat.setShortcut(_translate("Einkaufszettel", "Ctrl+W"))
        self.action_changecat.setText(_translate("Einkaufszettel", "Bearbeiten..."))
        self.action_changecat.setStatusTip(_translate("Einkaufszettel", "Den geladenen Produktkatalog bearbeiten"))
        self.action_changecat.setShortcut(_translate("Einkaufszettel", "Ctrl+K"))

        self.action_help.setText(_translate("Einkaufszettel", "Hilfe                          "))
        self.action_help.setStatusTip(_translate("Einkaufszettel", "Hilfe aufrufen"))
        self.action_help.setShortcut(_translate("Einkaufszettel", "F1"))
        self.action_about.setText(_translate("Einkaufszettel", "Über..."))
        self.action_about.setStatusTip(_translate("Einkaufszettel", "Informationen über das Programm"))

        self.button_plus.setStatusTip(_translate("Einkaufszettel", "Menge um eine Einheit erhöhen"))
        self.button_minus.setStatusTip(_translate("Einkaufszettel", "Menge um eine Einheit vermindern"))
        self.button_delete.setStatusTip(_translate("Einkaufszettel", "Artikel aus Einkaufszettel löschen"))
        self.button_append.setStatusTip(_translate("Einkaufszettel", "Ausgewählten Artikel zum Einkaufszettel hinzufügen"))
        self.button_search.setStatusTip(_translate("Einkaufszettel", "Artikel im aktuellen Katalog suchen"))

############################# Methods/Functions #########################

    def Combobox_Set(self):
        global currentCatalogName
        global KatalogFileList
        global lastCatalogName

        self.comboBox.blockSignals(True)
        self.comboBox.clear()

        if platform.system() == 'Linux':
            home_dir = Path(str(Path.cwd())+'/catalogs')
        elif platform.system() == 'Windows':
            home_dir = Path(str(Path.home() / 'Documents\ezExpress\catalogs'))

        KatalogFileList = []

        if currentCatalogName == '':
            self.comboBox.addItem('< Bitte auswählen >', currentCatalogName)
            # KatalogFileList.append(currentCatalogName)
        else:
            self.comboBox.addItem(Path(currentCatalogName).stem, currentCatalogName)
            KatalogFileList.append(currentCatalogName)

        for currentfile in home_dir.iterdir():
            if currentfile.suffix == '.epk':
                if (str(currentfile) != currentCatalogName) and (str(currentfile) not in KatalogFileList):
                    self.comboBox.addItem(currentfile.stem, str(currentfile))
                    KatalogFileList.append(str(currentfile))

        if (lastCatalogName != '') and (lastCatalogName != currentCatalogName) and (lastCatalogName not in KatalogFileList):
            self.comboBox.addItem(Path(lastCatalogName).stem, lastCatalogName)
            KatalogFileList.append(lastCatalogName)

        self.comboBox.setCurrentIndex(0)
        self.comboBox.blockSignals(False)

    def Combobox_Change(self):
        global Products
        global CategoryList
        global changeOccurred
        global currentCatalogName
        global KatalogFileList
        global lastCatalogName
        nummer = self.comboBox.currentIndex()
        if nummer > 0:

            if (currentCatalogName != '') and (lastCatalogName not in KatalogFileList):
                lastCatalogName = currentCatalogName

            currentCatalogName = KatalogFileList[nummer]
            dateiname = str(KatalogFileList[nummer])
            Products = load_file(dateiname)
            CategoryList = Products.get_list()
            changeOccurred = True
        self.catview_show()
        self.artview_showliste()

    def setCheckListView(self):
        global isCategoryView
        self.action_setListView.setChecked(True)
        self.action_setCatView.setChecked(False)
        if isCategoryView:
            self.Einkaufszettel_Convert2Listansicht()
            self.Einkaufszettel_show()

        isCategoryView = False

    def setCheckCatView(self):
        global isCategoryView
        self.action_setListView.setChecked(False)
        self.action_setCatView.setChecked(True)
        if not isCategoryView:
            self.Einkaufszettel_Convert2Catansicht()
            self.Einkaufszettel_show()
        isCategoryView = True

    def catview_folding(self):
        global Products
        global CategoryList
        itemnumber = self.catview.currentRow()
        index = CategoryList[itemnumber][0]
        Node = Products.find_indexnode(index)
        Node.aufgeklappt = not Node.aufgeklappt
        CategoryList = Products.get_list()
        self.catview_refresh()

    def catview_refresh(self):
        global CategoryList
        global currentCatalogName
        self.catview.clear()
        for eintrag in CategoryList:
            neues_Item = QtWidgets.QListWidgetItem()
            neues_Item.setText(eintrag[1])
            self.catview.addItem(neues_Item)
        self.Combobox_Set()

    def catview_show(self):
        global Products
        global CategoryList
        if Products:
            CategoryList = Products.get_list()
            self.catview_refresh()

    def artview_showliste(self):
        global Products
        global CategoryList
        global currentListIndex
        self.artview.setRowCount(0)
        self.artview.setEnabled(False)
        if self.catview.currentRow() >= 0:
            itemnumber = self.catview.currentRow()
            index = CategoryList[itemnumber][0]
            currentListIndex = index
            Node = Products.find_indexnode(index)
            if Node.is_leaf():
                self.artview.setEnabled(True)
                ArtListe = Node.liste
                for i in range(len(ArtListe)):
                    self.artview.insertRow(i)
                    self.artview.setItem(i, 0, QtWidgets.QTableWidgetItem(ArtListe[i][0]))
                    self.artview.setItem(i, 1, QtWidgets.QTableWidgetItem(ArtListe[i][1]))
                    self.artview.setItem(i, 2, QtWidgets.QTableWidgetItem(convert_f2s(ArtListe[i][2])))

                    self.artview.scrollToItem(self.artview.item(0, 0))

    def Add_to_Einkaufszettel(self):
        global ShoppingList
        global currentListIndex
        global changeOccurred
        global isCategoryView
        global currentCatalogName
        row = self.artview.currentRow()
        testie = Products.find_indexnode(currentListIndex)
        test1 = testie.is_leaf() and not testie.is_empty()
        test2 = testie.liste
        if (row >= 0) and test1:
            if test2[row][0] != '':
                changeOccurred = True
                art = self.artview.item(row, 0).text()
                vpe = self.artview.item(row, 1).text()
                epreis = convert_s2f(self.artview.item(row, 2).text())
                istdrin = False
                wohin = -1
                changeOccurred = True
                for zeile in range(len(ShoppingList)):
                    if (ShoppingList[zeile][1] == art) and (ShoppingList[zeile][2] == vpe):
                        istdrin = True
                        wohin = zeile
                if istdrin:
                    ShoppingList[wohin][0] += 1
                    ShoppingList[wohin][4] = ShoppingList[wohin][0]*ShoppingList[wohin][3]
                else:
                    if isCategoryView:
                        self.Einkaufszettel_Convert2Listansicht()
                        Node = Products.find_indexnode(currentListIndex)
                        level = Node.get_level()
                        for i in range(level-1):
                            Node = Node.parent
                        ShoppingList.append([1, art, vpe, epreis, epreis, Node.data, currentListIndex, currentCatalogName])
                        self.Einkaufszettel_Convert2Catansicht()
                    else:
                        Node = Products.find_indexnode(currentListIndex)
                        level = Node.get_level()
                        for i in range(level-1):
                            Node = Node.parent
                        ShoppingList.append([1, art, vpe, epreis, epreis, Node.data, currentListIndex, currentCatalogName])
                        self.Einkaufszettel_Convert2Listansicht()
                self.Einkaufszettel_show()

    def Einkaufszettel_show(self):
        global ShoppingList
        global TotalPrice
        global isCategoryView
        summe = 0.0
        self.einkauf.setRowCount(0)
        if ShoppingList:
            for zeile in range(len(ShoppingList)):
                self.einkauf.insertRow(zeile)
                if type(ShoppingList[zeile][0]) is int:  # Zeile ist ein Artikel
                    self.einkauf.setItem(zeile, 0, QtWidgets.QTableWidgetItem(str(ShoppingList[zeile][0])))
                    self.einkauf.setItem(zeile, 1, QtWidgets.QTableWidgetItem(ShoppingList[zeile][1]))
                    self.einkauf.setItem(zeile, 2, QtWidgets.QTableWidgetItem(ShoppingList[zeile][2]))
                    if type(ShoppingList[zeile][3]) is float:
                        self.einkauf.setItem(zeile, 3, QtWidgets.QTableWidgetItem(convert_f2s(ShoppingList[zeile][3])))
                    else:
                        self.einkauf.setItem(zeile, 3, QtWidgets.QTableWidgetItem(ShoppingList[zeile][3]))
                    if type(ShoppingList[zeile][4]) is float:
                        self.einkauf.setItem(zeile, 4, QtWidgets.QTableWidgetItem(convert_f2s(ShoppingList[zeile][4])))
                    else:
                        self.einkauf.setItem(zeile, 4, QtWidgets.QTableWidgetItem(ShoppingList[zeile][4]))
                    preis = ShoppingList[zeile][4]
                    summe += preis
                elif ShoppingList[zeile][7] == 'Laden':
                    item = QtWidgets.QTableWidgetItem(ShoppingList[zeile][1])
                    font = QtGui.QFont()
                    font.setFamily("Arial")
                    font.setBold(True)
                    item.setFont(font)
                    item.setForeground(QtGui.QBrush(QtGui.QColor(192, 101, 21)))
                    self.einkauf.setItem(zeile, 1, item)
                else:
                    item = QtWidgets.QTableWidgetItem(ShoppingList[zeile][1])
                    font = QtGui.QFont()
                    font.setFamily("Arial")
                    font.setBold(True)
                    item.setFont(font)
                    item.setForeground(QtGui.QBrush(QtGui.QColor(21, 101, 192)))
                    self.einkauf.setItem(zeile, 1, item)
        TotalPrice = summe
        self.lineEdit_sum.setText(convert_f2s(TotalPrice))
        isname = Path(currentShoppingListName)
        if currentShoppingListName:
            Einkaufszettel.setWindowTitle('ezExpress - ' + isname.name + ' - ©2020 Alexander Mielke')
        else:
            Einkaufszettel.setWindowTitle('ezExpress - ©2020 Alexander Mielke')

    def Einkaufszettel_new(self):
        global changeOccurred
        global ShoppingList
        global currentShoppingListName
        changeOccurred = True
        ShoppingList = []
        currentShoppingListName = ''
        self.Einkaufszettel_show()

    def Einkaufszettel_add(self):
        global changeOccurred
        global ShoppingList
        aktrow = self.einkauf.currentRow()
        aktcol = self.einkauf.currentColumn()
        if (aktrow >= 0) and (aktrow < len(ShoppingList)) and (type(ShoppingList[aktrow][0]) is int):
            changeOccurred = True
            ShoppingList[aktrow][0] += 1
            ShoppingList[aktrow][4] = ShoppingList[aktrow][0]*ShoppingList[aktrow][3]
            self.Einkaufszettel_show()
            self.einkauf.setCurrentCell(aktrow, aktcol)

    def Einkaufszettel_sub(self):
        global changeOccurred
        global ShoppingList
        aktrow = self.einkauf.currentRow()
        aktcol = self.einkauf.currentColumn()
        if (aktrow >= 0) and (aktrow < len(ShoppingList)) and (type(ShoppingList[aktrow][0]) is int):
            changeOccurred = True
            if ShoppingList[aktrow][0] > 1:
                ShoppingList[aktrow][0] -= 1
                ShoppingList[aktrow][4] = ShoppingList[aktrow][0]*ShoppingList[aktrow][3]
                self.Einkaufszettel_show()
                self.einkauf.setCurrentCell(aktrow, aktcol)
            else:
                self.Einkaufszettel_del()

    def Einkaufszettel_del(self):
        global changeOccurred
        global ShoppingList
        aktrow = self.einkauf.currentRow()
        if isCategoryView:
            if (aktrow > 0) and (aktrow < len(ShoppingList)):
                if type(ShoppingList[aktrow-1][0]) is int:
                    del ShoppingList[aktrow]
                elif aktrow == len(ShoppingList)-1:
                    del ShoppingList[aktrow]
                    del ShoppingList[aktrow-1]

                elif type(ShoppingList[aktrow+1][0]) is int:
                    del ShoppingList[aktrow]
                else:
                    del ShoppingList[aktrow]
                    del ShoppingList[aktrow-1]
                changeOccurred = True
                self.Einkaufszettel_show()
        else:
            if (aktrow >= 0) and (aktrow < len(ShoppingList)) and (type(ShoppingList[aktrow][0]) is int):
                changeOccurred = True
                del ShoppingList[aktrow]
                self.Einkaufszettel_show()

        # Überprüfung, ob isCategoryView oder nicht

    def Einkaufszettel_Convert2Catansicht(self):
        global changeOccurred
        global ShoppingList
        hauptlisten = []
        Ladenliste = []
        if ShoppingList != []:
            changeOccurred = True
            # ShoppingList nach Katalog und Hauptkategorie
            LoescheLadenListe = []
            for i in range(len(ShoppingList)):
                if (type(ShoppingList[i][0]) is int):
                    LoescheLadenListe.append(ShoppingList[i])
            ShoppingList = LoescheLadenListe
            ShoppingList.sort(key=lambda element: (element[7].upper(), element[5].upper()))
            Liste = []
            for i in range(len(ShoppingList)):
                if ShoppingList[i][7] not in Ladenliste:
                    Ladenliste.append(ShoppingList[i][7])
                    if Liste:
                        neuer_eintrag = ['', '', '', '', '', '', '', '']
                        Liste.append(neuer_eintrag)
                    neuer_eintrag = ['', Path(ShoppingList[i][7]).stem, '', '', '', '', '', 'Laden']
                    Liste.append(neuer_eintrag)
                    hauptlisten = []
                if ShoppingList[i][5] not in hauptlisten:
                    hauptlisten.append(ShoppingList[i][5])
                    neuer_eintrag = ['', ShoppingList[i][5], '', '', '', '', '', 'Kategorie']
                    Liste.append(neuer_eintrag)
                Liste.append(ShoppingList[i])
            ShoppingList = Liste

    def Einkaufszettel_Convert2Listansicht(self):
        global changeOccurred
        global ShoppingList
        Ladenliste = []
        if ShoppingList != []:
            LoescheLadenListe = []
            for i in range(len(ShoppingList)):
                if (type(ShoppingList[i][0]) is int):
                    LoescheLadenListe.append(ShoppingList[i])
            ShoppingList = LoescheLadenListe
            ShoppingList.sort(key=lambda element: (element[7].upper(), element[1].upper()))
            changeOccurred = True
            Liste = []
            for i in range(len(ShoppingList)):
                if (ShoppingList[i][7] not in Ladenliste):
                    Ladenliste.append(ShoppingList[i][7])
                    if Liste:
                        neuer_eintrag = ['', '', '', '', '', '', '', '']
                        Liste.append(neuer_eintrag)
                    neuer_eintrag = ['', Path(ShoppingList[i][7]).stem, '', '', '', '', '', 'Laden']
                    Liste.append(neuer_eintrag)
                    Liste.append(ShoppingList[i])
                else:
                    Liste.append(ShoppingList[i])
            ShoppingList = Liste

    def Einkaufszettel_print(self):
        global Einstellungen
        global ShoppingList
        filename = Einstellungen.ptempfilename
        Ueberschrift = Einstellungen.pHeadline
        the_time = datetime.now()
        datumstr = the_time.strftime(format='%d.%m.%Y')
        if Einstellungen.pdate:
            Ueberschrift += ' vom '+datumstr
        fname = Path(currentShoppingListName)
        fname = str(fname.name)
        if Einstellungen.pfilename:
            Ueberschrift += ' '+fname
        create_PDF.create_PDF_File(Ueberschrift, Convert_Einkaufszettel_2_PrintableList(ShoppingList), calculateTotal(), filename)
        self.printDialog()

    def Einkaufszettel_sendMail(self):
        global Einstellungen
        global ShoppingList
        filename = Einstellungen.ptempfilename

        Ueberschrift = Einstellungen.pHeadline

        the_time = datetime.now()
        datumstr = the_time.strftime(format='%d.%m.%Y')
        if Einstellungen.pdate:
            Ueberschrift += ' vom '+datumstr
        fname = Path(currentShoppingListName)
        fname = str(fname.name)
        if Einstellungen.pfilename:
            Ueberschrift += ' '+fname

        create_PDF.create_PDF_File(Ueberschrift, Convert_Einkaufszettel_2_PrintableList(ShoppingList), calculateTotal(), filename)

        message = MIMEMultipart()

        betreff = Einstellungen.mmessage
        if Einstellungen.mmessagedate:
            betreff += ' vom '+datumstr

        message['Subject'] = betreff
        message['From'] = Einstellungen.mfrom
        message['To'] = Einstellungen.mto

        text = MIMEText("siehe Anhang...")
        message.attach(text)

        sendfilename = Einstellungen.msendfilename
        dummy = Path(sendfilename)
        if Einstellungen.mdate:
            sendfilename = dummy.stem + '_'+datumstr+'.pdf'
        else:
            if dummy.suffix != '.pdf':
                sendfilename += '.pdf'

        with open(filename, 'rb') as opened:
            openedfile = opened.read()

        attachedfile = MIMEApplication(openedfile, _subtype="pdf", _encoder=encode_base64)
        attachedfile.add_header('content-disposition', 'attachment', filename=sendfilename)
        message.attach(attachedfile)

        hat_geklappt = True
        try:
            if Einstellungen.mSSL:
                adresse = Einstellungen.mserver+':'+str(Einstellungen.mport)
                server = smtplib.SMTP_SSL(adresse)
                server.ehlo()
                server.login(Einstellungen.musername, crypt.decode(Einstellungen.mpassword))
                server.sendmail(Einstellungen.mfrom, Einstellungen.mto, message.as_string())
                server.quit()
            else:
                server = smtplib.SMTP(Einstellungen.mserver, Einstellungen.mport)
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(Einstellungen.musername, crypt.decode(Einstellungen.mpassword))
                server.sendmail(Einstellungen.mfrom, Einstellungen.mto, message.as_string())
                server.close()
        except:
            hat_geklappt = False
            error = sys.exc_info()  # [1]

        msg = QtWidgets.QMessageBox()
        if hat_geklappt:
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setWindowTitle("Versenden per Email...")
            msg.setText("Das Versenden der Emailnachricht war erfolgreich! ")
        else:
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setWindowTitle("Fehler beim Versenden per Email...")
            msg.setText(str(error))
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        dummie = msg.exec_()

    def Einkaufszettel_save2PDF(self):
        global Einstellungen
        global ShoppingList

        Ueberschrift = Einstellungen.pHeadline
        the_time = datetime.now()
        datumstr = the_time.strftime(format='%d.%m.%Y')
        if Einstellungen.pdate:
            Ueberschrift += ' vom '+datumstr
        fname = Path(currentShoppingListName)
        fname = str(fname.name)
        if Einstellungen.pfilename:
            Ueberschrift += ' '+fname
        current_dir = str(Path.home() / 'Documents')
        filename = QtWidgets.QFileDialog.getSaveFileName(self, 'Einkaufszettel als PDF-Datei exportieren...', current_dir, 'Portable Document Format (*.pdf)', 'Portable Document Format (*.pdf)')
        fname = filename[0]
        if fname:
            dummy = Path(fname)
            if dummy.suffix != '.pdf':
                fname += '.pdf'

            create_PDF.create_PDF_File(Ueberschrift, Convert_Einkaufszettel_2_PrintableList(ShoppingList), calculateTotal(), fname)

    def printDialog(self):
        global Einstellungen
        filename = Einstellungen.ptempfilename

        filepath = str(Path(Einstellungen.ptempfilename).resolve().parent)
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)
        if dialog.exec_() == QPrintDialog.Accepted:
            images = convert_from_path(filename, dpi=300, output_folder=filepath)
            painter = QtGui.QPainter()
            painter.begin(printer)
            for i, image in enumerate(images):
                if i > 0:
                    printer.newPage()
                rect = painter.viewport()
                qtImage = ImageQt(image)
                qtImageScaled = qtImage.scaled(rect.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                painter.drawImage(rect, qtImageScaled)
            painter.end()

        if Einstellungen.pdelete:
            file2remove = Path(Einstellungen.ptempfilename)
            file2remove.unlink()

    def openfile(self):
        global Products
        global ShoppingList
        global currentShoppingListName
        global currentCatalogName
        global changeOccurred
        global isCategoryView
        if platform.system() == 'Linux':
            dir = str(Path.cwd())+'/save'
        elif platform.system() == 'Windows':
            dir = str(Path.home() / 'Documents\ezExpress\save')
        fname = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Einkaufszettel öffnen...', dir, 'Einkaufszettel (*.ekz)', 'Einkaufszettel (*.ekz)')
        fname = fname[0]
        if fname:
            isname = Path(fname)
            if isname.exists():
                savedata = load_file(fname)
                ShoppingList = savedata[0]
                Products = savedata[1]
                #isCategoryView = savedata[2]

                if savedata[2]:
                    self.setCheckCatView()
                else:
                    self.setCheckListView()

                self.catview_show()
                self.artview_showliste()
                self.Einkaufszettel_show()
                currentShoppingListName = fname
                changeOccurred = False
                Einkaufszettel.setWindowTitle('ezExpress - ' + isname.name + ' - ©2020 Alexander Mielke')

    def savefile(self):
        global Products
        global ShoppingList
        global currentShoppingListName
        global currentCatalogName
        global changeOccurred
        global isCategoryView

        if platform.system() == 'Linux':
            dir = str(Path.cwd())+'/save'
        elif platform.system() == 'Windows':
            dir = str(Path.home() / 'Documents\ezExpress\save')

        filename = QtWidgets.QFileDialog.getSaveFileName(self, 'Einkaufszettel speichern...', dir, 'Einkaufszettel (*.ekz)', 'Einkaufszettel (*.ekz)')
        fname = filename[0]
        if fname:
            dummy = Path(fname)
            if dummy.suffix != '.ekz':
                fname += '.ekz'
            isname = Path(fname)
            savedata = [ShoppingList, Products, isCategoryView]
            save_file(fname, savedata)
            currentShoppingListName = fname
            changeOccurred = False
            Einkaufszettel.setWindowTitle('ezExpress - ' + isname.name + ' - ©2020 Alexander Mielke')

    def fastsavefile(self):
        global Products
        global ShoppingList
        global currentShoppingListName
        global currentCatalogName
        global changeOccurred
        global isCategoryView
        if currentShoppingListName:
            iszettelname = Path(currentShoppingListName)
            if iszettelname.exists() and changeOccurred:
                fname = currentShoppingListName
                savedata = [ShoppingList, Products, isCategoryView]
                save_file(fname, savedata)
                changeOccurred = False
            elif changeOccurred and not iszettelname.exists():
                self.savefile()
        else:
            self.savefile()

    def opencatfile(self):
        global Products
        global CategoryList
        global currentCatalogName
        global changeOccurred
        if platform.system() == 'Linux':
            dir = str(Path.cwd())+'/catalogs'
        elif platform.system() == 'Windows':
            dir = str(Path.home() / 'Documents\ezExpress\catalogs')

        fname = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Produktkatalog importieren...', dir, 'Produktkatalog (*.epk)', 'Produktkatalog (*.epk)')
        fname = fname[0]
        if fname:
            isname = Path(fname)
            if isname.exists():
                Products = load_file(fname)
                CategoryList = Products.get_list()
                currentCatalogName = str(isname)
                changeOccurred = True
                self.catview_refresh()
                self.artview_showliste()

    def EinkaufcontextMenuEvent(self, event):
        menu = QtWidgets.QMenu(self)
        untermenu = menu.addMenu("Datei")
        newAction = untermenu.addAction("Neuer Einkaufszettel")
        openAction = untermenu.addAction("Einkaufszettel öffnen...")
        saveAction = untermenu.addAction("Einkaufszettel speichern")
        saveasAction = untermenu.addAction("Einkaufszettel speichern als...")
        printAction = menu.addAction("Einkaufszettel drucken...")
        pdfAction = menu.addAction("Speichern als PDF-Datei...")
        mailAction = menu.addAction("Senden per E-Mail")
        action = menu.exec_(self.einkauf.mapToGlobal(event.pos()))
        if action == newAction:
            self.Einkaufszettel_new()
        if action == openAction:
            self.openfile()
        if action == saveAction:
            self.fastsavefile()
        if action == saveasAction:
            self.savefile()
        if action == printAction:
            self.Einkaufszettel_print()
        if action == pdfAction:
            self.Einkaufszettel_save2PDF()
        if action == mailAction:
            self.Einkaufszettel_sendMail()

    def KatalogcontextMenuEvent(self, event):
        menu = QtWidgets.QMenu(self)
        importAction = menu.addAction("Katalog importieren...")
        editAction = menu.addAction("Katalog bearbeiten...")
        crawlAction = menu.addAction("Kataloge herunterladen...")
        action = menu.exec_(self.catview.mapToGlobal(event.pos()))
        if action == importAction:
            self.opencatfile()
        if action == editAction:
            show_ChangeCat()
        if action == crawlAction:
            show_PreislistenWebScraper()

    def ArtikelcontextMenuEvent(self, event):
        menu = QtWidgets.QMenu(self)
        searchAction = menu.addAction("Artikel suchen...")
        addAction = menu.addAction("Zum Einkaufszettel hinzufügen")
        action = menu.exec_(self.artview.mapToGlobal(event.pos()))
        if action == searchAction:
            show_SearchEngine()
        if action == addAction:
            self.Add_to_Einkaufszettel()

    def closeEvent(self, event):
        global Products
        global changeOccurred
        if changeOccurred:
            reply = QtWidgets.QMessageBox.question(self, 'Einkaufszettel beenden', 'Es wurden Änderungen vorgenommen! \n \n Möchten Sie den aktuellen Einkaufszettel speichern?        \n ',
                                                   QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel)
            if reply == QtWidgets.QMessageBox.Yes:
                self.savefile()
                save_settings()
                event.accept()
            elif reply == QtWidgets.QMessageBox.No:
                save_settings()
                event.accept()
            else:
                event.ignore()
        else:
            save_settings()
            event.accept()

###################################################################################
#       PyQt5 - Produktkatalog - Bearbeitungsfenster                              #
###################################################################################


class Ui_ChangeCat(QtWidgets.QWidget):

    def setupUi(self, ChangeCat):
        global currentCatalogName
        ChangeCat.setObjectName("ChangeCat")
        ChangeCat.resize(1059, 855)
        ChangeCat.setMinimumSize(1059, 855)
        ChangeCat.setMaximumSize(1059, 855)
        ChangeCat.setWindowModality(QtCore.Qt.ApplicationModal)
        ChangeCat.closeEvent = self.closeEvent
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ChangeCat.sizePolicy().hasHeightForWidth())
        ChangeCat.setSizePolicy(sizePolicy)
        #ChangeCat.setMinimumSize(QtCore.QSize(909, 705))
        #ChangeCat.setMaximumSize(QtCore.QSize(909, 705))

################################## Main #################################

        font = QtGui.QFont()
        font.setFamily("Arial")

        rows = 1
        columns = 3
        self.dartliste = QtWidgets.QTableWidget(ChangeCat)
        self.dartliste.setGeometry(QtCore.QRect(500, 50, 551, 749))
        self.dartliste.setFont(font)
        self.dartliste.viewport().setProperty("cursor", QtGui.QCursor(QtCore.Qt.IBeamCursor))
        self.dartliste.setObjectName("dartliste")
        self.dartliste.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.dartliste.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.dartliste.horizontalHeader().setHighlightSections(False)
        self.dartliste.clearContents()
        self.dartliste.setRowCount(rows)
        self.dartliste.setColumnCount(columns)
        self.dartliste.verticalHeader().setVisible(False)
        self.dartliste.setHorizontalHeaderLabels(['Artikelbezeichnung', 'Verpackung', 'Preis'])
        self.dartliste.setColumnWidth(0, 366)
        self.dartliste.setColumnWidth(1, 88)
        self.dartliste.setColumnWidth(2, 77)
        delegate = AlignRightDelegate(self.dartliste)
        self.dartliste.setItemDelegateForColumn(1, delegate)
        self.dartliste.setItemDelegateForColumn(2, delegate)
        self.dartliste.setEnabled(False)
        self.dartliste.horizontalHeader().setStretchLastSection(True)

        self.dcatview = QtWidgets.QListWidget(ChangeCat)
        self.dcatview.setGeometry(QtCore.QRect(10, 150, 476, 502))
        self.dcatview.setFont(font)
        self.dcatview.setObjectName("dcatview")
        self.dcatview.show()

        if platform.system() == 'Linux':
            dir = str(Path.cwd())+'/resources/ico/'
        elif platform.system() == 'Windows':
            dir = str(Path.cwd())+'\\resources\ico\\'

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(dir+"sort_abc.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(dir+"delete.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(dir+"back.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(dir+"up.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(dir+"save_as.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(dir+"down.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(dir+"open.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(dir+"new.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(dir+"save.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap(dir+"deletelist.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.dbutton_sort_abc = QtWidgets.QPushButton(ChangeCat)
        self.dbutton_sort_abc.setGeometry(QtCore.QRect(435, 662, 51, 31))
        self.dbutton_sort_abc.setText("")
        self.dbutton_sort_abc.setIcon(icon)
        self.dbutton_sort_abc.setIconSize(QtCore.QSize(20, 20))
        self.dbutton_sort_abc.setObjectName("dbutton_sort_abc")

        self.dbutton_up = QtWidgets.QPushButton(ChangeCat)
        self.dbutton_up.setGeometry(QtCore.QRect(10, 662, 51, 31))
        self.dbutton_up.setText("")
        self.dbutton_up.setIcon(icon3)
        self.dbutton_up.setIconSize(QtCore.QSize(20, 20))
        self.dbutton_up.setObjectName("dbutton_up")

        self.dbutton_down = QtWidgets.QPushButton(ChangeCat)
        self.dbutton_down.setGeometry(QtCore.QRect(60, 662, 51, 31))
        self.dbutton_down.setText("")
        self.dbutton_down.setIcon(icon5)
        self.dbutton_down.setIconSize(QtCore.QSize(20, 20))
        self.dbutton_down.setObjectName("dbutton_down")

        self.dbutton_delete = QtWidgets.QPushButton(ChangeCat)
        self.dbutton_delete.setGeometry(QtCore.QRect(120, 662, 51, 31))
        self.dbutton_delete.setText("")
        self.dbutton_delete.setIcon(icon1)
        self.dbutton_delete.setIconSize(QtCore.QSize(18, 18))
        self.dbutton_delete.setObjectName("dbutton_delete")

        self.dbutton_artup = QtWidgets.QPushButton(ChangeCat)
        self.dbutton_artup.setGeometry(QtCore.QRect(500, 808, 51, 36))
        self.dbutton_artup.setText("")
        self.dbutton_artup.setIcon(icon3)
        self.dbutton_artup.setIconSize(QtCore.QSize(20, 20))
        self.dbutton_artup.setObjectName("dbutton_artup")

        self.dbutton_artdown = QtWidgets.QPushButton(ChangeCat)
        self.dbutton_artdown.setGeometry(QtCore.QRect(550, 808, 51, 36))
        self.dbutton_artdown.setText("")
        self.dbutton_artdown.setIcon(icon5)
        self.dbutton_artdown.setIconSize(QtCore.QSize(20, 20))
        self.dbutton_artdown.setObjectName("dbutton_artdown")

        self.dbutton_artdelete = QtWidgets.QPushButton(ChangeCat)
        self.dbutton_artdelete.setGeometry(QtCore.QRect(610, 808, 51, 36))
        self.dbutton_artdelete.setText("")
        self.dbutton_artdelete.setIcon(icon1)
        self.dbutton_artdelete.setIconSize(QtCore.QSize(18, 18))
        self.dbutton_artdelete.setObjectName("dbutton_artdelete")

        self.dbutton_delList = QtWidgets.QPushButton(ChangeCat)
        self.dbutton_delList.setGeometry(QtCore.QRect(700, 808, 151, 36))
        self.dbutton_delList.setText(" Liste löschen")
        self.dbutton_delList.setIcon(icon9)
        self.dbutton_delList.setIconSize(QtCore.QSize(22, 22))
        self.dbutton_delList.setObjectName("dbutton_delList")

        self.dbutton_ArtListenSort = QtWidgets.QPushButton(ChangeCat)
        self.dbutton_ArtListenSort.setGeometry(QtCore.QRect(896, 808, 151, 36))
        self.dbutton_ArtListenSort.setText(" Sortieren")
        self.dbutton_ArtListenSort.setIcon(icon)
        self.dbutton_ArtListenSort.setIconSize(QtCore.QSize(20, 20))
        self.dbutton_ArtListenSort.setObjectName("dbutton_ArtListenSort")

        self.dedit_newcat = QtWidgets.QLineEdit(ChangeCat)
        self.dedit_newcat.setGeometry(QtCore.QRect(11, 808, 280, 32))
        self.dedit_newcat.setObjectName("dedit_newcat")
        self.dedit_newcat.setMaxLength(30)

        self.dbutton_rename = QtWidgets.QPushButton(ChangeCat)
        self.dbutton_rename.setGeometry(QtCore.QRect(300, 808, 186, 34))
        self.dbutton_rename.setObjectName("dbutton_rename")

        self.dedit_addcat = QtWidgets.QLineEdit(ChangeCat)
        self.dedit_addcat.setGeometry(QtCore.QRect(11, 712, 474, 32))
        self.dedit_addcat.setObjectName("dedit_addcat")
        self.dedit_addcat.setMaxLength(30)

        self.dbutton_addSibling = QtWidgets.QPushButton(ChangeCat)
        self.dbutton_addSibling.setGeometry(QtCore.QRect(10, 753, 238, 36))
        self.dbutton_addSibling.setObjectName("dbutton_addSibling")

        self.dbutton_addChild = QtWidgets.QPushButton(ChangeCat)
        self.dbutton_addChild.setGeometry(QtCore.QRect(248, 753, 238, 36))
        self.dbutton_addChild.setObjectName("dbutton_addChild")

        self.line = QtWidgets.QLabel(ChangeCat)
        self.line.setGeometry(QtCore.QRect(10, 702, 475, 1))
        self.line.setAutoFillBackground(False)
        self.line.setStyleSheet("background:darkred")
        self.line.setObjectName("line")

        self.line2 = QtWidgets.QLabel(ChangeCat)
        self.line2.setGeometry(QtCore.QRect(10, 798, 475, 1))
        self.line2.setAutoFillBackground(False)
        self.line2.setStyleSheet("background:darkred")
        self.line2.setObjectName("line2")

        self.dshowcat = QtWidgets.QLineEdit(ChangeCat)
        self.dshowcat.setEnabled(False)
        self.dshowcat.setStyleSheet("""QLineEdit { font-weight: bold; background-color: darkgreen; color: beige }""")
        self.dshowcat.setAlignment(QtCore.Qt.AlignCenter)
        self.dshowcat.setGeometry(QtCore.QRect(502, 10, 546, 37))
        self.dshowcat.setObjectName("dshowcat")

        self.dshowKatalog = QtWidgets.QLineEdit(ChangeCat)
        self.dshowKatalog.setEnabled(False)
        self.dshowKatalog.setStyleSheet("""QLineEdit { font-weight: bold; background-color: darkslateblue; color: gold }""")
        self.dshowKatalog.setAlignment(QtCore.Qt.AlignCenter)
        self.dshowKatalog.setGeometry(QtCore.QRect(10, 100, 476, 37))
        self.dshowKatalog.setObjectName("dshowKatalog")

        self.dbutton_new = QtWidgets.QPushButton(ChangeCat)
        self.dbutton_new.setGeometry(QtCore.QRect(10, 10, 235, 41))
        self.dbutton_new.setText(" Neu")
        self.dbutton_new.setIcon(icon7)
        self.dbutton_new.setIconSize(QtCore.QSize(28, 28))
        self.dbutton_new.setObjectName("dbutton_new")

        self.dbutton_open = QtWidgets.QPushButton(ChangeCat)
        self.dbutton_open.setGeometry(QtCore.QRect(246, 10, 240, 41))
        self.dbutton_open.setText(" Öffnen")
        self.dbutton_open.setIcon(icon6)
        self.dbutton_open.setIconSize(QtCore.QSize(28, 28))
        self.dbutton_open.setObjectName("dbutton_open")

        self.dbutton_save = QtWidgets.QPushButton(ChangeCat)
        self.dbutton_save.setGeometry(QtCore.QRect(10, 52, 157, 41))
        self.dbutton_save.setText(" Speichern")
        self.dbutton_save.setIcon(icon8)
        self.dbutton_save.setIconSize(QtCore.QSize(24, 24))
        self.dbutton_save.setObjectName("dbutton_save")

        self.dbutton_saveas = QtWidgets.QPushButton(ChangeCat)
        self.dbutton_saveas.setGeometry(QtCore.QRect(168, 52, 157, 41))
        self.dbutton_saveas.setText(" Speichern als")
        self.dbutton_saveas.setIcon(icon4)
        self.dbutton_saveas.setIconSize(QtCore.QSize(24, 24))
        self.dbutton_saveas.setObjectName("dbutton_saveas")

        self.dbutton_back = QtWidgets.QPushButton(ChangeCat)
        self.dbutton_back.setGeometry(QtCore.QRect(325, 52, 162, 41))
        self.dbutton_back.setText(" Fertig")
        self.dbutton_back.setIcon(icon2)
        self.dbutton_back.setIconSize(QtCore.QSize(26, 26))
        self.dbutton_back.setObjectName("dbutton_back")

        self.catview_show()

        self.retranslateUi(ChangeCat)

############################## Signals & Slots ##########################

        self.dbutton_back.clicked.connect(ChangeCat.close)
        self.dbutton_delete.clicked.connect(self.catview_delete)
        self.dbutton_sort_abc.clicked.connect(self.catview_sortTree)
        self.dbutton_up.clicked.connect(self.catview_moveUp)
        self.dbutton_down.clicked.connect(self.catview_moveDown)
        self.dcatview.clicked.connect(self.artview_show)
        self.dcatview.doubleClicked.connect(self.catview_folding)
        self.dartliste.itemChanged.connect(self.artview_refreshItem)
        self.dbutton_addChild.clicked.connect(self.catview_addChild)
        self.dbutton_addSibling.clicked.connect(self.catview_addSibling)
        self.dbutton_save.clicked.connect(self.savesamefile)
        self.dbutton_saveas.clicked.connect(self.savefile)
        self.dbutton_open.clicked.connect(self.openfile)
        self.dbutton_new.clicked.connect(self.catview_new)
        self.dbutton_ArtListenSort.clicked.connect(self.artview_sort)
        self.dbutton_artup.clicked.connect(self.artview_moveUp)
        self.dbutton_artdown.clicked.connect(self.artview_moveDown)
        self.dbutton_artdelete.clicked.connect(self.artview_deleteEntry)
        self.dbutton_delList.clicked.connect(self.artview_newList)
        self.dbutton_rename.clicked.connect(self.catview_rename)

        self.dedit_newcat.setText('')
        self.dedit_addcat.setText('')

        QtCore.QMetaObject.connectSlotsByName(ChangeCat)

################################ Translations ###########################

    def retranslateUi(self, ChangeCat):
        ChangeCat.setWindowTitle(QtCore.QCoreApplication.translate("ChangeCat", "Katalog bearbeiten"))
        _translate = QtCore.QCoreApplication.translate
        self.dbutton_addSibling.setText(_translate("ChangeCat", "Nebenkategorie hinzufügen"))
        self.dbutton_addChild.setText(_translate("ChangeCat", "Unterkategorie hinzufügen"))
        self.dbutton_rename.setText(_translate("ChangeCat", "Umbenennen"))
        self.dbutton_ArtListenSort.setToolTip(_translate("ChangeCat", "Artikelliste Sortieren"))
        self.dbutton_delete.setToolTip(_translate("ChangeCat", "Eintrag löschen"))
        self.dbutton_sort_abc.setToolTip(_translate("ChangeCat", "Die Kategorien des Katalogs alphabetisch sortieren"))
        self.dbutton_back.setToolTip(_translate("ChangeCat", "Fertig"))
        self.dbutton_back.setShortcut(_translate("ChangeCat", "Ctrl+X"))
        self.dbutton_up.setToolTip(_translate("ChangeCat", "Eins nach oben"))
        self.dbutton_save.setToolTip(_translate("ChangeCat", "Katalog speichern"))
        self.dbutton_saveas.setToolTip(_translate("ChangeCat", "Katalog speichern unter anderem Namen"))
        self.dbutton_down.setToolTip(_translate("ChangeCat", "Eins nach unten"))
        self.dbutton_open.setToolTip(_translate("ChangeCat", "Katalog öffnen"))
        self.dbutton_new.setToolTip(_translate("ChangeCat", "Neuen Produktkatalog erstellen"))
        self.dbutton_delList.setToolTip(_translate("ChangeCat", "Artikelliste löschen"))
        self.dbutton_artup.setToolTip(_translate("ChangeCat", "Artikel um eine Position nach oben verschieben"))
        self.dbutton_artdown.setToolTip(_translate("ChangeCat", "Artikel um eine Position nach unten verschieben"))
        self.dbutton_artdelete.setToolTip(_translate("ChangeCat", "Artikel löschen"))
        self.dbutton_rename.setToolTip(_translate("ChangeCat", "gewählte Kategorie umbenennen"))

############################## Methods/Functions ########################

    def catview_show(self):
        global Katalog
        global CategoryList
        global currentCatalogName
        CategoryList = Katalog.get_list()
        self.dshowKatalog.setText(str(Path(currentCatalogName).stem))
        self.catview_refresh()

    def catview_new(self):
        global Katalog
        global CategoryList
        global currentListIndex
        global catchangeOccurred
        global currentCatalogName
        global currentArtikelList

        if platform.system() == 'Linux':
            current_dir = str(Path.cwd())+'/catalogs'
        elif platform.system() == 'Windows':
            current_dir = str(Path.home() / 'Documents\ezExpress\catalogs')

        filename = QtWidgets.QFileDialog.getSaveFileName(self, 'Neuen Produktkatalog anlegen', current_dir, 'Produktkatalog (*.epk)', 'Produktkatalog (*.epk)')
        if filename[0] != '':
            catchangeOccurred = True
            currentListIndex = 0
            currentArtikelList = ''
            self.dshowcat.setText('')

            self.dedit_newcat.setText('')
            self.dedit_addcat.setText('')

            Katalog = TreeNode(0, 'Produkte')
            CategoryList = Katalog.get_list()

            fname = filename[0]

            dummy = Path(fname)
            if dummy.suffix != '.epk':
                fname += '.epk'
            save_file(fname, Katalog)

            currentCatalogName = fname

            self.catview_refresh()
            self.artview_refresh()

    def catview_folding(self):
        global Katalog
        global CategoryList
        itemnumber = self.dcatview.currentRow()
        index = CategoryList[itemnumber][0]
        Node = Katalog.find_indexnode(index)
        Node.aufgeklappt = not Node.aufgeklappt
        CategoryList = Katalog.get_list()
        self.catview_refresh()

    def catview_refresh(self):
        global CategoryList
        global currentCatalogName
        self.dcatview.clear()
        for eintrag in CategoryList:
            self.dcatview.addItem(eintrag[1])
        self.dshowKatalog.setText(str(Path(currentCatalogName).stem))

    def catview_delete(self):
        global Katalog
        global CategoryList
        global catchangeOccurred
        itemnumber = self.dcatview.currentRow()
        if itemnumber >= 0:
            index = CategoryList[itemnumber][0]
            Katalog.delete_index(index)
            CategoryList = Katalog.get_list()
            self.catview_refresh()
            catchangeOccurred = True

    def catview_rename(self):
        global Katalog
        global CategoryList
        global catchangeOccurred
        itemnumber = self.dcatview.currentRow()
        if itemnumber >= 0:
            index = CategoryList[itemnumber][0]
            Node = Katalog.find_indexnode(index)
            alter_Name = Node.data
            neuer_Name = self.dedit_newcat.text()
            if neuer_Name != alter_Name:
                Node.data = neuer_Name
                CategoryList = Katalog.get_list()
                self.catview_refresh()
                catchangeOccurred = True
                self.dcatview.setCurrentRow(itemnumber)

    def catview_sortTree(self):
        global Katalog
        global CategoryList
        global catchangeOccurred
        if len(CategoryList) > 0:
            Katalog.sort_Tree(Katalog)
            catchangeOccurred = True
            CategoryList = Katalog.get_list()
            self.catview_refresh()

    def catview_addChild(self):
        global Katalog
        global CategoryList
        global catchangeOccurred
        dat = self.dedit_addcat.text()
        if dat != '':
            if (self.dcatview.currentRow() >= 0):
                itemnumber = self.dcatview.currentRow()
                index = CategoryList[itemnumber][0]
                Node = Katalog.find_indexnode(index)

                idx = (Node.index*100)+len(Node.children)+1

                neu = TreeNode(idx, dat)
                Node.add_child(neu)
                Node.aufgeklappt = True
                self.dedit_addcat.setText('')
                catchangeOccurred = True
            elif Katalog.is_empty():
                neu = TreeNode(1, dat)
                Katalog.add_child(neu)
                self.dedit_addcat.setText('')
                catchangeOccurred = True
            CategoryList = Katalog.get_list()
            self.catview_refresh()
            self.artview_refresh()
            self.dartliste.setEnabled(False)

    def catview_addSibling(self):
        global Katalog
        global CategoryList
        global catchangeOccurred
        dat = self.dedit_addcat.text()
        if dat != '':
            if (self.dcatview.currentRow() >= 0):
                itemnumber = self.dcatview.currentRow()
                index = CategoryList[itemnumber][0]
                Node = Katalog.find_indexnode(index)

                idx = (Node.parent.index*100)+len(Node.parent.children)+1

                neu = TreeNode(idx, dat)
                Node.add_sibling(neu)
                self.dedit_addcat.setText('')
                catchangeOccurred = True
            elif Katalog.is_empty():
                neu = TreeNode(1, dat)
                Katalog.add_child(neu)
                self.dedit_addcat.setText('')
                catchangeOccurred = True

            CategoryList = Katalog.get_list()
            self.catview_refresh()
            self.artview_refresh()
            self.dartliste.setEnabled(False)

    def catview_moveUp(self):
        global Katalog
        global CategoryList
        global catchangeOccurred
        if self.dcatview.currentRow() >= 0:
            itemnumber = self.dcatview.currentRow()
            index = CategoryList[itemnumber][0]
            Node = Katalog.find_indexnode(index)
            Katalog.move_node(Node, 'UP')
            CategoryList = Katalog.get_list()
            self.catview_refresh()
            catchangeOccurred = True
            self.dcatview.setCurrentRow(itemnumber-1)

    def catview_moveDown(self):
        global Katalog
        global CategoryList
        global catchangeOccurred
        if self.dcatview.currentRow() >= 0:
            itemnumber = self.dcatview.currentRow()
            index = CategoryList[itemnumber][0]
            Node = Katalog.find_indexnode(index)
            Katalog.move_node(Node, 'DOWN')
            CategoryList = Katalog.get_list()
            self.catview_refresh()
            catchangeOccurred = True
            self.dcatview.setCurrentRow(itemnumber+1)

    def artview_refresh(self):
        global currentArtikelList
        self.dartliste.blockSignals(True)
        self.dartliste.setRowCount(0)
        if currentArtikelList != []:
            for i in range(len(currentArtikelList)):
                self.dartliste.insertRow(i)
                self.dartliste.setItem(i, 0, QtWidgets.QTableWidgetItem(currentArtikelList[i][0]))
                self.dartliste.setItem(i, 1, QtWidgets.QTableWidgetItem(currentArtikelList[i][1]))
                self.dartliste.setItem(i, 2, QtWidgets.QTableWidgetItem(convert_f2s(currentArtikelList[i][2])))
        self.dartliste.insertRow(len(currentArtikelList))
        self.dartliste.blockSignals(False)

    def artview_show(self):
        global Katalog
        global CategoryList
        global currentListIndex
        global currentArtikelList
        if self.dcatview.currentRow() >= 0:
            currentListIndex = CategoryList[self.dcatview.currentRow()][0]
            Node = Katalog.find_indexnode(currentListIndex)
            self.dedit_newcat.setText(Node.data)

            if not Node.is_leaf():
                currentArtikelList = []
                self.dartliste.setEnabled(False)
                self.dshowcat.setText('')
            else:
                self.dartliste.setEnabled(True)
                currentArtikelList = Node.liste
                self.dshowcat.setText(Node.data)
            self.artview_refresh()

    def artview_sort(self):
        global Katalog
        global catchangeOccurred
        global currentListIndex
        if self.dshowcat.text() != '':
            self.dartliste.blockSignals(True)
            self.dartliste.clearContents()
            Nodey = Katalog.find_indexnode(currentListIndex)
            Nodey.sort_list()
            catchangeOccurred = True
            ArtListe = Nodey.liste
            for i in range(len(ArtListe)):
                for j in range(3):
                    if j == 2:
                        NewItem = QtWidgets.QTableWidgetItem(convert_f2s(ArtListe[i][j]))
                    else:
                        NewItem = QtWidgets.QTableWidgetItem(ArtListe[i][j])
                    self.dartliste.setItem(i, j, NewItem)
            self.dartliste.blockSignals(False)

    def artview_Item2List(self):
        global catchangeOccurred
        catchangeOccurred = True
        worklist = []
        for i in range(self.dartliste.rowCount()):
            if self.dartliste.item(i, 0):
                eintrag1 = self.dartliste.item(i, 0).text()
            else:
                eintrag1 = ''

            if self.dartliste.item(i, 1):
                eintrag2 = self.dartliste.item(i, 1).text()
            else:
                eintrag2 = ''

            if (self.dartliste.item(i, 2)) and (eintrag1 or eintrag2):
                eintrag3 = convert_s2f(self.dartliste.item(i, 2).text())
                worklist.append([eintrag1[:45], eintrag2[:8], eintrag3])

            else:
                eintrag3 = ''
                if eintrag1 or eintrag2:
                    eintrag3 = 0.0
                worklist.append([eintrag1, eintrag2, eintrag3])
        return worklist

    def artview_refreshItem(self):
        global Katalog
        global currentListIndex
        global catchangeOccurred
        catchangeOccurred = True
        Nodey = Katalog.find_indexnode(currentListIndex)
        aktrow = self.dartliste.currentRow()
        aktcol = self.dartliste.currentColumn()
        Nodey.liste = self.artview_Item2List()
        self.dartliste.blockSignals(True)
        wat = Nodey.liste[aktrow]
        self.dartliste.setItem(aktrow, 0, QtWidgets.QTableWidgetItem(wat[0]))
        self.dartliste.setItem(aktrow, 1, QtWidgets.QTableWidgetItem(wat[1]))
        self.dartliste.setItem(aktrow, 2, QtWidgets.QTableWidgetItem(convert_f2s(wat[2])))

        if aktcol < 2:
            self.dartliste.setCurrentCell(aktrow, aktcol+1)
        else:
            if aktrow == self.dartliste.rowCount()-1:
                self.dartliste.insertRow(aktrow+1)
                self.dartliste.setCurrentCell(aktrow+1, 0)

        self.dartliste.blockSignals(False)

    def artview_moveUp(self):
        global Katalog
        global currentListIndex
        global catchangeOccurred
        global currentArtikelList
        aktrow = self.dartliste.currentRow()
        aktcul = self.dartliste.currentColumn()
        Nodey = Katalog.find_indexnode(currentListIndex)
        if (aktrow > 0) and (aktrow < (len(Nodey.liste))):
            catchangeOccurred = True
            temp = Nodey.liste[aktrow-1]
            Nodey.liste[aktrow-1] = Nodey.liste[aktrow]
            Nodey.liste[aktrow] = temp
            currentArtikelList = Nodey.liste
            self.artview_refresh()
            self.dartliste.setCurrentCell(aktrow-1, aktcul)

    def artview_moveDown(self):
        global Katalog
        global currentListIndex
        global catchangeOccurred
        global currentArtikelList
        aktrow = self.dartliste.currentRow()
        aktcul = self.dartliste.currentColumn()
        Nodey = Katalog.find_indexnode(currentListIndex)
        if (aktrow >= 0) and (aktrow < (len(Nodey.liste)-1)):
            catchangeOccurred = True

            temp = Nodey.liste[aktrow+1]
            Nodey.liste[aktrow+1] = Nodey.liste[aktrow]
            Nodey.liste[aktrow] = temp

            currentArtikelList = Nodey.liste
            self.artview_refresh()
            self.dartliste.setCurrentCell(aktrow+1, aktcul)

    def artview_deleteEntry(self):
        global Katalog
        global currentListIndex
        global catchangeOccurred
        global currentArtikelList
        aktrow = self.dartliste.currentRow()
        Nodey = Katalog.find_indexnode(currentListIndex)
        if (aktrow >= 0) and (aktrow <= (len(Nodey.liste)-1)):
            catchangeOccurred = True
            del Nodey.liste[aktrow]
            currentArtikelList = Nodey.liste
            self.artview_refresh()

    def artview_newList(self):
        global Katalog
        global currentListIndex
        global catchangeOccurred
        global currentArtikelList
        catchangeOccurred = True
        Nodey = Katalog.find_indexnode(currentListIndex)
        Nodey.liste = []
        currentArtikelList = Nodey.liste
        self.artview_refresh()

    def openfile(self):
        global Katalog
        global CategoryList
        global currentCatalogName
        global catchangeOccurred

        if platform.system() == 'Linux':
            home_dir = str(Path.cwd())+'/catalogs'
        elif platform.system() == 'Windows':
            home_dir = str(Path.home() / 'Documents\ezExpress\catalogs')

        fname = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Produktkatalog öffnen...', home_dir, 'Produktkatalog (*.epk)', 'Produktkatalog (*.epk)')
        fname = fname[0]
        if fname:
            isname = Path(fname)
            if isname.exists():
                Katalog = load_file(fname)
                CategoryList = Katalog.get_list()
                currentCatalogName = fname
                self.catview_refresh()
                self.artview_refresh()
                catchangeOccurred = True

    def savefile(self):
        global Katalog
        global CategoryList
        global currentCatalogName
        global catchangeOccurred

        if platform.system() == 'Linux':
            current_dir = str(Path.cwd())+'/catalogs'
        elif platform.system() == 'Windows':
            current_dir = str(Path.home() / 'Documents\ezExpress\catalogs')
        filename = QtWidgets.QFileDialog.getSaveFileName(self, 'Produktkatalog speichern...', current_dir, 'Produktkatalog (*.epk)', 'Produktkatalog (*.epk)')
        fname = filename[0]
        if fname:
            dummy = Path(fname)
            if dummy.suffix != '.epk':
                fname += '.epk'
            save_file(fname, Katalog)
            CategoryList = Katalog.get_list()
            currentCatalogName = fname
            self.catview_refresh()
            catchangeOccurred = False

    def savesamefile(self):
        global Katalog
        global CategoryList
        global currentCatalogName
        global catchangeOccurred

        if currentCatalogName != '':
            fname = currentCatalogName
            if Path(fname).exists():
                dummy = Path(fname)
                if dummy.suffix != '.epk':
                    fname += '.epk'
                save_file(fname, Katalog)
                CategoryList = Katalog.get_list()
                currentCatalogName = fname
                self.catview_refresh()
                catchangeOccurred = False
        else:
            self.savefile()

    def closeEvent(self, event):
        global Products
        global Katalog
        global catchangeOccurred
        global changeOccurred
        if catchangeOccurred:
            reply = QtWidgets.QMessageBox.question(self, 'Änderungen vorgenommen!', 'Möchten Sie den Produktkatalog speichern, verwerfen oder abbrechen?',
                                                   QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Discard | QtWidgets.QMessageBox.Cancel, QtWidgets.QMessageBox.Save)
            if reply == QtWidgets.QMessageBox.Save:
                changeOccurred = True
                self.savesamefile()
                Products = deepcopy(Katalog)
                #Katalog = []
                Einkaufszettel_show()
                event.accept()
            elif reply == QtWidgets.QMessageBox.Discard:
                Katalog = deepcopy(Products)
                Einkaufszettel_show()
                event.accept()
            elif reply == QtWidgets.QMessageBox.Cancel:
                event.ignore()
        else:
            Products = deepcopy(Katalog)
            Einkaufszettel_show()
            event.accept()


###################################################################################
#       PyQt5 - Settings - Einstellungenfenster                                   #
###################################################################################


class Ui_SetEinstellungen(object):

    def setupUi(self, SetEinstellungen):
        SetEinstellungen.setObjectName("SetEinstellungen")
        SetEinstellungen.setWindowModality(QtCore.Qt.ApplicationModal)
        SetEinstellungen.resize(790, 548)
        SetEinstellungen.setMinimumSize(790, 548)
        SetEinstellungen.setMaximumSize(790, 548)

############################ Groupbox (Print) ###########################

        self.groupBox = QtWidgets.QGroupBox(SetEinstellungen)
        self.groupBox.setGeometry(QtCore.QRect(10, 10, 771, 151))
        self.groupBox.setObjectName("groupBox")

        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setGeometry(QtCore.QRect(20, 30, 101, 31))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setGeometry(QtCore.QRect(20, 100, 101, 31))
        self.label_2.setObjectName("label_2")

        self.Edit_Headline = QtWidgets.QLineEdit(self.groupBox)
        self.Edit_Headline.setGeometry(QtCore.QRect(120, 30, 441, 32))
        self.Edit_Headline.setObjectName("Edit_Headline")
        self.check_Headline_plusDate = QtWidgets.QCheckBox(self.groupBox)
        self.check_Headline_plusDate.setGeometry(QtCore.QRect(580, 30, 151, 31))
        self.check_Headline_plusDate.setObjectName("check_Headline_plusDate")
        self.check_Headline_plusFilename = QtWidgets.QCheckBox(self.groupBox)
        self.check_Headline_plusFilename.setGeometry(QtCore.QRect(580, 60, 121, 31))
        self.check_Headline_plusFilename.setObjectName("check_Headline_plusFilename")

        self.Edit_Tempfile = QtWidgets.QLineEdit(self.groupBox)
        self.Edit_Tempfile.setGeometry(QtCore.QRect(120, 100, 441, 32))
        self.Edit_Tempfile.setObjectName("Edit_Tempfile")
        self.check_DeleteTemp = QtWidgets.QCheckBox(self.groupBox)
        self.check_DeleteTemp.setGeometry(QtCore.QRect(580, 90, 131, 51))
        self.check_DeleteTemp.setObjectName("check_DeleteTemp")

############################ Groupbox2 (Mail) ###########################

        self.groupBox_2 = QtWidgets.QGroupBox(SetEinstellungen)
        self.groupBox_2.setGeometry(QtCore.QRect(10, 170, 771, 331))
        self.groupBox_2.setObjectName("groupBox_2")

        self.label_3 = QtWidgets.QLabel(self.groupBox_2)
        self.label_3.setGeometry(QtCore.QRect(20, 30, 141, 31))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.groupBox_2)
        self.label_4.setGeometry(QtCore.QRect(20, 180, 151, 31))
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(self.groupBox_2)
        self.label_5.setGeometry(QtCore.QRect(20, 230, 141, 31))
        self.label_5.setObjectName("label_5")
        self.label_6 = QtWidgets.QLabel(self.groupBox_2)
        self.label_6.setGeometry(QtCore.QRect(20, 80, 111, 31))
        self.label_6.setObjectName("label_6")
        self.label_7 = QtWidgets.QLabel(self.groupBox_2)
        self.label_7.setGeometry(QtCore.QRect(570, 80, 41, 31))
        self.label_7.setObjectName("label_7")
        self.label_8 = QtWidgets.QLabel(self.groupBox_2)
        self.label_8.setGeometry(QtCore.QRect(20, 280, 141, 31))
        self.label_8.setObjectName("label_8")
        self.label_9 = QtWidgets.QLabel(self.groupBox_2)
        self.label_9.setGeometry(QtCore.QRect(20, 130, 121, 31))
        self.label_9.setObjectName("label_9")
        self.label_10 = QtWidgets.QLabel(self.groupBox_2)
        self.label_10.setGeometry(QtCore.QRect(440, 130, 81, 31))
        self.label_10.setObjectName("label_10")

        self.Edit_From = QtWidgets.QLineEdit(self.groupBox_2)
        self.Edit_From.setGeometry(QtCore.QRect(170, 30, 391, 32))
        self.Edit_From.setObjectName("Edit_From")

        self.Edit_Servername = QtWidgets.QLineEdit(self.groupBox_2)
        self.Edit_Servername.setGeometry(QtCore.QRect(170, 80, 391, 32))
        self.Edit_Servername.setObjectName("Edit_Servername")
        self.Edit_ServerPort = QtWidgets.QLineEdit(self.groupBox_2)
        self.Edit_ServerPort.setGeometry(QtCore.QRect(620, 80, 81, 32))
        self.Edit_ServerPort.setObjectName("Edit_ServerPort")
        self.check_SSL = QtWidgets.QCheckBox(self.groupBox_2)
        self.check_SSL.setGeometry(QtCore.QRect(710, 80, 51, 31))
        self.check_SSL.setObjectName("check_SSL")

        self.Edit_Username = QtWidgets.QLineEdit(self.groupBox_2)
        self.Edit_Username.setGeometry(QtCore.QRect(170, 130, 261, 32))
        self.Edit_Username.setObjectName("Edit_Username")
        self.Edit_Userpass = QtWidgets.QLineEdit(self.groupBox_2)
        self.Edit_Userpass.setGeometry(QtCore.QRect(520, 130, 241, 32))
        self.Edit_Userpass.setEchoMode(QtWidgets.QLineEdit.Password)
        self.Edit_Userpass.setObjectName("Edit_Userpass")

        self.Edit_To = QtWidgets.QLineEdit(self.groupBox_2)
        self.Edit_To.setGeometry(QtCore.QRect(170, 180, 391, 32))
        self.Edit_To.setObjectName("Edit_To")

        self.Edit_Message = QtWidgets.QLineEdit(self.groupBox_2)
        self.Edit_Message.setGeometry(QtCore.QRect(170, 230, 426, 32))
        self.Edit_Message.setObjectName("Edit_Message")
        self.check_MessageDate = QtWidgets.QCheckBox(self.groupBox_2)
        self.check_MessageDate.setGeometry(QtCore.QRect(610, 230, 151, 31))
        self.check_MessageDate.setObjectName("check_MessageDate")

        self.Edit_SendFileName = QtWidgets.QLineEdit(self.groupBox_2)
        self.Edit_SendFileName.setGeometry(QtCore.QRect(170, 280, 426, 32))
        self.Edit_SendFileName.setObjectName("Edit_SendFileName")
        self.check_SendFileName_plusDate = QtWidgets.QCheckBox(self.groupBox_2)
        self.check_SendFileName_plusDate.setGeometry(QtCore.QRect(610, 280, 151, 31))
        self.check_SendFileName_plusDate.setObjectName("check_SendFileName_plusDate")

################################ Buttons ################################

        self.Button_Save = QtWidgets.QPushButton(SetEinstellungen)
        self.Button_Save.setGeometry(QtCore.QRect(590, 510, 95, 32))
        self.Button_Save.setObjectName("Button_Save")
        self.Button_Back = QtWidgets.QPushButton(SetEinstellungen)
        self.Button_Back.setGeometry(QtCore.QRect(690, 510, 95, 32))
        self.Button_Back.setObjectName("Button_Back")

        self.retranslateUi(SetEinstellungen)

############################# Signals & Slots ###########################

        self.Button_Back.clicked.connect(SetEinstellungen.close)
        self.Button_Save.clicked.connect(self.fertig)
        QtCore.QMetaObject.connectSlotsByName(SetEinstellungen)

################################ Translations ###########################

    def retranslateUi(self, SetEinstellungen):
        _translate = QtCore.QCoreApplication.translate
        SetEinstellungen.setWindowTitle(_translate("SetEinstellungen", "Einstellungen"))
        self.groupBox.setTitle(_translate("SetEinstellungen", "Druckeinstellungen"))
        self.label.setText(_translate("SetEinstellungen", "Überschrift :"))
        self.Edit_Headline.setText(_translate("SetEinstellungen", "Einkaufszettel"))
        self.check_Headline_plusDate.setText(_translate("SetEinstellungen", "+ aktuelles Datum"))
        self.check_Headline_plusFilename.setText(_translate("SetEinstellungen", "+ Dateiname"))
        self.label_2.setText(_translate("SetEinstellungen", "Temp. Datei :"))
        self.check_DeleteTemp.setText(_translate("SetEinstellungen", "löschen nach\nDruckvorgang"))
        self.groupBox_2.setTitle(_translate("SetEinstellungen", "E-maileinstellungen"))
        self.label_3.setText(_translate("SetEinstellungen", "Absenderadresse :"))
        self.label_4.setText(_translate("SetEinstellungen", "Empfängeradresse :"))
        self.label_5.setText(_translate("SetEinstellungen", "Email Beftreff :"))
        self.label_8.setText(_translate("SetEinstellungen", "ges. Dateiname :"))
        self.check_SendFileName_plusDate.setText(_translate("SetEinstellungen", "+ aktuelles Datum"))
        self.check_MessageDate.setText(_translate("SetEinstellungen", "+ aktuelles Datum"))
        self.label_6.setText(_translate("SetEinstellungen", "SMTP-Server :"))
        self.label_7.setText(_translate("SetEinstellungen", "Port :"))
        self.check_SSL.setText(_translate("SetEinstellungen", "SSL"))
        self.label_9.setText(_translate("SetEinstellungen", "Benutzername :"))
        self.label_10.setText(_translate("SetEinstellungen", "Passwort :"))
        self.Button_Save.setText(_translate("SetEinstellungen", "Speichern"))
        self.Button_Back.setText(_translate("SetEinstellungen", "Zurück"))

############################## Methods/Functions ########################

    def settings_refresh(self):
        global Einstellungen
        self.Edit_Headline.setText(Einstellungen.pHeadline)
        self.check_Headline_plusDate.setChecked(Einstellungen.pdate)
        self.check_Headline_plusFilename.setChecked(Einstellungen.pfilename)
        self.Edit_Tempfile.setText(Einstellungen.ptempfilename)
        self.check_DeleteTemp.setChecked(Einstellungen.pdelete)
        self.Edit_From.setText(Einstellungen.mfrom)
        self.Edit_Servername.setText(Einstellungen.mserver)
        self.Edit_ServerPort.setText(str(Einstellungen.mport))
        self.check_SSL.setChecked(Einstellungen.mSSL)
        self.Edit_Username.setText(Einstellungen.musername)
        self.Edit_Userpass.setText(crypt.decode(Einstellungen.mpassword))
        self.Edit_To.setText(Einstellungen.mto)
        self.Edit_Message.setText(Einstellungen.mmessage)
        self.check_MessageDate.setChecked(Einstellungen.mmessagedate)
        self.Edit_SendFileName.setText(Einstellungen.msendfilename)
        self.check_SendFileName_plusDate.setChecked(Einstellungen.mdate)

    def fertig(self):
        global Einstellungen
        Einstellungen.pHeadline = self.Edit_Headline.text()
        Einstellungen.pdate = self.check_Headline_plusDate.isChecked()
        Einstellungen.pfilename = self.check_Headline_plusFilename.isChecked()
        Einstellungen.ptempfilename = self.Edit_Tempfile.text()
        Einstellungen.pdelete = self.check_DeleteTemp.isChecked()
        Einstellungen.mfrom = self.Edit_From.text()
        Einstellungen.mto = self.Edit_To.text()
        Einstellungen.mserver = self.Edit_Servername.text()
        Einstellungen.mport = int(self.Edit_ServerPort.text())
        Einstellungen.mSSL = self.check_SSL.isChecked()
        Einstellungen.musername = self.Edit_Username.text()
        Einstellungen.mpassword = crypt.encode(self.Edit_Userpass.text())
        Einstellungen.mmessage = self.Edit_Message.text()
        Einstellungen.mmessagedate = self.check_MessageDate.isChecked()
        Einstellungen.msendfilename = self.Edit_SendFileName.text()
        Einstellungen.mdate = self.check_SendFileName_plusDate.isChecked()
        save_settings()


###################################################################################
#       PyQt5 - KatalogWebScraper                                                 #
###################################################################################

class Ui_PreislistenWebScraper(object):

    def setupUi(self, PreislistenWebScraper):
        PreislistenWebScraper.setObjectName("PreislistenWebScraper")
        PreislistenWebScraper.setWindowModality(QtCore.Qt.ApplicationModal)
        PreislistenWebScraper.resize(781, 489)
        PreislistenWebScraper.setMinimumSize(781, 489)
        PreislistenWebScraper.setMaximumSize(781, 489)
        PreislistenWebScraper.closeEvent = self.closeEvent

################################## Main #################################

        self.groupBox_Auswahl = QtWidgets.QGroupBox(PreislistenWebScraper)
        self.groupBox_Auswahl.setGeometry(QtCore.QRect(10, 10, 761, 261))
        self.groupBox_Auswahl.setObjectName("groupBox_Auswahl")

        self.check_aldinord = QtWidgets.QCheckBox(self.groupBox_Auswahl)
        self.check_aldinord.setGeometry(QtCore.QRect(17, 145, 111, 26))
        self.check_aldinord.setObjectName("check_aldinord")
        self.check_aldisued = QtWidgets.QCheckBox(self.groupBox_Auswahl)
        self.check_aldisued.setGeometry(QtCore.QRect(147, 145, 94, 26))
        self.check_aldisued.setObjectName("check_aldisued")
        self.check_penny = QtWidgets.QCheckBox(self.groupBox_Auswahl)
        self.check_penny.setGeometry(QtCore.QRect(282, 145, 94, 26))
        self.check_penny.setObjectName("check_penny")
        self.check_lidl = QtWidgets.QCheckBox(self.groupBox_Auswahl)
        self.check_lidl.setGeometry(QtCore.QRect(420, 145, 94, 26))
        self.check_lidl.setObjectName("check_lidl")
        self.check_edeka = QtWidgets.QCheckBox(self.groupBox_Auswahl)
        self.check_edeka.setGeometry(QtCore.QRect(535, 145, 94, 26))
        self.check_edeka.setObjectName("check_edeka")
        self.check_netto = QtWidgets.QCheckBox(self.groupBox_Auswahl)
        self.check_netto.setGeometry(QtCore.QRect(657, 145, 94, 26))
        self.check_netto.setObjectName("check_netto")

        self.label_Aldi_Nord = QtWidgets.QLabel(self.groupBox_Auswahl)
        self.label_Aldi_Nord.setGeometry(QtCore.QRect(12, 30, 106, 111))
        self.label_Aldi_Nord.setText("")
        self.label_Aldi_Nord.setAlignment(QtCore.Qt.AlignCenter)
        self.label_Aldi_Nord.setObjectName("label_Aldi_Nord")

        self.label_Aldi_Sued = QtWidgets.QLabel(self.groupBox_Auswahl)
        self.label_Aldi_Sued.setGeometry(QtCore.QRect(143, 30, 92, 111))
        self.label_Aldi_Sued.setText("")
        self.label_Aldi_Sued.setAlignment(QtCore.Qt.AlignCenter)
        self.label_Aldi_Sued.setObjectName("label_Aldi_Sued")

        self.label_LIDL = QtWidgets.QLabel(self.groupBox_Auswahl)
        self.label_LIDL.setGeometry(QtCore.QRect(395, 30, 111, 111))
        self.label_LIDL.setText("")
        self.label_LIDL.setAlignment(QtCore.Qt.AlignCenter)
        self.label_LIDL.setObjectName("label_LIDL")

        self.label_EDEKA = QtWidgets.QLabel(self.groupBox_Auswahl)
        self.label_EDEKA.setGeometry(QtCore.QRect(524, 30, 92, 111))
        self.label_EDEKA.setText("")
        self.label_EDEKA.setAlignment(QtCore.Qt.AlignCenter)
        self.label_EDEKA.setObjectName("label_EDEKA")

        self.label_Netto = QtWidgets.QLabel(self.groupBox_Auswahl)
        self.label_Netto.setGeometry(QtCore.QRect(635, 65, 111, 40))
        self.label_Netto.setText("")
        self.label_Netto.setAlignment(QtCore.Qt.AlignCenter)
        self.label_Netto.setObjectName("label_Netto")

        self.label_Penny = QtWidgets.QLabel(self.groupBox_Auswahl)
        self.label_Penny.setGeometry(QtCore.QRect(260, 30, 111, 111))
        self.label_Penny.setText("")
        self.label_Penny.setAlignment(QtCore.Qt.AlignCenter)
        self.label_Penny.setObjectName("label_Penny")

        self.Button_all = QtWidgets.QPushButton(self.groupBox_Auswahl)
        self.Button_all.setGeometry(QtCore.QRect(20, 178, 180, 32))
        self.Button_all.setObjectName("Button_all")

        self.Button_none = QtWidgets.QPushButton(self.groupBox_Auswahl)
        self.Button_none.setGeometry(QtCore.QRect(200, 178, 180, 32))
        self.Button_none.setObjectName("Button_none")

        self.Button_vor = QtWidgets.QPushButton(self.groupBox_Auswahl)
        self.Button_vor.setGeometry(QtCore.QRect(380, 178, 180, 32))
        self.Button_vor.setObjectName("Button_vor")

        self.Button_nichtvor = QtWidgets.QPushButton(self.groupBox_Auswahl)
        self.Button_nichtvor.setGeometry(QtCore.QRect(560, 178, 180, 32))
        self.Button_nichtvor.setObjectName("Button_nichtvor")

        self.Button_delete = QtWidgets.QPushButton(self.groupBox_Auswahl)
        self.Button_delete.setStyleSheet('QPushButton {color: red;font-weight: bold;}')
        if platform.system() == 'Linux':
            dir = str(Path.cwd())+'/resources/ico/'
        elif platform.system() == 'Windows':
            dir = str(Path.cwd())+'\\resources\ico\\'
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(dir+"warning.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.Button_delete.setGeometry(QtCore.QRect(20, 214, 720, 32))
        self.Button_delete.setIcon(icon1)
        self.Button_delete.setIconSize(QtCore.QSize(24, 24))
        self.Button_delete.setObjectName("Button_delete")

        self.show_Logos()

        self.groupBox_Vorgang = QtWidgets.QGroupBox(PreislistenWebScraper)
        self.groupBox_Vorgang.setGeometry(QtCore.QRect(10, 280, 761, 161))
        self.groupBox_Vorgang.setObjectName("groupBox_Vorgang")
        self.progressBar_einzel = QtWidgets.QProgressBar(self.groupBox_Vorgang)
        self.progressBar_einzel.setGeometry(QtCore.QRect(20, 50, 721, 24))
        self.progressBar_einzel.setProperty("value", 24)
        self.progressBar_einzel.setObjectName("progressBar_einzel")
        self.progressBar_einzel.setValue(0)
        self.progressBar_gesamt = QtWidgets.QProgressBar(self.groupBox_Vorgang)
        self.progressBar_gesamt.setGeometry(QtCore.QRect(20, 110, 721, 24))
        self.progressBar_gesamt.setProperty("value", 24)
        self.progressBar_gesamt.setObjectName("progressBar_gesamt")
        self.progressBar_gesamt.setValue(0)
        self.label_fortschritt = QtWidgets.QLabel(self.groupBox_Vorgang)
        self.label_fortschritt.setGeometry(QtCore.QRect(20, 20, 721, 22))
        self.label_fortschritt.setAlignment(QtCore.Qt.AlignCenter)
        self.label_fortschritt.setObjectName("label_fortschritt")
        self.label_10 = QtWidgets.QLabel(self.groupBox_Vorgang)
        self.label_10.setGeometry(QtCore.QRect(20, 80, 721, 22))
        self.label_10.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_10.setAlignment(QtCore.Qt.AlignCenter)
        self.label_10.setObjectName("label_10")

        self.Button_Start = QtWidgets.QPushButton(PreislistenWebScraper)
        self.Button_Start.setGeometry(QtCore.QRect(580, 450, 95, 32))
        self.Button_Start.setObjectName("Button_Start")
        self.Button_Back = QtWidgets.QPushButton(PreislistenWebScraper)
        self.Button_Back.setGeometry(QtCore.QRect(680, 450, 95, 32))
        self.Button_Back.setObjectName("Button_Back")
        self.retranslateUi(PreislistenWebScraper)

############################# Signals & Slots ###########################

        self.Button_Back.clicked.connect(PreislistenWebScraper.close)
        self.Button_Start.clicked.connect(self.starte_Crawler)
        self.Button_all.clicked.connect(self.set_all)
        self.Button_none.clicked.connect(self.set_none)
        self.Button_vor.clicked.connect(self.set_vorhanden)
        self.Button_nichtvor.clicked.connect(self.set_nicht_vorhanden)
        self.Button_delete.clicked.connect(self.delete_Katalogs)

        QtCore.QMetaObject.connectSlotsByName(PreislistenWebScraper)

################################ Translations ###########################

    def retranslateUi(self, PreislistenWebScraper):
        _translate = QtCore.QCoreApplication.translate
        PreislistenWebScraper.setWindowTitle(_translate("PreislistenWebScraper", "Preislisten aktualisieren"))
        self.groupBox_Auswahl.setTitle(_translate("PreislistenWebScraper", "Discounter auswählen"))
        self.check_aldisued.setText(_translate("PreislistenWebScraper", "ALDI Süd"))
        self.check_penny.setText(_translate("PreislistenWebScraper", "Penny"))
        self.check_lidl.setText(_translate("PreislistenWebScraper", "LIDL"))
        self.check_edeka.setText(_translate("PreislistenWebScraper", "EDEKA"))
        self.check_netto.setText(_translate("PreislistenWebScraper", "Netto"))
        self.check_aldinord.setText(_translate("PreislistenWebScraper", "ALDI Nord"))
        self.groupBox_Vorgang.setTitle(_translate("PreislistenWebScraper", "Vorgang"))
        self.label_fortschritt.setText(_translate("PreislistenWebScraper", "Fortschritt"))
        self.label_10.setText(_translate("PreislistenWebScraper", "Gesamtfortschritt"))
        self.Button_Start.setText(_translate("PreislistenWebScraper", "Start"))
        self.Button_Back.setText(_translate("PreislistenWebScraper", "Fertig"))
        self.Button_all.setText(_translate("PreislistenWebScraper", "Alle"))
        self.Button_none.setText(_translate("PreislistenWebScraper", "Keine"))
        self.Button_vor.setText(_translate("PreislistenWebScraper", "Vorhanden"))
        self.Button_nichtvor.setText(_translate("PreislistenWebScraper", "Nicht Vorhanden"))
        self.Button_delete.setText(_translate("PreislistenWebScraper", "  Ausgewählte Kataloge löschen"))

############################## Methods/Functions ########################

    def show_Logos(self):
        if platform.system() == 'Linux':
            self.label_Aldi_Nord.setPixmap(QtGui.QPixmap("resources/logos/Aldi_Nord.png")) if Path(str(Path.cwd()) +
                                                                                                   '/catalogs/ALDI_Nord.epk').exists() else self.label_Aldi_Nord.setPixmap(QtGui.QPixmap("resources/logos/Aldi_Nord_grey.png"))
            self.label_Aldi_Sued.setPixmap(QtGui.QPixmap("resources/logos/Aldi_Sued.png")) if Path(str(Path.cwd()) +
                                                                                                   '/catalogs/ALDI_Sued.epk').exists() else self.label_Aldi_Sued.setPixmap(QtGui.QPixmap("resources/logos/Aldi_Sued_grey.png"))
            self.label_LIDL.setPixmap(QtGui.QPixmap("resources/logos/LIDL.png")) if Path(str(Path.cwd()) +
                                                                                         '/catalogs/LIDL.epk').exists() else self.label_LIDL.setPixmap(QtGui.QPixmap("resources/logos/LIDL_grey.png"))
            self.label_Penny.setPixmap(QtGui.QPixmap("resources/logos/Penny.png")) if Path(str(Path.cwd()) +
                                                                                           '/catalogs/PENNY.epk').exists() else self.label_Penny.setPixmap(QtGui.QPixmap("resources/logos/Penny_grey.png"))
            self.label_Netto.setPixmap(QtGui.QPixmap("resources/logos/Netto.png")) if Path(str(Path.cwd()) +
                                                                                           '/catalogs/NETTO.epk').exists() else self.label_Netto.setPixmap(QtGui.QPixmap("resources/logos/Netto_grey.png"))
            self.label_EDEKA.setPixmap(QtGui.QPixmap("resources/logos/EDEKA.png")) if Path(str(Path.cwd()) +
                                                                                           '/catalogs/EDEKA.epk').exists() else self.label_EDEKA.setPixmap(QtGui.QPixmap("resources/logos/EDEKA_grey.png"))
        elif platform.system() == 'Windows':
            self.label_Aldi_Nord.setPixmap(QtGui.QPixmap(str(Path.cwd())+'\\resources\\logos\\'+"Aldi_Nord.png")) if Path(str(Path.home() / 'Documents\ezExpress\catalogs') +
                                                                                                                          '\\'+'ALDI_Nord.epk').exists() else self.label_Aldi_Nord.setPixmap(QtGui.QPixmap(str(Path.cwd())+'\\resources\\logos\\'+"Aldi_Nord_grey.png"))
            self.label_Aldi_Sued.setPixmap(QtGui.QPixmap(str(Path.cwd())+'\\resources\\logos\\'+"Aldi_Sued.png")) if Path(str(Path.home() / 'Documents\ezExpress\catalogs') +
                                                                                                                          '\\'+'ALDI_Sued.epk').exists() else self.label_Aldi_Sued.setPixmap(QtGui.QPixmap(str(Path.cwd())+'\\resources\\logos\\'+"Aldi_Sued_grey.png"))
            self.label_LIDL.setPixmap(QtGui.QPixmap(str(Path.cwd())+'\\resources\\logos\\'+"LIDL.png")) if Path(str(Path.home() / 'Documents\ezExpress\catalogs') +
                                                                                                                '\\'+'LIDL.epk').exists() else self.label_LIDL.setPixmap(QtGui.QPixmap(str(Path.cwd())+'\\resources\\logos\\'+"LIDL_grey.png"))
            self.label_Penny.setPixmap(QtGui.QPixmap(str(Path.cwd())+'\\resources\\logos\\'+"Penny.png")) if Path(str(Path.home() / 'Documents\ezExpress\catalogs') +
                                                                                                                  '\\'+'PENNY.epk').exists() else self.label_Penny.setPixmap(QtGui.QPixmap(str(Path.cwd())+'\\resources\\logos\\'+"Penny_grey.png"))
            self.label_Netto.setPixmap(QtGui.QPixmap(str(Path.cwd())+'\\resources\\logos\\'+"Netto.png")) if Path(str(Path.home() / 'Documents\ezExpress\catalogs') +
                                                                                                                  '\\'+'NETTO.epk').exists() else self.label_Netto.setPixmap(QtGui.QPixmap(str(Path.cwd())+'\\resources\\logos\\'+"Netto_grey.png"))
            self.label_EDEKA.setPixmap(QtGui.QPixmap(str(Path.cwd())+'\\resources\\logos\\'+"EDEKA.png")) if Path(str(Path.home() / 'Documents\ezExpress\catalogs') +
                                                                                                                  '\\'+'EDEKA.epk').exists() else self.label_EDEKA.setPixmap(QtGui.QPixmap(str(Path.cwd())+'\\resources\\logos\\'+"EDEKA_grey.png"))

    def delete_Katalogs(self):
        global currentCatalogName
        global lastCatalogName
        global Products
        global CategoryList
        reply = QtWidgets.QMessageBox.question(PreislistenWebScraper, 'Kataloge löschen?', 'Sind Sie sicher?', QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            if platform.system() == 'Linux':
                if Path(str(Path.cwd())+'/catalogs/ALDI_Nord.epk').exists() and self.check_aldinord.isChecked():
                    Path(str(Path.cwd())+'/catalogs/ALDI_Nord.epk').unlink()
                if Path(str(Path.cwd())+'/catalogs/ALDI_Sued.epk').exists() and self.check_aldisued.isChecked():
                    Path(str(Path.cwd())+'/catalogs/ALDI_Sued.epk').unlink()
                if Path(str(Path.cwd())+'/catalogs/LIDL.epk').exists() and self.check_lidl.isChecked():
                    Path(str(Path.cwd())+'/catalogs/LIDL.epk').unlink()
                if Path(str(Path.cwd())+'/catalogs/PENNY.epk').exists() and self.check_penny.isChecked():
                    Path(str(Path.cwd())+'/catalogs/PENNY.epk').unlink()
                if Path(str(Path.cwd())+'/catalogs/NETTO.epk').exists() and self.check_netto.isChecked():
                    Path(str(Path.cwd())+'/catalogs/NETTO.epk').unlink()
                if Path(str(Path.cwd())+'/catalogs/EDEKA.epk').exists() and self.check_edeka.isChecked():
                    Path(str(Path.cwd())+'/catalogs/EDEKA.epk').unlink()
            elif platform.system() == 'Windows':
                if Path(str(Path.home() / 'Documents\ezExpress\catalogs')+'\\'+'ALDI_Nord.epk').exists() and self.check_aldinord.isChecked():
                    Path(str(Path.home() / 'Documents\ezExpress\catalogs')+'\\'+'ALDI_Nord.epk').unlink()
                if Path(str(Path.home() / 'Documents\ezExpress\catalogs')+'\\'+'ALDI_Sued.epk').exists() and self.check_aldisued.isChecked():
                    Path(str(Path.home() / 'Documents\ezExpress\catalogs')+'\\'+'ALDI_Sued.epk').unlink()
                if Path(str(Path.home() / 'Documents\ezExpress\catalogs')+'\\'+'LIDL.epk').exists() and self.check_lidl.isChecked():
                    Path(str(Path.home() / 'Documents\ezExpress\catalogs')+'\\'+'LIDL.epk').unlink()
                if Path(str(Path.home() / 'Documents\ezExpress\catalogs')+'\\'+'PENNY.epk').exists() and self.check_penny.isChecked():
                    Path(str(Path.home() / 'Documents\ezExpress\catalogs')+'\\'+'PENNY.epk').unlink()
                if Path(str(Path.home() / 'Documents\ezExpress\catalogs')+'\\'+'NETTO.epk').exists() and self.check_netto.isChecked():
                    Path(str(Path.home() / 'Documents\ezExpress\catalogs')+'\\'+'NETTO.epk').unlink()
                if Path(str(Path.home() / 'Documents\ezExpress\catalogs')+'\\'+'EDEKA.epk').exists() and self.check_edeka.isChecked():
                    Path(str(Path.home() / 'Documents\ezExpress\catalogs')+'\\'+'EDEKA.epk').unlink()
            if not Path(currentCatalogName).exists():
                currentCatalogName = ''
                lastCatalogName = ''
                Products = []
                CategoryList = []
            self.set_none()
            self.show_Logos()

    def set_vorhanden(self):
        if platform.system() == 'Linux':
            self.check_aldinord.setChecked(True) if Path(str(Path.cwd())+'/catalogs/ALDI_Nord.epk').exists() else self.check_aldinord.setChecked(False)
            self.check_aldisued.setChecked(True) if Path(str(Path.cwd())+'/catalogs/ALDI_Sued.epk').exists() else self.check_aldisued.setChecked(False)
            self.check_lidl.setChecked(True) if Path(str(Path.cwd())+'/catalogs/LIDL.epk').exists() else self.check_lidl.setChecked(False)
            self.check_penny.setChecked(True) if Path(str(Path.cwd())+'/catalogs/PENNY.epk').exists() else self.check_penny.setChecked(False)
            self.check_netto.setChecked(True) if Path(str(Path.cwd())+'/catalogs/NETTO.epk').exists() else self.check_netto.setChecked(False)
            self.check_edeka.setChecked(True) if Path(str(Path.cwd())+'/catalogs/EDEKA.epk').exists() else self.check_edeka.setChecked(False)
        elif platform.system() == 'Windows':
            self.check_aldinord.setChecked(True) if Path(str(Path.home() / 'Documents\ezExpress\catalogs')+'\\'+'ALDI_Nord.epk').exists() else self.check_aldinord.setChecked(False)
            self.check_aldisued.setChecked(True) if Path(str(Path.home() / 'Documents\ezExpress\catalogs')+'\\'+'ALDI_Sued.epk').exists() else self.check_aldisued.setChecked(False)
            self.check_lidl.setChecked(True) if Path(str(Path.home() / 'Documents\ezExpress\catalogs')+'\\'+'LIDL.epk').exists() else self.check_lidl.setChecked(False)
            self.check_penny.setChecked(True) if Path(str(Path.home() / 'Documents\ezExpress\catalogs')+'\\'+'PENNY.epk').exists() else self.check_penny.setChecked(False)
            self.check_netto.setChecked(True) if Path(str(Path.home() / 'Documents\ezExpress\catalogs')+'\\'+'NETTO.epk').exists() else self.check_netto.setChecked(False)
            self.check_edeka.setChecked(True) if Path(str(Path.home() / 'Documents\ezExpress\catalogs')+'\\'+'EDEKA.epk').exists() else self.check_edeka.setChecked(False)

    def set_nicht_vorhanden(self):
        if platform.system() == 'Linux':
            self.check_aldinord.setChecked(False) if Path(str(Path.cwd())+'/catalogs/ALDI_Nord.epk').exists() else self.check_aldinord.setChecked(True)
            self.check_aldisued.setChecked(False) if Path(str(Path.cwd())+'/catalogs/ALDI_Sued.epk').exists() else self.check_aldisued.setChecked(True)
            self.check_lidl.setChecked(False) if Path(str(Path.cwd())+'/catalogs/LIDL.epk').exists() else self.check_lidl.setChecked(True)
            self.check_penny.setChecked(False) if Path(str(Path.cwd())+'/catalogs/PENNY.epk').exists() else self.check_penny.setChecked(True)
            self.check_netto.setChecked(False) if Path(str(Path.cwd())+'/catalogs/NETTO.epk').exists() else self.check_netto.setChecked(True)
            self.check_edeka.setChecked(False) if Path(str(Path.cwd())+'/catalogs/EDEKA.epk').exists() else self.check_edeka.setChecked(True)
        elif platform.system() == 'Windows':
            self.check_aldinord.setChecked(False) if Path(str(Path.home() / 'Documents\ezExpress\catalogs')+'\\'+'ALDI_Nord.epk').exists() else self.check_aldinord.setChecked(True)
            self.check_aldisued.setChecked(False) if Path(str(Path.home() / 'Documents\ezExpress\catalogs')+'\\'+'ALDI_Sued.epk').exists() else self.check_aldisued.setChecked(True)
            self.check_lidl.setChecked(False) if Path(str(Path.home() / 'Documents\ezExpress\catalogs')+'\\'+'LIDL.epk').exists() else self.check_lidl.setChecked(True)
            self.check_penny.setChecked(False) if Path(str(Path.home() / 'Documents\ezExpress\catalogs')+'\\'+'PENNY.epk').exists() else self.check_penny.setChecked(True)
            self.check_netto.setChecked(False) if Path(str(Path.home() / 'Documents\ezExpress\catalogs')+'\\'+'NETTO.epk').exists() else self.check_netto.setChecked(True)
            self.check_edeka.setChecked(False) if Path(str(Path.home() / 'Documents\ezExpress\catalogs')+'\\'+'EDEKA.epk').exists() else self.check_edeka.setChecked(True)

    def set_all(self):
        self.check_aldinord.setChecked(True)
        self.check_aldisued.setChecked(True)
        self.check_lidl.setChecked(True)
        self.check_penny.setChecked(True)
        self.check_netto.setChecked(True)
        self.check_edeka.setChecked(True)

    def set_none(self):
        self.check_aldinord.setChecked(False)
        self.check_aldisued.setChecked(False)
        self.check_lidl.setChecked(False)
        self.check_penny.setChecked(False)
        self.check_netto.setChecked(False)
        self.check_edeka.setChecked(False)

    def starte_Crawler(self):
        Discounter_List = []
        if self.check_aldinord.isChecked():
            Discounter_List.append(['https://www.discounter-preisvergleich.de/ALDI-Nord-Preise/', 'ALDI_Nord.epk', 18, 'ALDI Nord', 2616])
        if self.check_aldisued.isChecked():
            Discounter_List.append(['https://www.discounter-preisvergleich.de/ALDI-Sued-Preise/', 'ALDI_Sued.epk', 18, 'ALDI Süd', 3549])
        if self.check_lidl.isChecked():
            Discounter_List.append(['https://www.discounter-preisvergleich.de/LIDL-Preise/', 'LIDL.epk', 13, 'LIDL', 2327])
        if self.check_penny.isChecked():
            Discounter_List.append(['https://www.discounter-preisvergleich.de/PENNY-Preise/', 'PENNY.epk', 14, 'Penny', 2445])
        if self.check_edeka.isChecked():
            Discounter_List.append(['https://www.discounter-preisvergleich.de/EDEKA-Preise/', 'EDEKA.epk', 14, 'EDEKA', 3441])
        if self.check_netto.isChecked():
            Discounter_List.append(['https://www.discounter-preisvergleich.de/NETTO-Preise/', 'NETTO.epk', 14, 'Netto', 2023])
        self.create_Preislisten(Discounter_List)

    def save_catalog(self, data, filename):
        if platform.system() == 'Linux':
            fname = str(Path(__file__).resolve().parent) + '/catalogs/' + filename
        elif platform.system() == 'Windows':
            fname = str(Path.home() / 'Documents\ezExpress\catalogs')+'\\' + filename
        afile = open(fname, 'wb')
        dump(data, afile)
        afile.close()

    def refresh(self):
        self.label_fortschritt.setText('Fortschritt')
        self.progressBar_gesamt.setValue(0)
        self.progressBar_einzel.setValue(0)

    def create_Preislisten(self, discounterliste):
        # PreislistenWebScraper.setEnabled(False)
        self.groupBox_Auswahl.setEnabled(False)
        self.Button_Start.setEnabled(False)
        self.Button_Back.setEnabled(False)

        maxgesamt = 0
        isgesamt = 0
        try:
            for eintrag in discounterliste:
                maxgesamt += eintrag[4]

            for nummer in range(len(discounterliste)):
                maxzaehler = discounterliste[nummer][4]
                zaehler = 0
                self.label_fortschritt.setText('Fortschritt : '+discounterliste[nummer][3])
                main_url = discounterliste[nummer][0]
                req = requests.get(main_url)
                soup = BeautifulSoup(req.text, "lxml")
                all = soup.find('ul', class_='list-inline')
                cats = all.find_all('a')
                new_url = main_url[0:(len(main_url)-2)]
                list_of_urls = []
                list_of_names = []
                root = []
                root = TreeNode(0, 'Produkte')
                for cat in cats:
                    name = cat.text.replace('\xad', '')
                    name = name.replace('\xa0', '')
                    eintrag = cat['href'][discounterliste[nummer][2]:]
                    next_url = new_url+eintrag
                    list_of_urls.append(next_url)
                    list_of_names.append(name)
                    zaehler += 1
                    isgesamt += 1
                    self.progressBar_gesamt.setValue((isgesamt*100)//maxgesamt)
                    self.progressBar_einzel.setValue((zaehler*100)//maxzaehler)
                for x in range(len(list_of_urls)):
                    new_site = requests.get(list_of_urls[x])
                    new_soup = BeautifulSoup(new_site.text, "lxml")
                    formaction = new_soup.find('form', action=list_of_urls[x])
                    unter = formaction.find_all('h2')
                    tabellen = formaction.find_all('table', class_='table table-striped table-hover')
                    Node = TreeNode(x+1, list_of_names[x])
                    for i in range(len(unter)):
                        bezeichnung = unter[i].text.replace('\xad', '')
                        bezeichnung = bezeichnung.replace('\xa0', '')
                        New_Node = TreeNode(((x+1)*100+i+1), bezeichnung)
                        zeilen = tabellen[i].find_all('tr')
                        new_list = []
                        for j in range(len(zeilen)):
                            zeile = zeilen[j]
                            spalten = zeile.find_all('td')
                            if len(spalten) > 0:
                                #pname = spalten[2].text + ' ' + spalten[1].find('a').text
                                if spalten[2].text == "\xA0":
                                    pname = spalten[1].find('a').text
                                else:
                                    pname = spalten[1].find('a').text + ', ' + spalten[2].text
                                pname = pname.replace('\xa0', '')
                                if pname[0] == ' ':
                                    pname = pname[1:]
                                ppreis = spalten[3].text.replace('\n', '')
                                pvpe = spalten[4].text.replace('\n', '')
                                new_list.append([pname[:45], pvpe[:8], float(ppreis)])
                                zaehler += 1
                                isgesamt += 1
                                self.progressBar_gesamt.setValue((isgesamt*100)//maxgesamt)
                                self.progressBar_einzel.setValue((zaehler*100)//maxzaehler)
                        New_Node.liste = new_list
                        Node.add_child(New_Node)
                        zaehler += 1
                        isgesamt += 1
                        self.progressBar_gesamt.setValue((isgesamt*100)//maxgesamt)
                        self.progressBar_einzel.setValue((zaehler*100)//maxzaehler)
                    Node.aufgeklappt = False
                    root.add_child(Node)
                    zaehler += 1
                    isgesamt += 1
                    self.progressBar_gesamt.setValue((isgesamt*100)//maxgesamt)
                    self.progressBar_einzel.setValue((zaehler*100)//maxzaehler)
                self.save_catalog(root, discounterliste[nummer][1])
                self.progressBar_einzel.setValue(100)
                self.show_Logos()
            self.progressBar_gesamt.setValue(100)
        except:
            error = sys.exc_info()  # [1]
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setWindowTitle("Fehler")
            msg.setText(str(error))

            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            dummie = msg.exec_()
        self.set_none()
        self.groupBox_Auswahl.setEnabled(True)
        self.Button_Start.setEnabled(True)
        self.Button_Back.setEnabled(True)
        # PreislistenWebScraper.setEnabled(True)

    def closeEvent(self, event):
        self.set_none()
        ui.catview_refresh()
        ui.Combobox_Change()


###################################################################################
#       PyQt5 - SearchEngine                                                      #
###################################################################################

class Ui_SearchEngine(object):

    def __init__(self):
        self.SuchergebnisListe = []

    def setupUi(self, SearchEngine):
        SearchEngine.setObjectName("SearchEngine")
        SearchEngine.setWindowModality(QtCore.Qt.ApplicationModal)
        SearchEngine.resize(1100, 856)
        #SearchEngine.setMinimumSize(881, 776)
        #SearchEngine.setMaximumSize(881, 776)
        SearchEngine.closeEvent = self.closeEvent
################################## Main ##################################

        self.label = QtWidgets.QLabel(SearchEngine)
        self.label.setGeometry(QtCore.QRect(10, 50, 101, 31))
        self.label.setObjectName("label")

        self.label1 = QtWidgets.QLabel(SearchEngine)
        self.label1.setEnabled(False)
        self.label1.setGeometry(QtCore.QRect(500, 90, 230, 31))
        self.label1.setStyleSheet("color: yellowgreen")
        self.label1.setObjectName("label1")

        self.label2 = QtWidgets.QLabel(SearchEngine)
        self.label2.setEnabled(False)
        self.label2.setGeometry(QtCore.QRect(765, 90, 61, 31))
        self.label2.setStyleSheet("color: yellowgreen")
        self.label2.setObjectName("label2")

        self.label3 = QtWidgets.QLabel(SearchEngine)
        self.label3.setEnabled(False)
        self.label3.setGeometry(QtCore.QRect(1040, 90, 41, 31))
        self.label3.setStyleSheet("color: yellowgreen")
        self.label3.setObjectName("label3")

        self.sucheingabe = QtWidgets.QLineEdit(SearchEngine)
        self.sucheingabe.setGeometry(QtCore.QRect(110, 50, 341, 32))
        self.sucheingabe.setText("")
        self.sucheingabe.setMaxLength(35)
        self.sucheingabe.setObjectName("sucheingabe")

        self.search_similar = QtWidgets.QCheckBox(SearchEngine)
        self.search_similar.setGeometry(QtCore.QRect(733, 50, 251, 31))
        self.search_similar.setObjectName("search_similar")
        self.search_similar.setFocusPolicy(QtCore.Qt.NoFocus)

        self.search_all = QtWidgets.QCheckBox(SearchEngine)
        self.search_all.setGeometry(QtCore.QRect(113, 90, 251, 31))
        self.search_all.setObjectName("search_all")
        self.search_all.setFocusPolicy(QtCore.Qt.NoFocus)

        self.Katalogname = QtWidgets.QLineEdit(SearchEngine)
        self.Katalogname.setEnabled(False)
        self.Katalogname.setGeometry(QtCore.QRect(10, 10, 1080, 32))
        self.Katalogname.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.Katalogname.setStyleSheet("background: darkblue; color: yellow; font-weight: Bold")
        self.Katalogname.setFrame(True)
        self.Katalogname.setAlignment(QtCore.Qt.AlignCenter)
        self.Katalogname.setObjectName("Katalogname")

        self.similarity = QtWidgets.QSlider(SearchEngine)
        self.similarity.setEnabled(False)
        self.similarity.setGeometry(QtCore.QRect(827, 100, 200, 21))
        self.similarity.setOrientation(QtCore.Qt.Horizontal)
        self.similarity.setFocusPolicy(QtCore.Qt.NoFocus)
        self.similarity.setRange(60, 100)
        self.similarity.setValue(80)
        self.similarity.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.similarity.setTickInterval(10)
        self.similarity.setSingleStep(10)
        self.similarity.setPageStep(10)
        self.similarity.setObjectName("similarity")

############################### Suchergebnis #############################

        self.Suchergebnis = QtWidgets.QTableWidget(SearchEngine)
        self.Suchergebnis.setGeometry(QtCore.QRect(10, 130, 1080, 671))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.Suchergebnis.setFont(font)
        self.Suchergebnis.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.Suchergebnis.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.Suchergebnis.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.Suchergebnis.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.Suchergebnis.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        # self.Suchergebnis.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        self.Suchergebnis.setGridStyle(QtCore.Qt.DotLine)
        self.Suchergebnis.setRowCount(100)
        self.Suchergebnis.setColumnCount(5)
        self.Suchergebnis.setObjectName("Suchergebnis")
        self.Suchergebnis.setColumnWidth(0, 150)
        self.Suchergebnis.setColumnWidth(1, 351)
        self.Suchergebnis.setColumnWidth(2, 380)
        self.Suchergebnis.setColumnWidth(3, 88)
        self.Suchergebnis.setColumnWidth(4, 84)
        rdelegate = AlignRightDelegate(self.Suchergebnis)
        ldelegate = AlignLeftDelegate(self.Suchergebnis)
        cdelegate = AlignCenterDelegate(self.Suchergebnis)
        self.Suchergebnis.setItemDelegateForColumn(0, ldelegate)
        self.Suchergebnis.setItemDelegateForColumn(1, ldelegate)
        self.Suchergebnis.setItemDelegateForColumn(2, ldelegate)
        self.Suchergebnis.setItemDelegateForColumn(3, cdelegate)
        self.Suchergebnis.setItemDelegateForColumn(4, rdelegate)
        self.Suchergebnis.verticalHeader().setDefaultSectionSize(11)

        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        item.setFont(font)
        self.Suchergebnis.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        item.setFont(font)
        self.Suchergebnis.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        item.setFont(font)
        self.Suchergebnis.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        item.setFont(font)
        self.Suchergebnis.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        item.setFont(font)
        self.Suchergebnis.setHorizontalHeaderItem(4, item)
        self.Suchergebnis.horizontalHeader().setStretchLastSection(True)
        self.Suchergebnis.verticalHeader().setVisible(False)

################################### Rest #################################

        if platform.system() == 'Linux':
            dir = str(Path.cwd())+'/resources/ico/'
        elif platform.system() == 'Windows':
            dir = str(Path.cwd())+'\\resources\ico\\'
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(dir+"append.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(dir+"back.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(dir+"search.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(dir+"delete.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.Button_add = QtWidgets.QPushButton(SearchEngine)
        self.Button_add.setGeometry(QtCore.QRect(751, 810, 341, 41))
        self.Button_add.setObjectName("Button_add")
        self.Button_add.setFocusPolicy(QtCore.Qt.NoFocus)
        self.Button_add.setIcon(icon)
        self.Button_add.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.Button_add.setIconSize(QtCore.QSize(30, 30))

        self.Button_back = QtWidgets.QPushButton(SearchEngine)
        self.Button_back.setGeometry(QtCore.QRect(10, 810, 151, 41))
        self.Button_back.setIcon(icon1)
        self.Button_back.setIconSize(QtCore.QSize(24, 24))
        self.Button_back.setObjectName("Button_back")

        self.Button_startSearch = QtWidgets.QPushButton(SearchEngine)
        self.Button_startSearch.setGeometry(QtCore.QRect(497, 48, 211, 36))
        self.Button_startSearch.setFocusPolicy(QtCore.Qt.NoFocus)
        self.Button_startSearch.setIcon(icon2)
        self.Button_startSearch.setIconSize(QtCore.QSize(26, 26))
        self.Button_startSearch.setObjectName("Button_startSearch")

        self.Button_resetSearch = QtWidgets.QPushButton(SearchEngine)
        self.Button_resetSearch.setGeometry(QtCore.QRect(457, 48, 36, 36))
        self.Button_resetSearch.setIcon(icon3)
        self.Button_resetSearch.setFocusPolicy(QtCore.Qt.NoFocus)
        self.Button_resetSearch.setIconSize(QtCore.QSize(20, 20))
        self.Button_resetSearch.setObjectName("Button_resetSearch")

        self.label1.setVisible(False)
        self.label2.setVisible(False)
        self.label3.setVisible(False)
        self.similarity.setVisible(False)

#############################  Signals & Slots  ##########################

        self.Button_back.clicked.connect(SearchEngine.close)
        self.search_similar.stateChanged.connect(self.set_visible)
        self.search_all.stateChanged.connect(self.set_all)
        self.sucheingabe.returnPressed.connect(self.Button_startSearch.click)
        self.Button_startSearch.clicked.connect(self.starte_Suche)
        self.Button_add.clicked.connect(self.add2ShoppingList)
        self.Button_resetSearch.clicked.connect(self.set_resetSearch)
        self.Suchergebnis.doubleClicked.connect(self.add2ShoppingList)
        self.retranslateUi(SearchEngine)
        QtCore.QMetaObject.connectSlotsByName(SearchEngine)

################################ Translation #############################

    def retranslateUi(self, SearchEngine):
        _translate = QtCore.QCoreApplication.translate
        SearchEngine.setWindowTitle(_translate("SearchEngine", "Artikel im aktuellen Katalog suchen..."))
        self.label.setText(_translate("SearchEngine", "Suchbegriff :"))
        self.sucheingabe.setToolTip(_translate("SearchEngine", "Einen Suchbegriff eingeben"))
        self.search_all.setText(_translate("SearchEngine", "in allen Katalogen suchen"))
        self.search_all.setToolTip(_translate("SearchEngine", "Der Suchbegriff wird in allen gefundenen Produktkatalogen gesucht"))
        self.search_similar.setText(_translate("SearchEngine", "auch ähnliche Begriffe suchen"))
        self.search_similar.setToolTip(_translate("SearchEngine", "Andere Schreibweisen bzw. Schreibfehler werden mit einbezogen"))
        self.Katalogname.setText(_translate("SearchEngine", "Katalogname"))
        self.Katalogname.setToolTip(_translate("SearchEngine", "Aktuell ausgewählter Produktkatalog in dem gesucht wird"))
        self.Suchergebnis.setToolTip(_translate("SearchEngine", "Hier werden eventuelle Suchergebnisse angezeigt"))
        self.label1.setText(_translate("SearchEngine", "Suchempfindlichkeit/-unschärfe :"))
        self.label1.setToolTip(_translate("SearchEngine", "je höher die Suchempfindlichkeit, desto genauer wird die Suche durchgeführt"))
        self.label2.setText(_translate("SearchEngine", "niedrig"))
        self.label2.setToolTip(_translate("SearchEngine", "je höher die Suchempfindlichkeit, desto genauer wird die Suche durchgeführt"))
        self.label3.setText(_translate("SearchEngine", "hoch"))
        self.label3.setToolTip(_translate("SearchEngine", "je höher die Suchempfindlichkeit, desto genauer wird die Suche durchgeführt"))
        item = self.Suchergebnis.horizontalHeaderItem(0)
        item.setText(_translate("SearchEngine", "Produktkatalog"))
        item = self.Suchergebnis.horizontalHeaderItem(1)
        item.setText(_translate("SearchEngine", "Kategorie"))
        item = self.Suchergebnis.horizontalHeaderItem(2)
        item.setText(_translate("SearchEngine", "Artikelbezeichnung"))
        item = self.Suchergebnis.horizontalHeaderItem(3)
        item.setText(_translate("SearchEngine", "Verpackung"))
        item = self.Suchergebnis.horizontalHeaderItem(4)
        item.setText(_translate("SearchEngine", "Preis"))
        self.Button_add.setText(_translate("SearchEngine", "Zum Einkaufszettel hinzufügen  "))
        self.Button_add.setToolTip(_translate("SearchEngine", "Fügt einen ausgewählten Suchlisteneintrag in den Einkaufszettel ein"))
        self.Button_back.setText(_translate("SearchEngine", " Fertig"))
        self.Button_startSearch.setText(_translate("SearchEngine", " Suche starten"))
        self.Button_startSearch.setToolTip(_translate("SearchEngine", "Sucht nach dem eingegebenen Begriff in allen Artikeln des Katalogs"))
        self.Button_resetSearch.setText(_translate("SearchEngine", ""))
        self.Button_resetSearch.setToolTip(_translate("SearchEngine", "Löscht Suchbegriff und Suchergebnisse"))

################################## Methods ###############################

    def set_all(self):
        global KatalogFileList
        self.show_Katalogs()

    def set_visible(self):
        self.label1.setEnabled(True) if self.search_similar.isChecked() else self.label1.setEnabled(False)
        self.label2.setEnabled(True) if self.search_similar.isChecked() else self.label2.setEnabled(False)
        self.label3.setEnabled(True) if self.search_similar.isChecked() else self.label3.setEnabled(False)
        self.similarity.setEnabled(True) if self.search_similar.isChecked() else self.similarity.setEnabled(False)
        self.label1.setVisible(True) if self.search_similar.isChecked() else self.label1.setVisible(False)
        self.label2.setVisible(True) if self.search_similar.isChecked() else self.label2.setVisible(False)
        self.label3.setVisible(True) if self.search_similar.isChecked() else self.label3.setVisible(False)
        self.similarity.setVisible(True) if self.search_similar.isChecked() else self.similarity.setVisible(False)

    def show_Katalogs(self):

        if self.search_all.isChecked():
            alle_namen = ''
            for eintrag in KatalogFileList:
                alle_namen += '    +    ' + Path(eintrag).stem
            alle_namen = alle_namen[5:]
            self.Katalogname.setText(alle_namen)
        else:
            self.Katalogname.setText(str(Path(currentCatalogName).stem))

    def show_Suchergebnisse(self):
        global currentCatalogName
        self.show_Katalogs()
        self.Suchergebnis.setRowCount(0)
        for eintrag in self.SuchergebnisListe:
            position = self.Suchergebnis.rowCount()
            self.Suchergebnis.insertRow(position)
            self.Suchergebnis.setItem(position, 0, QtWidgets.QTableWidgetItem(Path(eintrag[6]).stem))
            self.Suchergebnis.setItem(position, 1, QtWidgets.QTableWidgetItem(eintrag[0])) if eintrag[4] == '' else self.Suchergebnis.setItem(
                position, 1, QtWidgets.QTableWidgetItem(eintrag[0]+'  /  '+eintrag[4]))
            self.Suchergebnis.setItem(position, 2, QtWidgets.QTableWidgetItem(eintrag[1]))
            self.Suchergebnis.setItem(position, 3, QtWidgets.QTableWidgetItem(eintrag[2]))
            self.Suchergebnis.setItem(position, 4, QtWidgets.QTableWidgetItem(convert_f2s(eintrag[3])))

    def set_resetSearch(self):
        self.SuchergebnisListe = []
        self.sucheingabe.setText('')
        self.show_Suchergebnisse()

    def starte_Suche(self):
        global Products
        global currentCatalogName
        global KatalogFileList

        def search_eintrag(suchwort, eintrag, similarity=False):
            entry = eintrag.replace(',', ' ')
            wortliste = entry.split()
            ergebnis = False
            for wort in wortliste:
                if suchwort.upper() in wort.upper():
                    ergebnis = True
                elif similarity:
                    if SequenceMatcher(None, suchwort.upper(), wort.upper()).ratio() >= (self.similarity.value()/100):
                        ergebnis = True
                if ergebnis:
                    break
            return ergebnis

        def search_liste(liste):
            ergebnisse = []
            for eintrag in liste:
                if search_eintrag(self.sucheingabe.text(), eintrag[0], similarity=self.search_similar.isChecked()):
                    ergebnisse.append(eintrag)
            return ergebnisse

        def search_katalog(Node, Katalogname):
            if Node != []:
                for child in Node.children:
                    if child.is_leaf():
                        ergebnisse = search_liste(child.liste)
                        if len(ergebnisse) > 0:
                            # Unterkategorien füllen
                            Unterkategorien = ''
                            level = child.get_level()
                            kind = child
                            if level > 1:
                                for _ in range(level-1):
                                    Unterkategorien = kind.data + '  /  ' + Unterkategorien if Unterkategorien != '' else kind.data
                                    kind = kind.parent
                            # aktuelle Hauptkategorie
                            aktkat = kind.data
                            aktindex = child.index
                            for ergebnis in ergebnisse:
                                self.SuchergebnisListe.append([aktkat, ergebnis[0], ergebnis[1], ergebnis[2], Unterkategorien, aktindex, Katalogname])
                    else:
                        search_katalog(child, Katalogname)

        self.SuchergebnisListe = []

        if self.search_all.isChecked() and KatalogFileList != []:
            for Katalogbezeichnung in KatalogFileList:
                if Path(Katalogbezeichnung).exists():
                    Produkte = load_file(Katalogbezeichnung)
                    search_katalog(Produkte, Katalogbezeichnung)
        else:
            if Path(currentCatalogName).exists():
                search_katalog(Products, currentCatalogName)

        self.show_Suchergebnisse()

    def add2ShoppingList(self):
        global ShoppingList
        global changeOccurred
        global isCategoryView
        global currentCatalogName
        global KatalogFileList
        if self.Suchergebnis.currentRow() in range(self.Suchergebnis.rowCount()):
            row = self.Suchergebnis.currentRow()
            changeOccurred = True
            kat = self.SuchergebnisListe[row][0]
            art = self.SuchergebnisListe[row][1]
            vpe = self.SuchergebnisListe[row][2]
            epreis = self.SuchergebnisListe[row][3]
            listIndex = self.SuchergebnisListe[row][5]
            Katalogbezeichnung = self.SuchergebnisListe[row][6]
            istdrin = False
            for zeile in range(len(ShoppingList)):
                if (ShoppingList[zeile][1] == art) and (ShoppingList[zeile][2] == vpe):
                    istdrin = True
                    wohin = zeile
                    ShoppingList[wohin][0] += 1
                    ShoppingList[wohin][4] = ShoppingList[wohin][0]*ShoppingList[wohin][3]
                    break
            if not istdrin:
                if isCategoryView:
                    ui.Einkaufszettel_Convert2Listansicht()
                    ShoppingList.append([1, art, vpe, epreis, epreis, kat, listIndex, Katalogbezeichnung])
                    ui.Einkaufszettel_Convert2Catansicht()
                else:
                    ShoppingList.append([1, art, vpe, epreis, epreis, kat, listIndex, Katalogbezeichnung])
                    ui.Einkaufszettel_Convert2Listansicht()

            ui.Einkaufszettel_show()

    def closeEvent(self, event):
        self.set_resetSearch()


###################################################################################
#       PyQt5 - About                                                             #
###################################################################################

class Ui_About_Dialog(object):
    def setupUi(self, About_Dialog):
        About_Dialog.setObjectName("About_Dialog")
        About_Dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        About_Dialog.resize(570, 698)
        About_Dialog.setModal(True)
        self.buttonBox = QtWidgets.QDialogButtonBox(About_Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(50, 660, 471, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.label = QtWidgets.QLabel(About_Dialog)
        self.label.setGeometry(QtCore.QRect(100, 10, 371, 91))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(48)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setStyleSheet("color: darkviolet")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(About_Dialog)
        self.label_2.setText("")

        if platform.system() == 'Linux':
            datei = str(Path.cwd())+'/resources/logos/ezExpress_small.png'
        elif platform.system() == 'Windows':
            datei = str(Path.cwd())+'\\resources\logos\\ezExpress_small.png'
        self.label_2.setPixmap(QtGui.QPixmap(datei))
        self.label_2.setGeometry(QtCore.QRect(185, 85, 200, 200))
        self.label_2.setObjectName("label_2")

        self.textBrowser_2 = QtWidgets.QTextBrowser(About_Dialog)
        self.textBrowser_2.setGeometry(QtCore.QRect(10, 310, 551, 341))
        self.textBrowser_2.setSource(QtCore.QUrl('README.md'))
        self.textBrowser_2.setOpenExternalLinks(True)
        self.textBrowser_2.setObjectName("textBrowser_2")
        About_Dialog.setWindowTitle(QtCore.QCoreApplication.translate("About_Dialog", "Über ezExpress"))
        self.label.setText(QtCore.QCoreApplication.translate("About_Dialog", "ezExpress"))
        self.buttonBox.accepted.connect(About_Dialog.close)
        QtCore.QMetaObject.connectSlotsByName(About_Dialog)


###################################################################################
#       PyQt5 - Global Methods/Functions                                          #
###################################################################################

######################### Call Windows & Widgets ########################


def show_ChangeCat():
    global Katalog
    global Products
    global currentCatalogName
    Katalog = deepcopy(Products)
    ui2.catview_refresh()
    ui2.artview_refresh()
    ChangeCat.show()


def Einkaufszettel_show():
    global isCategoryView
    # ChangeCat.close()
    if isCategoryView:
        ui.action_setListView.setChecked(False)
        ui.action_setCatView.setChecked(True)
    else:
        ui.action_setListView.setChecked(True)
        ui.action_setCatView.setChecked(False)

    ui.catview_show()
    ui.catview_refresh()
    ui.artview_showliste()


def show_Settings():
    ui3.settings_refresh()
    SetEinstellungen.show()


def show_PreislistenWebScraper():
    ui4.refresh()
    PreislistenWebScraper.show()


def show_SearchEngine():
    ui5.show_Suchergebnisse()
    SearchEngine.show()


########################### File Operations #############################


def save_file(datei, data):
    afile = open(datei, 'wb')
    dump(data, afile)
    afile.close()


def load_file(datei):
    try:
        afile = open(datei, 'rb')
        data = load(afile)
        afile.close()
        return data
    except:
        return None


def load_settings():
    global currentCatalogName
    global currentShoppingListName
    global isCategoryView
    global Einstellungen

    if platform.system() == 'Linux':
        filename = str(Path(__file__).resolve().parent) + '/resources/settings.cfg'
    elif platform.system() == 'Windows':
        filename = str(Path.home() / 'Documents\ezExpress\save\settings.cfg')

    test = Path(filename)
    if test.exists():
        Einstellungen = load_file(filename)
        currentCatalogName = Einstellungen.catfilename
        currentShoppingListName = Einstellungen.zetfilename
        isCategoryView = Einstellungen.iscatview
        return True
    else:
        return False


def save_settings():
    global currentCatalogName
    global currentShoppingListName
    global isCategoryView
    global Einstellungen

    Einstellungen.catfilename = currentCatalogName
    Einstellungen.zetfilename = currentShoppingListName
    Einstellungen.iscatview = isCategoryView

    if platform.system() == 'Linux':
        filename = str(Path(__file__).resolve().parent) + '/resources/settings.cfg'
    elif platform.system() == 'Windows':
        filename = str(Path.home() / 'Documents\ezExpress\save\settings.cfg')

    settings = Einstellungen
    save_file(filename, settings)

########################## Currency Operations ##########################


def convert_f2s(wert: float):
    if type(wert) is float:
        preis = str(wert)
        test = preis.split('.')
        if len(test[1]) == 1:
            test[1] += '0'
        elif len(test[1]) > 2:
            test[1] = test[1][:2]
        preis = test[0] + ',' + test[1] + ' €'
    else:
        preis = ''
    return preis


def convert_s2f(preis: str):
    if type(preis) is str:
        wert = 0.0
        test = preis.replace(' €', '')
        test2 = test.replace(',', '.')
        test3 = test2.replace('.', '')
        if test3.isdecimal():
            wert = float(test2)
        else:
            wert = 0.0
    else:
        wert = 0.0
    return wert

########################### File Operations #############################


def Convert_Einkaufszettel_2_PrintableList(Liste):
    global isCategoryView
    neue_Liste = []
    for eintrag in Liste:
        if eintrag[7] == 'Laden':
            neue_Liste.append([eintrag[7], eintrag[0], eintrag[1], eintrag[2], eintrag[3], eintrag[4]])
        elif eintrag[7] == 'Kategorie':
            neue_Liste.append([eintrag[7], eintrag[0], eintrag[1], eintrag[2], eintrag[3], eintrag[4]])
        else:
            neue_Liste.append(['', eintrag[0], eintrag[1], eintrag[2], eintrag[3], eintrag[4]])
    return neue_Liste


def calculateTotal():
    global ShoppingList
    gesamt = 0.0
    for eintrag in ShoppingList:
        if type(eintrag[0]) is int:
            gesamt += eintrag[4]
    preis = convert_f2s(gesamt)
    return preis


def darkmode():
    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Base, QtGui.QColor(25, 25, 25))
    palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.black)
    palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
    palette.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))
    palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))
    palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
    app.setPalette(palette)


###################################################################################
#       Initialisierung des Hauptprogramms                                        #
###################################################################################
if __name__ == '__main__':
    Einstellungen = ShoppingListSettings()

    chdir(Path(__file__).parent)
    if platform.system() == 'Windows':
        if not Path(str(Path.home() / 'Documents\ezExpress\catalogs')).exists():
            Path(str(Path.home() / 'Documents\ezExpress\catalogs')).mkdir(parents=True, exist_ok=True)
        if not Path(str(Path.home() / 'Documents\ezExpress\save')).exists():
            Path(str(Path.home() / 'Documents\ezExpress\save')).mkdir(parents=True, exist_ok=True)

    if platform.system() == 'Linux':
        Einstellungen.ptempfilename = str(Path.cwd())+'/resources/temp.prt'
    elif platform.system() == 'Windows':
        Einstellungen.ptempfilename = str(Path.home() / 'Documents\ezExpress\save\\temp.prt')

    if load_settings():
        if currentShoppingListName != '':
            iszettelname = Path(currentShoppingListName)
            if iszettelname.exists():
                savedata = load_file(currentShoppingListName)
                ShoppingList = savedata[0]
                Products = savedata[1]
                isCategoryView = savedata[2]
            else:
                isCategoryView = False
                ShoppingList = []
                currentShoppingListName = ''

        if currentCatalogName != '':
            iscatname = Path(currentCatalogName)
            if iscatname.exists():
                Products = load_file(currentCatalogName)
            else:
                currentCatalogName = ''

    if Products == []:
        Products = TreeNode(0, 'Produkte')

    Katalog = deepcopy(Products)

    app = QtWidgets.QApplication(sys.argv)
    # Load German QT Translation File
    if platform.system() == 'Linux':
        transfile = str(Path(__file__).resolve().parent) + '/resources/language'
    elif platform.system() == 'Windows':
        transfile = str(Path(__file__).resolve().parent) + r'\resources\language'
    translator = QtCore.QTranslator()
    if translator.load('qt_de', transfile):
        app.installTranslator(translator)
    # Create Windows/Widgets
    Einkaufszettel = QtWidgets.QMainWindow()
    ui = Ui_Einkaufszettel()
    ui.setupUi(Einkaufszettel)

    if platform.system() == 'Windows':
        app.setStyle('Fusion')
        darkmode()

    ChangeCat = QtWidgets.QWidget()
    ui2 = Ui_ChangeCat(ChangeCat)
    ui2.setupUi(ChangeCat)

    SetEinstellungen = QtWidgets.QWidget()
    ui3 = Ui_SetEinstellungen()
    ui3.setupUi(SetEinstellungen)

    PreislistenWebScraper = QtWidgets.QWidget()
    ui4 = Ui_PreislistenWebScraper()
    ui4.setupUi(PreislistenWebScraper)

    SearchEngine = QtWidgets.QWidget()
    ui5 = Ui_SearchEngine()
    ui5.setupUi(SearchEngine)

    About_Dialog = QtWidgets.QDialog()
    ui6 = Ui_About_Dialog()
    ui6.setupUi(About_Dialog)

    Einkaufszettel.show()
    sys.exit(app.exec_())
