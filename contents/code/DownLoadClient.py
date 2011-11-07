# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtGui, QtCore
from ui.ButtonPanel import ButtonPanel
from Functions import pathPrefix, createStructure

createStructure()
app = QtGui.QApplication(sys.argv)
main = ButtonPanel(\
				sys.argv[1], sys.argv[2], sys.argv[3], \
				sys.argv[4], sys.argv[5], sys.argv[6], \
				sys.argv[7], sys.argv[8], sys.argv[9])
main.show()
sys.exit(app.exec_())
