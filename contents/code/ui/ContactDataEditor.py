# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class ContactDataEditor(QDialog):
	def __init__(self, obj = None, parent = None):
		QDialog.__init__(self, parent)

		self.Parent = parent
		self.Obj = obj
		self.setModal(False)

		self.layout = QVBoxLayout()

		self.nameLabel = QLabel(self.Obj.text())
		self.layout.addWidget(self.nameLabel)

		self.addressLabel = QLabel(self.Obj.data(Qt.AccessibleTextRole).toList()[0].toString())
		self.layout.addWidget(self.addressLabel)

		self.stateLabel = QLabel()
		self.layout.addWidget(self.stateLabel)

		self.encodeLabel = QLabel()
		self.layout.addWidget(self.encodeLabel)

		self.domainLabel = QLabel(self.Obj.data(Qt.AccessibleTextRole).toList()[2].toString())
		self.layout.addWidget(self.domainLabel)

		self.policyLabel = QLabel('Current Policy')
		self.layout.addWidget(self.policyLabel)

		self.allowedPolicySelect = QRadioButton()
		self.layout.addWidget(self.allowedPolicySelect)

		self.confirmPolicySelect = QRadioButton()
		self.layout.addWidget(self.confirmPolicySelect)

		self.blockedPolicySelect = QRadioButton()
		self.layout.addWidget(self.blockedPolicySelect)

		self.buttonPanel = QHBoxLayout()

		self.okButton = QPushButton('&Ok')
		self.okButton.clicked.connect(self.ok)
		self.buttonPanel.addWidget(self.okButton)

		self.cancelButton = QPushButton('&Cancel')
		self.cancelButton.clicked.connect(self.cancel)
		self.buttonPanel.addWidget(self.cancelButton)

		self.layout.addItem(self.buttonPanel)

		self.setLayout(self.layout)

	def ok(self):
		print 'ok'
		self.done(0)

	def cancel(self):
		self.done(0)

	def closeEvent(self, event):
		event.ignore()
		self.done(0)

	def closeEvent():
		self.done(0)
