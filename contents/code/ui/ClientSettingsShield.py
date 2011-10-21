# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
from ListingText import ListingText
from Functions import InitConfigValue, Path
import os

class ClientSettingsShield(QtGui.QDialog):
	def __init__(self, obj = None, parent = None):
		QtGui.QDialog.__init__(self, parent)

		self.Obj = obj
		self.SEP = os.sep

		self.setWindowTitle('LightMight Client Settings')
		self.setWindowIcon(QtGui.QIcon('..' + self.SEP + 'icons' + self.SEP + 'tux_partizan.png'))

		form = QtGui.QGridLayout()

		self.upLoadPathLabel = QtGui.QLabel('DownLoad Path :')
		form.addWidget(self.upLoadPathLabel, 3, 0)

		path_ = InitConfigValue(self.Obj.Settings, 'DownLoadTo', Path.Temp)
		self.upLoadPathString = QtGui.QLineEdit(path_)
		form.addWidget(self.upLoadPathString, 4, 0, 4, 2)

		self.upLoadPathButton = QtGui.QPushButton('&Path')
		self.upLoadPathButton.setMaximumWidth(75)
		self.connect(self.upLoadPathButton, QtCore.SIGNAL('clicked()'), self.getPath)
		form.addWidget(self.upLoadPathButton, 3, 1)

		self.cancelButton = QtGui.QPushButton('&Cancel')
		self.cancelButton.setMaximumWidth(75)
		self.connect(self.cancelButton, QtCore.SIGNAL('clicked()'), self.cancel)
		form.addWidget(self.cancelButton, 4, 2, 4, 2)

		self.okButton = QtGui.QPushButton('&Ok')
		self.okButton.setMaximumWidth(75)
		self.connect(self.okButton, QtCore.SIGNAL('clicked()'), self.ok)
		form.addWidget(self.okButton, 3, 2)

		nullColumn = QtGui.QLabel('')
		nullColumn.setMaximumWidth(5)
		form.addWidget(nullColumn, 4, 3)

		self.setLayout(form)

	def getPath(self):
		_nameDir = QtGui.QFileDialog.getExistingDirectory(self, 'Path_to_', '~', QtGui.QFileDialog.ShowDirsOnly)
		nameDir = QtCore.QString(_nameDir).toUtf8().data()
		if os.access(nameDir, os.R_OK) and os.access(nameDir, os.W_OK) and os.access(nameDir, os.X_OK) :
			self.upLoadPathString.setText(_nameDir)
		else :
			showHelp = ListingText("MSG: uncorrect Path (or access denied) : " + nameDir, self)
			showHelp.exec_()

	def ok(self):
		self.saveData()
		self.done(0)

	def saveData(self):
		self.Obj.Settings.setValue('DownLoadTo', self.upLoadPathString.text())
		self.Obj.Settings.sync()

	def cancel(self):
		self.done(0)

	def closeEvent(self, event):
		event.ignore()
		self.done(0)


