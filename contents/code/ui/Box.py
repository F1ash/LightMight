# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
from TreeProc import TreeModel
from TreeItem import TreeItem
from TreeProcess import TreeProcessing
from TreeBox import TreeBox
from AddContact import AddContact
from clnt import xr_client
from ToolsThread import ToolsThread
from Wait import SetupTree
from Functions import InCache, Path, moveFile, DelFromCache, InitConfigValue
from os.path import basename as BaseName
from mcastSender import _send_mcast as Sender
import os, shutil

class Box(QtGui.QWidget):
	complete = QtCore.pyqtSignal()
	tree = QtCore.pyqtSignal(TreeItem, int, int)
	data = QtCore.pyqtSignal(TreeBox)
	setAvatar = QtCore.pyqtSignal(QtGui.QListWidgetItem, str)
	def __init__(self, Obj_, parent = None):
		QtGui.QWidget.__init__(self, parent)

		self.Obj = Obj_

		self.treeModel = TreeModel('Name', 'Description', parent = self)
		self.treeProcessing = TreeProcessing()
		
		viewMode = self.Obj.Settings.value('ViewMode', 'TreeMode').toString()
		self.sharedTree = TreeBox(self.treeModel, self, viewMode)

		self.layout = QtGui.QGridLayout()
		self.layout.setColumnStretch(0, 0)

		self.userList = QtGui.QListWidget()
		self.userList.setToolTip('Users in Web')
		self.userList.setMaximumWidth(250)
		#self.userList.setMinimumSize(100, 75)
		self.userList.setSortingEnabled(True)
		self.userList.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self.userList.itemDoubleClicked.connect(self.itemSharedSourceQuired)
		self.layout.addWidget(self.userList, 0, 0)

		self.buttonLayout = QtGui.QVBoxLayout()
		self.buttonLayout.addStretch(0)

		self.progressBar = QtGui.QProgressBar()
		self.progressBar.setOrientation(QtCore.Qt.Vertical)
		self.progressBar.setAlignment(QtCore.Qt.AlignHCenter)
		self.progressBar.setRange(0, 0)
		self.progressBar.hide()
		self.buttonLayout.addWidget(self.progressBar, 0, QtCore.Qt.AlignHCenter)

		self.addContactButton = QtGui.QPushButton(QtCore.QString('&Add'))
		self.addContactButton.setToolTip('Add Contact')
		self.addContactButton.setMaximumWidth(65)
		self.connect(self.addContactButton, QtCore.SIGNAL('clicked()'), self.addContact)
		self.buttonLayout.addWidget(self.addContactButton, 0, QtCore.Qt.AlignHCenter)

		self.treeButton = QtGui.QPushButton(QtCore.QString('&Tree'))
		self.treeButton.setToolTip('Show Tree \nof Shared Source')
		self.treeButton.setMaximumWidth(65)
		self.connect(self.treeButton, QtCore.SIGNAL('clicked()'), self.hide_n_showTree)
		self.buttonLayout.addWidget(self.treeButton, 0, QtCore.Qt.AlignHCenter)

		self.refreshButton = QtGui.QPushButton(QtCore.QString('&R'))
		self.refreshButton.setToolTip('Restart Server')
		self.refreshButton.setMaximumWidth(65)
		self.connect(self.refreshButton, QtCore.SIGNAL('clicked()'), self.restartServer)
		self.buttonLayout.addWidget(self.refreshButton, 0, QtCore.Qt.AlignHCenter)

		self.layout.addItem(self.buttonLayout, 0, 2)

		self.setLayout(self.layout)

		self.currentTreeEncode = False

		self.complete.connect(self.hideProgressBar)
		self.tree.connect(self.showTree)
		self.data.connect(self.changeViewMode)
		self.setAvatar.connect(self.setContactAvatar)

	def addContact(self):
		_AddContact = AddContact(self)
		_AddContact.exec_()

	def showSharedSources(self, str_ = ''):
		if not self.progressBar.isVisible() : self.progressBar.show()
		path = str_
		#print path, ' representation structure file'
		self.treeModel = TreeModel('Name', 'Description', parent = self)
		#self.threadSetupTree = SetupTree(self.treeProcessing, [path], self.treeModel.rootItem, self, False, self)
		#self.threadSetupTree.start()
		count, downLoads = self.treeProcessing.setupItemData([path], self.treeModel.rootItem)
		self.hideProgressBar()
		self.showTree(self.treeModel.rootItem, count, downLoads)

	def setContactAvatar(self, item_, name_):
		item_.setIcon(QtGui.QIcon(Path.tempAvatar(name_)))

	def searchItem(self, addr):
		count = self.userList.count()
		for i in xrange(count) :
			item_ = self.userList.item(i)
			if str(item_.data(QtCore.Qt.AccessibleTextRole).toList()[0].toString()) == addr :
				self.setAvatar.emit(item_, self.Obj.USERS[addr][4])
				break

	def _showSharedSources(self):
		self.progressBar.show()
		#print 'not cached'
		addr = self.clientThread.Obj.servaddr
		key = addr.split(':')[0]
		# get session ID if don`t it
		if key not in self.Obj.serverThread.Obj.currentSessionID :
			self.clientThread.Obj.getSessionID(self.Obj.server_addr)
		if key in self.Obj.serverThread.Obj.currentSessionID :
			sessionID = self.Obj.serverThread.Obj.currentSessionID[key]
		else :
			sessionID = ''
		path, previousState = self.clientThread.getSharedSourceStructFile(sessionID)
		self.clientThread.Obj.getAvatar(sessionID)
		""" search USERS key with desired value for set it in "cached" """
		Value = BaseName(path)
		for itemValue in self.Obj.USERS.iteritems() :
			if itemValue[1][4] == Value :
				#print Value, 'state found'
				self.Obj.USERS[itemValue[0]] = (itemValue[1][0], \
												itemValue[1][1], \
												itemValue[1][2], \
												itemValue[1][3], \
												itemValue[1][4], \
												True)
				self.searchItem(str(itemValue[1][1] + ':' + itemValue[1][2]))
				break
		if previousState != '' : DelFromCache(previousState)
		self.showSharedSources(path)

	def hideProgressBar(self):
		self.progressBar.hide()
		self.sharedTree.show()

	def showTree(self, rootItem, c = None, d = None):
		self.treeModel.rootItem = rootItem
		self.sharedTree.setModel(self.treeModel)
		#self.sharedTree.reset()
		self.sharedTree.setToolTip(self.sharedTree.toolTip() + \
									'Shared Source :\n' + \
									str(d) + ' Byte(s)\nin ' + str(c) + ' file(s).')

	def itemSharedSourceQuired(self, item):
		key = str(item.data(QtCore.Qt.AccessibleTextRole).toList()[0].toString())
		#print unicode(item.text()) , ' dClicked :', self.Obj.USERS[key]
		serverState = self.Obj.USERS[key][4]
		pathExist = InCache(serverState)
		self.sharedTree.setToolTip(item.toolTip())
		if pathExist[0] :
			#print 'cached'
			self.showSharedSources(pathExist[1])
			return None
		""" run the getting new structure in QThread """
		if 'clientThread' in dir(self) :
			self.disconnect(self.clientThread, QtCore.SIGNAL('threadRunning'), self.showSharedSources)
			self.clientThread = None
		if self.Obj.USERS[key][3] == 'Yes' :
			self.currentTreeEncode = True
		else :
			self.currentTreeEncode = False
		self.clientThread = ToolsThread(\
										xr_client(\
												str(self.Obj.USERS[key][1]), \
												str(self.Obj.USERS[key][2]), \
												self.Obj, \
												self, \
												self.currentTreeEncode), \
										self)

		self.connect(self.clientThread, QtCore.SIGNAL('threadRunning'), self._showSharedSources)
		self.clientThread.start()

	def hide_n_showTree(self):
		if self.sharedTree.isVisible():
			self.sharedTree.hide()
		else:
			self.sharedTree.show()

	def changeViewMode(self, obj):
		if obj is not None :
			self.Obj.Settings.sync()
			currentIdx = obj.currentIdx
			currentChain = obj.parentItemChain
			toolTip = obj.toolTip()
			obj.close()
			#unlink()
			del obj; obj = None
			viewMode = self.Obj.Settings.value('ViewMode', 'TreeMode').toString()
			self.sharedTree = TreeBox(self.treeModel, self, viewMode, \
										  currentChain = currentChain, \
										  currentIdx = currentIdx)
			self.sharedTree.setToolTip(toolTip)
			self.sharedTree.show()

	def restartServer(self):
		self.sentOfflinePost()
		#print Path.multiPath(Path.tempStruct, 'server', 'sharedSource_' + self.serverState), ' close'
		if InitConfigValue(self.Obj.Settings, 'UseCache', 'True') == 'True' : self.Obj.saveCache()
		if InitConfigValue(self.Obj.Settings, 'SaveLastStructure', 'True') == 'True' :
			#print True
			if os.path.exists(Path.multiPath(Path.tempStruct, 'server', 'sharedSource_' + self.Obj.serverState)) :
				#print 'Exist'
				shutil.move(Path.multiPath(Path.tempStruct, 'server', 'sharedSource_' + self.Obj.serverState), \
							Path.config('lastSharedSource'))
				with open(Path.config('lastServerState'), 'wb') as f :
					f.write(self.Obj.serverState)
			else :
				#print 'not Exist'
				pass
		if 'serverThread' in dir(self.Obj) :
			self.Obj.serverThread._terminate('reStart')
			#self.Obj.serverThread.exit()
		else : self.preStartServer()
 
	@QtCore.pyqtSlot(str, name = 'preStartServer')
	def preStartServer(self, str_):
		if str_ == 'reStart' :
			print 'serverDown signal received'
		else :
			print 'alien signal'
			return None
		self.Obj.initServeR.emit(self.treeModel, '', 'reStart')

	def sentOfflinePost(self):
		if self.Obj.Settings.value('BroadcastDetect', True).toBool() :
			key = str(self.Obj.server_addr + ':' + str(self.Obj.server_port))
			if key in self.Obj.USERS :
				#print 'key :', key, ' in USERS'
				data = QtCore.QString('0' + '<||>' + \
									InitConfigValue(self.Obj.Settings, 'ServerName', \
											os.getenv('USER', '') + ' LightMight Server') + '<||>' + \
									self.Obj.USERS[key][1] + '<||>' + \
									self.Obj.USERS[key][2] + '<||>' + \
									'' + '<||>' + \
									'' + '<||>' + \
									'*infoShare*')
				Sender(data)
