# -*- coding: utf-8 -*-

from PyQt4.QtGui import *
from PyQt4.QtCore import *
import os

class ConfirmRequest(QDialog):
	def __init__(self, parent = None):
		QDialog.__init__(self, parent)

		self.Parent = parent
		self.SEP = os.sep

		self.setWindowTitle('Confirm Request')
		self.setWindowIcon(QIcon('..' + self.SEP + 'icons' + self.SEP + 'tux_partizan.png'))

		form = QGridLayout()

		self.addrString = QLineEdit()
		self.addrString.setToolTip('Enter IP of client')
		form.addWidget(self.addrString, 1, 0, 2, 4)

		self.okButton = QPushButton('&Ok')
		self.okButton.setMaximumWidth(75)
		self.connect(self.okButton, SIGNAL('clicked()'), self.ok)
		form.addWidget(self.okButton, 4, 2)

		self.cancelButton = QPushButton('&Cancel')
		self.cancelButton.setMaximumWidth(75)
		self.connect(self.cancelButton, SIGNAL('clicked()'), self.cancel)
		form.addWidget(self.cancelButton, 4, 3)

		self.setLayout(form)

	def ok(self):
		self.done(0)

	def cancel(self):
		self.done(10)

	def closeEvent(self, event):
		event.ignore()
		self.done(10)

