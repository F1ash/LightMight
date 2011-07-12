# -*- coding: utf-8 -*-

import os, sys
from PyQt4 import QtGui, QtCore
from ui import MainWindow
from Functions import pathPrefix, InitConfigValue, createStructure

#os.system('cd $HOME && xauth merge /dev/shm/dsa && rm /dev/shm/dsa')
name_ = os.path.basename(sys.argv[0])
#print sys.argv[0][:-len(name_)]
os.chdir(sys.argv[0][:-len(name_)])
createStructure()
app = QtGui.QApplication(sys.argv)
main = MainWindow()
if InitConfigValue(main.Settings, 'RunInTray', 'False') == 'True' :
	main.hide()
else :
	main.show()
sys.exit(app.exec_())
