# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
import os, string

class ListingText(QtGui.QMessageBox):
	def __init__(self, path_, parent = None):
		QtGui.QMessageBox.__init__(self, parent)

		self.setWindowTitle('LightMight Message')

		if path_[:3] != 'MSG':
			self.setIcon(QtGui.QMessageBox.Information)
			f = open(path_,'rU')
			data_ = f.readlines()
			f.close()
			raw_data = string.join(data_)
			megadata = QtCore.QString.fromUtf8(raw_data)
			self.setText(megadata)
			width_ = '450'
		else:
			self.setIcon(QtGui.QMessageBox.Warning)
			msg = QtCore.QString.fromUtf8(path_)
			self.setText(msg)
			width_ = '750'
		self.addButton('Ok', QtGui.QMessageBox.YesRole)
		self.resize(int(width_, 10), 100)

	def closeEvent(self, event):
		event.ignore()
		self.done(0)

