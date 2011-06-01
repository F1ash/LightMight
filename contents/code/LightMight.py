# -*- coding: utf-8 -*-

import os, sys, os.path, stat, gc, xml.parsers.expat
from PyQt4 import QtGui, QtCore
from ui import MainWindow

def createStructure():
	for nameDir in ['/dev/shm/LightMight', '/dev/shm/LightMight/cache', \
					'/dev/shm/LightMight/structure', '/dev/shm/LightMight/client', \
					'/dev/shm/LightMight/server', os.path.expanduser('~/.config/LightMight')] :
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
app = QtGui.QApplication(sys.argv)
main = MainWindow()
main.show()
sys.exit(app.exec_())
