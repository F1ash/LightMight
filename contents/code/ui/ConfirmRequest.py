# -*- coding: utf-8 -*-

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from Functions import *
import os

class ConfirmRequest(QDialog):
	def __init__(self, address = '', parent = None):
		QDialog.__init__(self, parent)

		self.Parent = parent
		self.address = str(address)
		self.SEP = os.sep

		self.setWindowTitle('Confirm Request')
		self.setWindowIcon(QIcon('..' + self.SEP + 'icons' + self.SEP + 'tux_partizan.png'))

		form = QGridLayout()

		self.progressBar = QProgressBar()
		self.progressBar.setOrientation(Qt.Horizontal)
		self.progressBar.setAlignment(Qt.AlignHCenter)
		self.progressBar.setValue(0)
		self.range_ = int(self.Parent.serverThread.Obj._srv.timeout -1)
		if self.range_ == 0 : self.range_ = 1
		self.progressBar.setRange(0, self.range_)
		form.addWidget(self.progressBar, 0, Qt.AlignHCenter)

		self.allowOnceButton = QPushButton('&Allow Once')
		#self.allowOnce.setMaximumWidth(75)
		self.connect(self.allowOnceButton, SIGNAL('clicked()'), self.setTemporarilyAccess)
		form.addWidget(self.allowOnceButton, 1, 0)

		self.allowSessionButton = QPushButton('&Allow Session')
		#self.allowSessionButton.setMaximumWidth(75)
		self.connect(self.allowSessionButton, SIGNAL('clicked()'), self.setAllowPolicy)
		form.addWidget(self.allowSessionButton, 1, 1)

		self.blockSessionButton = QPushButton('&Block Session')
		#self.allowSessionButton.setMaximumWidth(75)
		self.connect(self.blockSessionButton, SIGNAL('clicked()'), self.setBlockPolicy)
		form.addWidget(self.blockSessionButton, 1, 2)

		self.cancelButton = QPushButton('&Cancel')
		#self.cancelButton.setMaximumWidth(75)
		self.connect(self.cancelButton, SIGNAL('clicked()'), self.cancel)
		form.addWidget(self.cancelButton, 1, 3)

		self.setLayout(form)
		self.Timer = QTimer()
		self.Timer.timeout.connect(self.progressBarChangeVolume)
		self.Timer.start(1000)

	def setTemporarilyAccess(self, str_ = ''):
		item = self.Parent.serverThread.Obj.currentSessionID[self.address]
		if str_ == 'CANCEL' :
			temporarilySessionID = 'CANCEL'
		else :
			temporarilySessionID = randomString(DIGITS_LENGTH)
		newItem = (item[0], item[1], temporarilySessionID)
		if self.address in self.Parent.serverThread.Obj.currentSessionID :
			self.Parent.serverThread.Obj.currentSessionID[self.address] = newItem
		self.done(0)

	def setPermanentAccess(self, access):
		item = self.Parent.serverThread.Obj.currentSessionID[self.address]
		if access == self.Parent.Policy.Allowed :
			newItem = (item[0], self.Parent.Policy.Allowed)
		elif access == self.Parent.Policy.Blocked :
			newItem = (item[0], self.Parent.Policy.Blocked)
		else : return None
		if self.address in self.Parent.serverThread.Obj.currentSessionID :
			self.Parent.serverThread.Obj.currentSessionID[self.address] = newItem
		self.done(0)

	def setAllowPolicy(self):
		self.setPermanentAccess(self.Parent.Policy.Allowed)

	def setBlockPolicy(self):
		self.setPermanentAccess(self.Parent.Policy.Blocked)

	def progressBarChangeVolume(self):
		self.progressBar.setValue(self.progressBar.value() + 1)
		if self.progressBar.value() >= self.range_ : self.cancel()

	def cancel(self):
		self.setTemporarilyAccess('CANCEL')
		self.done(0)

	def closeEvent(self, event):
		event.ignore()
