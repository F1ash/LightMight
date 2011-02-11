# -*- coding: utf-8 -*-

import os, sys, os.path, stat, gc, xml.parsers.expat
from PyQt4 import QtGui, QtCore
from Parser import Parser
#from TreeProc import TreeItem, TreeModel
#from TreeProcess import TreeProcessing
#from xml.dom.minidom import Document, parse

# my changes
from ui import MainWindow
from TreeSettingThread import TreeSettingThread

FileNameList = []
FileNameList2UpLoad = []

def createStructure():
	for nameDir in ['/dev/shm/LightMight', '/dev/shm/LightMight/cache', '/dev/shm/LightMight/structure'] :
		if not os.path.isdir(nameDir):
			os.mkdir(nameDir)

#os.system('cd $HOME && xauth merge /dev/shm/dsa && rm /dev/shm/dsa')
gc.enable()
gc.set_debug(gc.DEBUG_UNCOLLECTABLE)
name_ = os.path.basename(sys.argv[0])
#print sys.argv[0][:-len(name_)]
os.chdir(sys.argv[0][:-len(name_)])
createStructure()
GeneralLOCK = QtCore.QMutex()
TSThread = TreeSettingThread()
app = QtGui.QApplication(sys.argv)
main = MainWindow()
main.show()
sys.exit(app.exec_())
