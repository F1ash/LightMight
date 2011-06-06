# -*- coding: utf-8 -*-

import os, sys, os.path
from PyQt4 import QtGui, QtCore
from ui.ButtonPanel import ButtonPanel

def createStructure():
	for nameDir in ['/dev/shm/LightMight', '/dev/shm/LightMight/cache', \
					'/dev/shm/LightMight/structure', '/dev/shm/LightMight/client', \
					'/dev/shm/LightMight/server', os.path.expanduser('~/.config/LightMight')] :
		if not os.path.isdir(nameDir):
			os.mkdir(nameDir)

#os.system('cd $HOME && xauth merge /dev/shm/dsa && rm /dev/shm/dsa')
#name_ = os.path.basename(sys.argv[0])
#print sys.argv[0][:-len(name_)]
#os.chdir(sys.argv[0][:-len(name_)])
createStructure()
app = QtGui.QApplication(sys.argv)
main = ButtonPanel(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7])
main.show()
sys.exit(app.exec_())
