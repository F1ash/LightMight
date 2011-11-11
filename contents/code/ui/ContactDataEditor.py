# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Functions import InitConfigValue

class ContactDataEditor(QDialog):
	def __init__(self, obj = None, parent = None):
		QDialog.__init__(self, parent)

		self.Parent = parent
		self.Obj = obj
		self.setWindowTitle('Contact Editor')
		self.setModal(False)

		self.layout = QVBoxLayout()

		self.nameLabel = QLabel(self.Obj.text())
		self.layout.addWidget(self.nameLabel)

		self.addressLabel = QLabel(self.Obj.data(Qt.AccessibleTextRole).toList()[0].toString())
		self.layout.addWidget(self.addressLabel)

		self.domainLabel = QLabel(self.Obj.data(Qt.AccessibleTextRole).toList()[2].toString())
		self.layout.addWidget(self.domainLabel)

		self.policyLabel = QLabel('Custom policy')
		self.layout.addWidget(self.policyLabel)

		self.policySelect = QComboBox()
		self.policySelect.addItem(QIcon(), 'Allowed')
		self.policySelect.addItem(QIcon(), 'Confirm')
		self.policySelect.addItem(QIcon(), 'Blocked')
		key = str(self.addressLabel.text().split(':')[0])
		#print [self.Parent.Obj.serverThread.Obj.currentSessionID, key]
		if key in self.Parent.Obj.serverThread.Obj.currentSessionID :
			policy = self.Parent.Obj.serverThread.Obj.currentSessionID[key][1]
			self.policySelect.setCurrentIndex(policy)
		else :
			currentCommonPolicy = InitConfigValue(self.Parent.Obj.Settings, 'CommonPolicy', 'Blocked')
			self.policySelect.setCurrentIndex(self.policySelect.findText(currentCommonPolicy))
		self.layout.addWidget(self.policySelect)

		self.specialLabel = QLabel('Special')
		self.layout.addWidget(self.specialLabel)

		self.specialListSelect = QComboBox()
		self.specialListSelect.addItem(QIcon(), 'Non-special')
		self.specialListSelect.addItem(QIcon(), 'To WhiteList')
		self.specialListSelect.addItem(QIcon(), 'To BlackList')
		self.specialListSelect.currentIndexChanged[QString].connect(self.customPolicyEnable)
		self.layout.addWidget(self.specialListSelect)

		self.buttonPanel = QHBoxLayout()

		self.okButton = QPushButton('&Ok')
		self.okButton.clicked.connect(self.ok)
		self.buttonPanel.addWidget(self.okButton)

		self.cancelButton = QPushButton('&Cancel')
		self.cancelButton.clicked.connect(self.cancel)
		self.buttonPanel.addWidget(self.cancelButton)
		self.layout.addItem(self.buttonPanel)

		self.setLayout(self.layout)

	def customPolicyEnable(self, special):
		if special == 'Non-special' :
			self.policySelect.setEnabled(True)
			return None
		elif special == 'To WhiteList' :
			self.policySelect.setCurrentIndex(self.policySelect.findText('Allowed'))
		elif special == 'To BlackList' :
			self.policySelect.setCurrentIndex(self.policySelect.findText('Blocked'))
		self.policySelect.setEnabled(False)

	def ok(self):
		#print 'ok'
		customPolicyName = self.policySelect.currentText()
		idx = self.Parent.Obj.Policy.PolicyName.index(customPolicyName)
		key = str(self.addressLabel.text().split(':')[0])
		#print [self.Parent.Obj.serverThread.Obj.currentSessionID, key]
		if key in self.Parent.Obj.serverThread.Obj.currentSessionID :
			sessionID = self.Parent.Obj.serverThread.Obj.currentSessionID[key][0]
			self.Parent.Obj.serverThread.Obj.currentSessionID[key] = (sessionID, idx)
		else :
			self.Parent.Obj.showMSG('The setting not available.\nMay be contact not cached or fail.')
		self.done(0)

	def cancel(self):
		self.done(0)

	def closeEvent(self, event):
		event.ignore()
		self.done(0)

	def closeEvent():
		self.done(0)
