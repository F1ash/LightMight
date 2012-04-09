#!/usr/bin/python 
# -*- coding: utf-8 -*-

import os, sys, locale, os.path
from PyQt4 import QtGui, QtCore
from ui import MainWindow
from Functions import InitConfigValue, createStructure

locale.setlocale(locale.LC_ALL, 'C')
createStructure()
app = QtGui.QApplication(sys.argv)
os.chdir(os.path.split(sys.argv[0])[0])
pixmap = QtGui.QPixmap ('..' + os.sep + 'icons' + os.sep + 'tux_partizan.png')
splash = QtGui.QSplashScreen (pixmap, QtCore.Qt.WindowStaysOnTopHint)
splash.show()
app.processEvents()
main = MainWindow()
if InitConfigValue(main.Settings, 'RunInTray', 'False') == 'True' :
	main.hide()
else :
	main.show()
#splash.showMessage(" 00001\n", QtCore.Qt.AlignCenter, QtCore.Qt.yellow)
#app.processEvents()
splash.finish(main)
sys.exit(app.exec_())
