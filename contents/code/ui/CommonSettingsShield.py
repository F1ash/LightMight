# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
from ListingText import ListingText
from Functions import InitConfigValue, pathPrefix, createStructure
import os, stat, os.path, shutil

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

		self.runTrayLabel = QtGui.QLabel('Run in tray :')
		form.addWidget(self.runTrayLabel, 3, 0)

		self.runTrayCheck = QtGui.QCheckBox()
		if InitConfigValue(self.Obj.Settings, 'RunInTray', 'False') == 'True' :
			value = QtCore.Qt.Checked
		else:
			value = QtCore.Qt.Unchecked
		self.runTrayCheck.setCheckState(value)
		form.addWidget(self.runTrayCheck, 3, 3)

		self.useCacheLabel = QtGui.QLabel('Use Cache :')
		form.addWidget(self.useCacheLabel, 4, 0)

		self.sizeCacheLabel = QtGui.QLabel('Cache Size:')
		form.addWidget(self.sizeCacheLabel, 5, 0, 6, 1)

		value = InitConfigValue(self.Obj.Settings, 'CacheSize', '100')
		self.sizeCacheValueLabel = QtGui.QLabel(str(int(value)/100.00) + ' MB')
		self.sizeCacheValueLabel.setMinimumWidth(75)
		form.addWidget(self.sizeCacheValueLabel, 5, 1, 6, 1)

		self.sizeCacheSlider = QtGui.QSlider()
		self.sizeCacheSlider.setOrientation(QtCore.Qt.Horizontal)
		self.sizeCacheSlider.setRange(0, 1000)
		self.sizeCacheSlider.setValue(int(value))
		self.sizeCacheSlider.valueChanged.connect(self.valueSizeCacheChange)
		form.addWidget(self.sizeCacheSlider, 5, 2, 6, 4)

		self.cleanCacheLabel = QtGui.QLabel('Clean Cache :')
		form.addWidget(self.cleanCacheLabel, 13, 0)

		self.cleanAllButton = QtGui.QPushButton('&All')
		self.cleanAllButton.setMaximumWidth(75)
		self.cleanAllButton.setToolTip('Clean all cached data')
		self.connect(self.cleanAllButton, QtCore.SIGNAL('clicked()'), self.cleanAllData)
		form.addWidget(self.cleanAllButton, 13, 1)

		self.cleanAbsentButton = QtGui.QPushButton('A&bsent')
		self.cleanAbsentButton.setMaximumWidth(75)
		self.cleanAbsentButton.setToolTip('Clean cached data of absent participant')
		self.connect(self.cleanAbsentButton, QtCore.SIGNAL('clicked()'), self.cleanAbsentParticipantData)
		form.addWidget(self.cleanAbsentButton, 13, 2)

		self.okButton = QtGui.QPushButton('&Ok')
		self.okButton.setMaximumWidth(75)
		self.connect(self.okButton, QtCore.SIGNAL('clicked()'), self.ok)
		form.addWidget(self.okButton, 14, 2)

		self.cancelButton = QtGui.QPushButton('&Cancel')
		self.cancelButton.setMaximumWidth(75)
		self.connect(self.cancelButton, QtCore.SIGNAL('clicked()'), self.cancel)
		form.addWidget(self.cancelButton, 14, 3)

		self.useCacheCheck = QtGui.QCheckBox()
		if InitConfigValue(self.Obj.Settings, 'UseCache', 'True') == 'True' :
			value = QtCore.Qt.Checked
		else:
			value = QtCore.Qt.Unchecked
		self.useCacheCheck.stateChanged.connect(self.cacheSettingsHide_n_Show)
		self.useCacheCheck.setCheckState(value)
		form.addWidget(self.useCacheCheck, 4, 3)

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
		shutil.rmtree(self.pathPref + os.path.expanduser('~/.cache/LightMight/'), ignore_errors = True)
		createStructure()

	def cleanAbsentParticipantData(self):
		""" получить список состояний уд.серверов на данный момент;
			если имя файла из кеша не входит в список состояний,
			то файл удалить
		"""
		statesList = []
		for item in self.Obj.avahiBrowser.USERS.values() : statesList.append(item[4]) 
		print statesList
		for name in os.listdir(self.pathPref + os.path.expanduser('~/.cache/LightMight/')) :
			if os.path.isfile(name) and name not in statesList :
				os.remove(self.pathPref + os.path.expanduser('~/.cache/LightMight/') + name)
				os.remove(self.pathPref + os.path.expanduser('~/.cache/LightMight/avatars/') + name)

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
			self.Obj.Settings.setValue('CacheSize', str(self.sizeCacheSlider.value()))
		else :
			value = 'False'
		self.Obj.Settings.setValue('UseCache', value)
		self.Obj.Settings.sync()

	def closeEvent(self, event):
		event.ignore()
		self.done(0)

