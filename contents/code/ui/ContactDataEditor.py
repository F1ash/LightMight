# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Functions import *
from clnt import xr_client
from ToolsThread import ToolsThread

class ContactDataEditor(QDialog):
	def __init__(self, obj = None, parent = None):
		QDialog.__init__(self, parent)

		self.Parent = parent
		self.Obj = obj
		self.setWindowTitle('Contact Editor')
		self.setModal(True)

		self.layout = QVBoxLayout()

		self.nameLabel = QLabel(self.Obj.text())
		self.layout.addWidget(self.nameLabel)

		self.key = str(self.Obj.data(Qt.AccessibleTextRole).toList()[0].toString())
		self.addressLabel = QLabel(self.key)
		self.layout.addWidget(self.addressLabel)

		encode = self.Parent.Obj.USERS[self.key][3]
		self.encryptLabel = QLabel('Encoding: ' + encode)
		self.layout.addWidget(self.encryptLabel)

		self.myAccessLabel = QLabel('My access in :')
		self.layout.addWidget(self.myAccessLabel)

		self.serverState = str(self.Parent.Obj.USERS[self.key][4])
		self.cachedLabel = QLabel('Cached :')
		self.setCachedStatus(self.serverState)
		self.layout.addWidget(self.cachedLabel)

		self.refreshButton = QPushButton('&Info Refresh')
		self.refreshButton.clicked.connect(self.infoRefresh)
		self.layout.addWidget(self.refreshButton)

		self.policyLabel = QLabel('Custom policy')
		self.layout.addWidget(self.policyLabel)

		self.policySelect = QComboBox()
		self.policySelect.addItem(QIcon(), 'Allowed')
		self.policySelect.addItem(QIcon(), 'Confirm')
		self.policySelect.addItem(QIcon(), 'Blocked')
		key = str(self.key.split(':')[0])
		#print [self.Parent.Obj.serverThread.Obj.currentSessionID, key]
		if hasattr(self.Parent.Obj, 'serverThread') and self.Parent.Obj.serverThread is not None \
				and key in self.Parent.Obj.serverThread.Obj.currentSessionID :
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

		self.setButton = QPushButton('&Set')
		self.setButton.clicked.connect(self.set)
		self.buttonPanel.addWidget(self.setButton)

		self.cancelButton = QPushButton('&Cancel')
		self.cancelButton.clicked.connect(self.cancel)
		self.buttonPanel.addWidget(self.cancelButton)
		self.layout.addItem(self.buttonPanel)

		self.setLayout(self.layout)

	def setCachedStatus(self, serverState = ''):
		structCached = InCache(serverState)[0]
		avatarCached, name_ = avatarInCache(serverState)
		if structCached and avatarCached :
			status = 'Full'
			self.Obj.setIcon(QIcon(name_))
		elif structCached :
			status = 'Stucture'
		elif avatarCached :
			status = 'Avatar'
			self.Obj.setIcon(QIcon(name_))
		else : status = 'None'
		self.cachedLabel.setText('Cached : ' + status)

	def customPolicyEnable(self, special):
		if special == 'Non-special' :
			self.policySelect.setEnabled(True)
			return None
		elif special == 'To WhiteList' :
			self.policySelect.setCurrentIndex(self.policySelect.findText('Allowed'))
		elif special == 'To BlackList' :
			self.policySelect.setCurrentIndex(self.policySelect.findText('Blocked'))
		self.policySelect.setEnabled(False)

	def enabled_Change(self, status = False):
		self.refreshButton.setEnabled(status)
		self.policySelect.setEnabled(status)
		self.specialListSelect.setEnabled(status)
		self.setButton.setEnabled(status)
		self.cancelButton.setEnabled(status)

	def infoRefresh(self):
		self.enabled_Change(False)
		if 'clientThread' in dir(self) :
			del self.clientThread
			self.clientThread = None
		if self.Parent.Obj.USERS[self.key][3] == 'Yes' :
			encode = True
		else :
			encode = False
		addr, port = self.key.split(':')
		self.clientThread = ToolsThread(\
										xr_client(\
												addr, \
												port, \
												self.Parent.Obj, \
												self.Parent, \
												encode), \
										parent = self)
		self.clientThread.Obj.serverState = self.serverState
		self.connect(self.clientThread, SIGNAL('threadRunning'), self.refreshRun)
		self.clientThread.start()

	def refreshRun(self):
		self.disconnect(self.clientThread, SIGNAL('threadRunning'), self.refreshRun)
		addr, port = self.key.split(':')
		sessionID = ''; access = -1
		if hasattr(self.clientThread, 'runned') and self.clientThread.runned :
			# get session ID if don`t it
			if hasattr(self.Parent.Obj, 'serverThread') and self.Parent.Obj.serverThread is not None \
					and addr not in self.Parent.Obj.serverThread.Obj.currentSessionID :
				self.clientThread.Obj.getSessionID(self.Parent.Obj.server_addr)
			if hasattr(self.Parent.Obj, 'serverThread') and self.Parent.Obj.serverThread is not None \
					and addr in self.Parent.Obj.serverThread.Obj.currentSessionID :
				sessionID_ = self.Parent.Obj.serverThread.Obj.currentSessionID[addr][0]
				_keyHash = self.Parent.Obj.serverThread.Obj.currentSessionID[addr][3]
				sessionID = createEncryptedSessionID(sessionID_, _keyHash)
			#print 'session:', [sessionID]
			if sessionID != '' : access = self.clientThread.Obj.getAccess(sessionID, self.serverState)
		else :
			## contact is a dead or brocken
			self.Parent.Obj.showMSG('Contact is a dead or brocken.\nContact will be removed.')
			self.Parent.Obj.delContact(None, addr, port, None, None)
			self.done(0)
		self.clientThread._terminate()
		if access > -1 :
			text = 'My access in : ' + self.Parent.Obj.Policy.PolicyName[access]
		elif SESSION_MISMATCH == access :
			self.Parent.Obj.showMSG('Session ID mismatched.\nContact will be removed.')
			self.Parent.Obj.delContact(None, addr, port, None, None)
			self.done(0)
		else :
			text = 'My access in : Unknown'
		self.myAccessLabel.setText(text)
		self.setCachedStatus(self.serverState)
		self.enabled_Change(True)

	def set(self):
		#print 'ok'
		customPolicyName = self.policySelect.currentText()
		idx = self.Parent.Obj.Policy.PolicyName.index(customPolicyName)
		key = str(self.addressLabel.text().split(':')[0])
		#print [self.Parent.Obj.serverThread.Obj.currentSessionID, key]
		if hasattr(self.Parent.Obj, 'serverThread') and self.Parent.Obj.serverThread is not None \
				and key in self.Parent.Obj.serverThread.Obj.currentSessionID :
			sessionID = self.Parent.Obj.serverThread.Obj.currentSessionID[key][0]
			tempSessionID = self.Parent.Obj.serverThread.Obj.currentSessionID[key][2]
			_keyHash = self.Parent.Obj.serverThread.Obj.currentSessionID[key][3]
			self.Parent.Obj.serverThread.Obj.currentSessionID[key] = (sessionID, idx, tempSessionID, _keyHash)
			saveContactPolicy(idx, _keyHash)
		else :
			self.Parent.Obj.showMSG('The setting not available.\nMay be contact not cached or fail.')
		self.done(0)

	def cancel(self):
		self.done(0)

	def closeEvent(self, event):
		event.ignore()
		self.clientThread._terminate()
		self.done(0)
