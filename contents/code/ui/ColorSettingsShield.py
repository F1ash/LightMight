# -*- coding: utf-8 -*-

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from Functions import InitConfigValue, Path
import os

class ColorSettingsShield(QDialog):
	def __init__(self, parent = None):
		QDialog.__init__(self, parent)

		self.Obj = parent
		self.SEP = os.sep

		self.setWindowTitle('LightMight Client Settings')
		self.setWindowIcon(QIcon('..' + self.SEP + 'icons' + self.SEP + 'tux_partizan.png'))

		form = QGridLayout()

		self.fontColorLabel = QLabel('Font Color')
		form.addWidget(self.fontColorLabel, 0, 0)

		path_ = InitConfigValue(self.Obj.Settings, 'DownLoadTo', Path.Temp)

		self.fontColorButton = QPushButton('&Path')
		self.fontColorButton.setMaximumWidth(75)
		self.connect(self.fontColorButton, SIGNAL('clicked()'), self.getFontColor)
		form.addWidget(self.fontColorButton, 0, 3)

		self.backgroundLabel = QLabel('Background')
		form.addWidget(self.backgroundLabel, 1, 0)

		self.backgroundButton = QPushButton('&Path')
		self.backgroundButton.setMaximumWidth(75)
		self.connect(self.backgroundButton, SIGNAL('clicked()'), self.getBackGroundColor)
		form.addWidget(self.backgroundButton, 1, 3)

		self.okButton = QPushButton('&Ok')
		self.okButton.setMaximumWidth(75)
		self.connect(self.okButton, SIGNAL('clicked()'), self.ok)
		form.addWidget(self.okButton, 3, 1)

		self.cancelButton = QPushButton('&Cancel')
		self.cancelButton.setMaximumWidth(75)
		self.connect(self.cancelButton, SIGNAL('clicked()'), self.cancel)
		form.addWidget(self.cancelButton, 3, 2)

		self.setLayout(form)
		#color, yes, style = self.getColor()
		#print style, 'styleSheet', self.getRGBaStyle((int(color), yes))
		self.currentFontColor = InitConfigValue(self.Obj.Settings, 'FontColor', self.getSystemColor('int'))
		self.currentBGrdColor = InitConfigValue(self.Obj.Settings, 'BackGroundColor', self.getSystemColor('int'))

	def getFontColor(self):
		color, yes = self.getColor(self.currentFontColor)
		if yes :
			self.currentFontColor = color
			self.setWidgetColors()

	def getBackGroundColor(self):
		color, yes = self.getColor(self.currentBGrdColor)
		if yes :
			self.currentBGrdColor = color
			self.setWidgetColors()

	def setWidgetColors(self):
		self.setStyleSheet('QWidget { background: rgba' + self.getRGBaStyle((int(self.currentBGrdColor), True)) + ';} \
							QLabel { color: rgba' + self.getRGBaStyle((int(self.currentFontColor), True)) + ';}')

	def getColor(self, currentColor = ''):
		colour = QColorDialog()
		if currentColor == '' : currentColor = self.getSystemColor('int')
		selectColour, _yes = colour.getRgba(int(currentColor))
		colour.done(0)
		return str(selectColour), _yes

	def getRGBaStyle(self, (colour, yes)):
		if yes :
			style = str(QColor().fromRgba(colour).getRgb())
		else :
			style = self.getSystemColor()
		return style

	def getSystemColor(self, key_ = ''):
		currentBrush = QPalette().windowText()
		colour = currentBrush.color()
		if key_ == 'int' :
			#print colour.rgba()
			return str(colour.rgba())
		else :
			#print str(colour.getRgb())
			return str(colour.getRgb())

	def ok(self):
		self.saveData()
		self.done(0)

	def saveData(self):
		#self.Obj.Settings.setValue('DownLoadTo', self.upLoadPathString.text())
		self.Obj.Settings.sync()

	def cancel(self):
		self.done(0)

	def closeEvent(self, event):
		event.ignore()
		self.done(0)
