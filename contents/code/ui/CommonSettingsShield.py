# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
from ListingText import ListingText
from Functions import InitConfigValue, Path, createStructure
import os, stat, os.path, shutil

class CommonSettingsShield(QtGui.QDialog):
	def __init__(self, parent = None):
		QtGui.QDialog.__init__(self, parent)

		self.Obj = parent
		self.SEP = os.sep

		self.setWindowTitle('LightMight Common Settings')
		self.setWindowIcon(QtGui.QIcon('..' + self.SEP + 'icons' + self.SEP + 'tux_partizan.png'))

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

		self.runTrayLabel = QtGui.QLabel('Run in tray :')
		form.addWidget(self.runTrayLabel, 3, 0)

		self.runTrayCheck = QtGui.QCheckBox()
		if InitConfigValue(self.Obj.Settings, 'RunInTray', 'False') == 'True' :
			value = QtCore.Qt.Checked
		else:
			value = QtCore.Qt.Unchecked
		self.runTrayCheck.setCheckState(value)
		form.addWidget(self.runTrayCheck, 3, 3)

		self.showErrorsLabel = QtGui.QLabel('Show all Error Messages :')
		form.addWidget(self.showErrorsLabel, 4, 0)

		self.showErrorsCheck = QtGui.QCheckBox()
		if InitConfigValue(self.Obj.Settings, 'ShowAllErrors', 'False') == 'True' :
			value = QtCore.Qt.Checked
		else:
			value = QtCore.Qt.Unchecked
		self.showErrorsCheck.setCheckState(value)
		form.addWidget(self.showErrorsCheck, 4, 3)

		self.useCacheLabel = QtGui.QLabel('Use Cache :')
		form.addWidget(self.useCacheLabel, 5, 0)

		self.sizeCacheLabel = QtGui.QLabel('Cache Size:')
		form.addWidget(self.sizeCacheLabel, 6, 0, 7, 1)

		value = InitConfigValue(self.Obj.Settings, 'CacheSize', '100')
		self.sizeCacheValueLabel = QtGui.QLabel(str(int(value)/100.00) + ' MB')
		self.sizeCacheValueLabel.setMinimumWidth(75)
		form.addWidget(self.sizeCacheValueLabel, 6, 1, 7, 1)

		self.sizeCacheSlider = QtGui.QSlider()
		self.sizeCacheSlider.setOrientation(QtCore.Qt.Horizontal)
		self.sizeCacheSlider.setRange(0, 1000)
		self.sizeCacheSlider.setValue(int(value))
		self.sizeCacheSlider.valueChanged.connect(self.valueSizeCacheChange)
		form.addWidget(self.sizeCacheSlider, 6, 2, 7, 4)

		self.cleanCacheLabel = QtGui.QLabel('Clean Cache :')
		form.addWidget(self.cleanCacheLabel, 14, 0)

		self.cleanAllButton = QtGui.QPushButton('&All')
		self.cleanAllButton.setMaximumWidth(75)
		self.cleanAllButton.setToolTip('Clean all cached data')
		self.connect(self.cleanAllButton, QtCore.SIGNAL('clicked()'), self.cleanAllData)
		form.addWidget(self.cleanAllButton, 14, 1)

		self.cleanAbsentButton = QtGui.QPushButton('A&bsent')
		self.cleanAbsentButton.setMaximumWidth(75)
		self.cleanAbsentButton.setToolTip('Clean cached data of absent participant')
		self.connect(self.cleanAbsentButton, QtCore.SIGNAL('clicked()'), self.cleanAbsentParticipantData)
		form.addWidget(self.cleanAbsentButton, 14, 2)

		self.policyLabel = QtGui.QLabel('Common policy')
		form.addWidget(self.policyLabel, 15, 0)

		self.policySelect = QtGui.QComboBox()
		currentCommonPolicy = InitConfigValue(self.Obj.Settings, 'CommonPolicy', 'Blocked')
		self.policySelect.addItem(QtGui.QIcon(), 'Allowed')
		self.policySelect.addItem(QtGui.QIcon(), 'Confirm')
		self.policySelect.addItem(QtGui.QIcon(), 'Blocked')
		self.policySelect.setCurrentIndex(self.policySelect.findText(currentCommonPolicy))
		form.addWidget(self.policySelect, 15, 2)

		self.okButton = QtGui.QPushButton('&Ok')
		self.okButton.setMaximumWidth(75)
		self.connect(self.okButton, QtCore.SIGNAL('clicked()'), self.ok)
		form.addWidget(self.okButton, 16, 2)

		self.cancelButton = QtGui.QPushButton('&Cancel')
		self.cancelButton.setMaximumWidth(75)
		self.connect(self.cancelButton, QtCore.SIGNAL('clicked()'), self.cancel)
		form.addWidget(self.cancelButton, 16, 3)

		self.useCacheCheck = QtGui.QCheckBox()
		if InitConfigValue(self.Obj.Settings, 'UseCache', 'True') == 'True' :
			value = QtCore.Qt.Checked
		else:
			value = QtCore.Qt.Unchecked
		self.useCacheCheck.stateChanged.connect(self.cacheSettingsHide_n_Show)
		self.useCacheCheck.setCheckState(value)
		form.addWidget(self.useCacheCheck, 5, 3)

		self.setLayout(form)
		self.cacheSettingsHide_n_Show(value)

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

	def valueSizeCacheChange(self, value):
		self.sizeCacheValueLabel.setText(str(value/100.00) + ' MB')

	def cacheSettingsHide_n_Show(self, i):
		if i == QtCore.Qt.Checked :
			self.sizeCacheLabel.show()
			self.sizeCacheSlider.show()
			self.sizeCacheValueLabel.show()
		else :
			self.sizeCacheLabel.hide()
			self.sizeCacheSlider.hide()
			self.sizeCacheValueLabel.hide()

	def cleanAllData(self):
		shutil.rmtree(Path.Cache, ignore_errors = True)
		createStructure()

	def cleanAbsentParticipantData(self):
		statesList = []
		for item in self.Obj.USERS.values() : statesList.append(item[4]) 
		#print statesList
		for name in os.listdir(Path.Cache) :
			if name not in statesList :
				if os.path.isfile(Path.cache(name)) : os.remove(Path.cache(name))
				if os.path.isfile(Path.avatar(name)) : os.remove(Path.avatar(name))
				if os.path.isfile(Path.tempCache(name)) : os.remove(Path.tempCache(name))
				if os.path.isfile(Path.tempAvatar(name)) : os.remove(Path.tempAvatar(name))

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
		if self.showErrorsCheck.isChecked() :
			value = 'True'
		else :
			value = 'False'
		self.Obj.Settings.setValue('ShowAllErrors', value)
		if self.useCacheCheck.isChecked() :
			value = 'True'
			self.Obj.Settings.setValue('CacheSize', str(self.sizeCacheSlider.value()))
		else :
			value = 'False'
		self.Obj.Settings.setValue('UseCache', value)
		self.Obj.Policy.setPolicy(self.policySelect.currentText())
		self.Obj.Settings.sync()

	def closeEvent(self, event):
		event.ignore()
		self.done(0)
