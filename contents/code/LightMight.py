# -*- coding: utf-8 -*-

import os, sys, os.path
from PyQt4 import QtGui, QtCore
from ui import MainWindow
from Functions import pathPrefix

def createStructure():
	for nameDir in [pathPref + '/dev/shm/LightMight/cache', \
					pathPref + '/dev/shm/LightMight/structure', \
					pathPref + '/dev/shm/LightMight/client', \
					pathPref + '/dev/shm/LightMight/server', \
					os.path.expanduser('~/.config/LightMight/treeBackup')] :
		if not os.path.isdir(nameDir):
			os.makedirs(nameDir)

#os.system('cd $HOME && xauth merge /dev/shm/dsa && rm /dev/shm/dsa')
name_ = os.path.basename(sys.argv[0])
#print sys.argv[0][:-len(name_)]
os.chdir(sys.argv[0][:-len(name_)])
pathPref = pathPrefix()
createStructure()
app = QtGui.QApplication(sys.argv)
main = MainWindow()
main.show()
sys.exit(app.exec_())
