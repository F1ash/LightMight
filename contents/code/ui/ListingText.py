# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
import os, string

class ListingText(QtGui.QMessageBox):
	def __init__(self, path_, parent = None):
		QtGui.QMessageBox.__init__(self, parent)

		self.setWindowTitle('LightMight Message')
		self.setWindowModality(QtCore.Qt.NonModal)
		self.setTextFormat(QtCore.Qt.PlainText)

		if path_[:3] != 'MSG':
			self.setIcon(QtGui.QMessageBox.Information)
			f = open(path_,'rU')
			data_ = f.readlines()
			f.close()
			raw_data = string.join(data_)
			megadata = QtCore.QString.fromUtf8(raw_data)
			self.setText('About LightMight																')
			self.setDetailedText(megadata)
		else:
			self.setIcon(QtGui.QMessageBox.Warning)
			msg = QtCore.QString.fromUtf8(path_)
			self.setText(msg)
		self.addButton('Ok', QtGui.QMessageBox.YesRole)

	def closeEvent(self, event):
		event.ignore()
		self.done(0)

