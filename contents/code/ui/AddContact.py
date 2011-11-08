# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
from ListingText import ListingText
from mcastSender import _send_mcast as Sender
from Functions import InitConfigValue
import os

class AddContact(QtGui.QDialog):
	def __init__(self, parent = None):
		QtGui.QDialog.__init__(self, parent)

		self.Parent = parent
		self.SEP = os.sep

		self.setWindowTitle('Connect to New Contact')
		self.setWindowIcon(QtGui.QIcon('..' + self.SEP + 'icons' + self.SEP + 'tux_partizan.png'))

		form = QtGui.QGridLayout()

		self.addrString = QtGui.QLineEdit()
		form.addWidget(self.addrString, 1, 0, 2, 4)

		self.okButton = QtGui.QPushButton('&Ok')
		self.okButton.setMaximumWidth(75)
		self.connect(self.okButton, QtCore.SIGNAL('clicked()'), self.ok)
		form.addWidget(self.okButton, 4, 2)

		self.cancelButton = QtGui.QPushButton('&Cancel')
		self.cancelButton.setMaximumWidth(75)
		self.connect(self.cancelButton, QtCore.SIGNAL('clicked()'), self.cancel)
		form.addWidget(self.cancelButton, 4, 3)

		self.setLayout(form)

	def ok(self):
		addr = str(self.addrString.text())
		name_ = InitConfigValue(self.Parent.Obj.Settings, 'ServerName', 'Own Avahi Server')
		if self.Parent.Obj.TLS :
			encode = 'Yes'
		else :
			encode = 'No'
		data = QtCore.QString('1' + '<||>' + \
							  name_ + '<||>' + \
							  self.Parent.Obj.server_addr + '<||>' + \
							  str(self.Parent.Obj.server_port) + '<||>' + \
							  encode + '<||>' + \
							  self.Parent.Obj.serverState + '<||>' + \
							  '*infoShare*')
		Sender(data, addr)
		self.done(0)

	def cancel(self):
		self.done(0)

	def closeEvent(self, event):
		event.ignore()
		self.done(0)
