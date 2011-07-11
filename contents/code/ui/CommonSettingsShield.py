# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
from ListingText import ListingText
from Functions import InitConfigValue, pathPrefix
import os, stat, os.path

class CommonSettingsShield(QtGui.QDialog):
	def __init__(self, obj = None, parent = None):
		QtGui.QDialog.__init__(self, parent)

		self.Obj = obj
		self.pathPref = pathPrefix()

		self.setWindowTitle('LightMight Common Settings')
		self.setWindowIcon(QtGui.QIcon('../icons/tux_partizan.png'))

		form = QtGui.QGridLayout()

		self.avatarLabel = QtGui.QLabel('Avatar :')
		form.addWidget(self.avatarLabel, 0, 0)

		self.avatarPathButton = QtGui.QPushButton('&Path')
		self.avatarPathButton.setMaximumWidth(75)
		self.avatarPathButton.setToolTip('Set pat to Avatar')
		self.connect(self.avatarPathButton, QtCore.SIGNAL('clicked()'), self.avatarPath)
		form.addWidget(self.avatarPathButton, 0, 3)

		self.avatarPathString = QtGui.QLineEdit(self.Obj.avatarPath)
		form.addWidget(self.avatarPathString, 1, 0, 2, 4)

		self.useCacheLabel = QtGui.QLabel('Use Cache :')
		form.addWidget(self.useCacheLabel, 3, 0)

		self.useCacheCheck = QtGui.QCheckBox()
		if InitConfigValue(self.Obj.Settings, 'UseCache', 'True') == 'True' :
			value = QtCore.Qt.Checked
		else:
			value = QtCore.Qt.Unchecked
		self.useCacheCheck.setCheckState(value)
		form.addWidget(self.useCacheCheck, 3, 3)

		self.runTrayLabel = QtGui.QLabel('Run in tray :')
		form.addWidget(self.runTrayLabel, 4, 0)

		self.runTrayCheck = QtGui.QCheckBox()
		if InitConfigValue(self.Obj.Settings, 'RunInTray', 'False') == 'True' :
			value = QtCore.Qt.Checked
		else:
			value = QtCore.Qt.Unchecked
		self.runTrayCheck.setCheckState(value)
		form.addWidget(self.runTrayCheck, 4, 3)

		self.okButton = QtGui.QPushButton('&Ok')
		self.okButton.setMaximumWidth(75)
		self.connect(self.okButton, QtCore.SIGNAL('clicked()'), self.ok)
		form.addWidget(self.okButton, 14, 2)

		self.cancelButton = QtGui.QPushButton('&Cancel')
		self.cancelButton.setMaximumWidth(75)
		self.connect(self.cancelButton, QtCore.SIGNAL('clicked()'), self.cancel)
		form.addWidget(self.cancelButton, 14, 3)

		self.setLayout(form)

	def avatarPath(self):
		fileName = QtGui.QFileDialog.getOpenFileName(self, 'Path_to_', '~', 'Images PNG (*.png);; Images GIF (*.gif);; Images JPEG (*.jpeg);; Images JPG (*.jpg)')
		name_ = QtCore.QString(fileName).toUtf8().data()
		if not stat.S_ISLNK(os.lstat(name_).st_mode) and os.access(name_, os.R_OK) :
			if os.lstat(name_).st_size < 25600 :
				self.avatarPathString.setText(unicode(fileName))
				self.Obj.avatarPath = unicode(fileName)
			else :
				showHelp = ListingText("MSG: file more then 25 KBytes : " + name_, self)
				showHelp.exec_()
		else :
			showHelp = ListingText("MSG: incorrect Path\n(access denied) or symLink : " + name_, self)
			showHelp.exec_()

	def ok(self):
		self.saveData()
		self.done(0)

	def cancel(self):
		self.done(0)

	def saveData(self):
		self.Obj.Settings.setValue('AvatarPath', self.avatarPathString.text())
		if self.runTrayCheck.isChecked() :
			value = 'True'
		else :
			value = 'False'
		self.Obj.Settings.setValue('RunInTray', value)
		if self.useCacheCheck.isChecked() :
			value = 'True'
		else :
			value = 'False'
		self.Obj.Settings.setValue('UseCache', value)
		self.Obj.Settings.sync()

	def closeEvent(self, event):
		event.ignore()
		self.done(0)

