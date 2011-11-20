#!/usr/bin/python 
# -*- coding: utf-8 -*-

import os, sys, locale
from PyQt4 import QtGui, QtCore
from ui import MainWindow
from Functions import pathPrefix, InitConfigValue, createStructure

#os.system('cd $HOME && xauth merge /dev/shm/dsa && rm /dev/shm/dsa')
name_ = os.path.basename(sys.argv[0])
#print sys.argv[0][:-len(name_)]
os.chdir(sys.argv[0][:-len(name_)])
#lang = locale.getdefaultlocale()
locale.setlocale(locale.LC_ALL, 'C')
createStructure()
app = QtGui.QApplication(sys.argv)
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
