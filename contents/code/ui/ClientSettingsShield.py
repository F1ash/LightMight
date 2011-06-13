# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
from ListingText import ListingText
from Functions import InitConfigValue
import os

class ClientSettingsShield(QtGui.QDialog):
	def __init__(self, obj = None, parent = None):
		QtGui.QDialog.__init__(self, parent)

		self.Obj = obj

		self.setWindowTitle('LightMight Client Settings')
		self.setWindowIcon(QtGui.QIcon('../icons/tux_partizan.png'))

		form = QtGui.QGridLayout()

		"""self.listenPort = QtGui.QLabel('Listen Port Diapason :')
		form.addWidget(self.listenPort, 0, 1)

		self.checkMinPortBox = QtGui.QSpinBox()
		self.checkMinPortBox.setMinimum(0)
		self.checkMinPortBox.setMaximum(65535)
		self.checkMinPortBox.setValue(34100)
		self.checkMinPortBox.setSingleStep(1)
		form.addWidget(self.checkMinPortBox, 0, 2)

		self.checkMaxPortBox = QtGui.QSpinBox()
		self.checkMaxPortBox.setMinimum(0)
		self.checkMaxPortBox.setMaximum(65535)
		self.checkMaxPortBox.setValue(34200)
		self.checkMaxPortBox.setSingleStep(1)
		form.addWidget(self.checkMaxPortBox, 1, 2)

		self.useAvahi = QtGui.QLabel('Use Avahi Service (Zeroconf) :')
		form.addWidget(self.useAvahi, 2, 1)

		self.checkUseAvahi = QtGui.QCheckBox()
		self.checkUseAvahi.setCheckState(QtCore.Qt.Unchecked)
		form.addWidget(self.checkUseAvahi, 2, 2)
		"""

		self.upLoadPathLabel = QtGui.QLabel('DownLoad Path :')
		form.addWidget(self.upLoadPathLabel, 3, 0)

		path_ = InitConfigValue(self.Obj.Settings, 'DownLoadTo', '/tmp/LightMight/DownLoad')
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


