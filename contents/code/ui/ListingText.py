# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
import os, string

class ListingText(QtGui.QDialog):
	def __init__(self, path_, parent = None):
		QtGui.QDialog.__init__(self, parent)

		self.setWindowTitle('LightMight Message')
		self.setWindowIcon(QtGui.QIcon('../icons/tux_partizan.png'))

		browseText = QtGui.QTextEdit()
		browseText.setReadOnly(True)

		if path_[:3] != 'MSG':
			f = open(path_,'rU')
			data_ = f.readlines()
			f.close()
			raw_data = string.join(data_)
			megadata = QtCore.QString.fromUtf8(raw_data)
			browseText.setText(megadata)
			width_ = '450'
		else:
			path_ = QtCore.QString.fromUtf8(path_)
			browseText.setText(path_)
			width_ = '750'

		form = QtGui.QGridLayout()
		form.addWidget(browseText,0,0)
		self.setLayout(form)
		self.resize(int(width_, 10), 100)

	def closeEvent(self, event):
		event.ignore()
		self.done(0)

