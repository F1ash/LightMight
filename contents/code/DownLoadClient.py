# -*- coding: utf-8 -*-

import os, sys, os.path
from PyQt4 import QtGui, QtCore
from ui.ButtonPanel import ButtonPanel
from Functions import pathPrefix

def createStructure():
	for nameDir in [pathPref + '/dev/shm/LightMight/cache', \
					pathPref + '/dev/shm/LightMight/structure', \
					pathPref + '/dev/shm/LightMight/client', \
					pathPref + '/dev/shm/LightMight/server', \
					os.path.expanduser('~/.config/LightMight')] :
		if not os.path.isdir(nameDir):
			os.makekdirs(nameDir)

pathPref = pathPrefix()
createStructure()
app = QtGui.QApplication(sys.argv)
main = ButtonPanel(\
				sys.argv[1], sys.argv[2], sys.argv[3], \
				sys.argv[4], sys.argv[5], sys.argv[6], \
				sys.argv[7], sys.argv[8])
main.show()
sys.exit(app.exec_())
