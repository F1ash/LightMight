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
from ContactDataEditor import ContactDataEditor
from Functions import InCache, Path, moveFile, DelFromCache, InitConfigValue, avatarInCache
from os.path import basename as BaseName
from mcastSender import _send_mcast as Sender
import os, shutil, os.path, threading

class Box(QtGui.QWidget):
	complete = QtCore.pyqtSignal()
	tree = QtCore.pyqtSignal(TreeItem, int, int)
	data = QtCore.pyqtSignal(TreeBox)
	setAvatar = QtCore.pyqtSignal(QtGui.QListWidgetItem, str)
	cachedData = QtCore.pyqtSignal(str, bool)
	def __init__(self, Obj_, parent = None):
		QtGui.QWidget.__init__(self, parent)

		self.Obj = Obj_
		self.SEP = os.sep

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
		self.userList.customContextMenuRequested.connect(self.itemContextMenuQuired)
		self.layout.addWidget(self.userList, 0, 0)

		self.buttonLayout = QtGui.QVBoxLayout()
		self.buttonLayout.addStretch(0)

		self.progressBar = QtGui.QProgressBar()
		self.progressBar.setOrientation(QtCore.Qt.Vertical)
		self.progressBar.setAlignment(QtCore.Qt.AlignHCenter)
		self.progressBar.setRange(0, 0)
		self.progressBar.hide()
		self.buttonLayout.addWidget(self.progressBar, 0, QtCore.Qt.AlignHCenter)

		self.addContactIcon = QtGui.QIcon('..' + self.SEP + 'icons' + self.SEP + 'contact_new.png')
		self.addContactButton = QtGui.QPushButton(self.addContactIcon, '')
		self.addContactButton.setToolTip('Connect to New Contact')
		self.connect(self.addContactButton, QtCore.SIGNAL('clicked()'), self.addContact)
		self.buttonLayout.addWidget(self.addContactButton, 0, QtCore.Qt.AlignHCenter)

		self.treeIcon = QtGui.QIcon('..' + self.SEP + 'icons' + self.SEP + 'tree.png')
		self.treeButton = QtGui.QPushButton(self.treeIcon, '')
		self.treeButton.setToolTip('Show Tree \nof Shared Source')
		self.connect(self.treeButton, QtCore.SIGNAL('clicked()'), self.hide_n_showTree)
		self.buttonLayout.addWidget(self.treeButton, 0, QtCore.Qt.AlignHCenter)

		self.refreshIcon = QtGui.QIcon('..' + self.SEP + 'icons' + self.SEP + 'restart.png')
		self.refreshButton = QtGui.QPushButton(self.refreshIcon, '')
		self.refreshButton.setToolTip('Restart Server')
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
		#self.threadSetupTree = SetupTree(self.treeProcessing, [path], self.treeModel, self, False, self)
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

	def _showSharedSources(self, path_, error):
		self.cachedData.disconnect(self._showSharedSources)
		path = str(path_)
		if error : cached = False
		else : cached = True
		""" search USERS key with desired value for set it in "cached" """
		Value = BaseName(path)
		for itemValue in self.Obj.USERS.iteritems() :
			try :
				if itemValue[1][4] == Value :
					#print Value, 'state found'
					self.Obj.USERS[itemValue[0]] = (itemValue[1][0], \
													itemValue[1][1], \
													itemValue[1][2], \
													itemValue[1][3], \
													itemValue[1][4], \
													cached)
					self.searchItem(str(itemValue[1][1] + ':' + itemValue[1][2]))
					break
			except RuntimeError , err :
				print '[in _showSharedSources() Box]: ', err
				continue
		if os.path.isfile(path) : self.showSharedSources(path)
		else :
			self.Obj.showMSG('Error at getting data.')
			self.progressBar.hide()
		self.clientThread._terminate()
		self.userList.itemDoubleClicked.connect(self.itemSharedSourceQuired)

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
		#print 'not cached'
		self.userList.itemDoubleClicked.disconnect(self.itemSharedSourceQuired)
		""" run the getting new structure in QThread """
		if 'clientThread' in dir(self) :
			self.clientThread = None
		if self.Obj.USERS[key][3] == 'Yes' :
			encode = True
		else :
			encode = False
		self.clientThread = ToolsThread(\
										xr_client(\
												str(self.Obj.USERS[key][1]), \
												str(self.Obj.USERS[key][2]), \
												self.Obj, \
												self, \
												encode), \
										parent = self)
		self.clientThread.Obj.serverState = self.Obj.USERS[key][4]
		self.clientThread.flag = 'cache_now'
		self.clientThread.start()
		if hasattr(self.clientThread, 'runned') and self.clientThread.runned :
			self.cachedData.connect(self._showSharedSources)
			self.progressBar.show()
		else :
			self.userList.itemDoubleClicked.connect(self.itemSharedSourceQuired)

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
		self.Obj.saveTemporaryData()
		if 'serverThread' in dir(self.Obj) :
			self.Obj.stopServices(True, '', 'reStart')
		else : self.preStartServer('reStart:')

	@QtCore.pyqtSlot(str, name = 'preStartServer')
	def preStartServer(self, str_ = ''):
		print 'serverDown signal received'
		self.Obj.initServeR.emit(self.treeModel, '', str_, True)

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
				#Sender(data)
				s = threading.Thread(target = Sender,  args = (data,))
				s.start()

	def itemContextMenuQuired(self, point):
		item = self.userList.itemAt(point)
		if item is not None :
			#print point, 'clicked', QtCore.QString().fromUtf8(item.text())
			Editor  = ContactDataEditor(item, self)
			Editor.move(point)
			Editor.exec_()

