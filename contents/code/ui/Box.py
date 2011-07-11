# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
from TreeProc import TreeModel
from TreeItem import TreeItem
from TreeProcess import TreeProcessing
from clnt import xr_client
from ToolsThread import ToolsThread
from Wait import SetupTree
from Functions import InCache, pathPrefix, moveFile

class Box(QtGui.QWidget):
	complete = QtCore.pyqtSignal()
	tree = QtCore.pyqtSignal(TreeItem, int, int)
	def __init__(self, Obj_, parent = None):
		QtGui.QWidget.__init__(self, parent)

		self.Obj = Obj_
		self.layout = QtGui.QGridLayout()

		self.userList = QtGui.QListWidget()
		self.userList.setToolTip('Users in Web')
		self.userList.setMaximumWidth(250)
		#self.userList.setMinimumSize(100, 75)
		self.userList.sortItems()
		self.userList.itemDoubleClicked.connect(self.itemSharedSourceQuired)
		self.layout.addWidget(self.userList, 0, 0)

		""" отображение в приложении списка расшаренных ресурсов """
		self.treeModel = TreeModel('Name', 'Description', parent = self)
		self.sharedTree = QtGui.QTreeView()
		self.sharedTree.setRootIsDecorated(True)
		self.treeProcessing = TreeProcessing()
		self.sharedTree.setToolTip('Shared Source')
		self.sharedTree.setExpandsOnDoubleClick(True)
		self.sharedTree.setModel(self.treeModel)
		self.layout.addWidget(self.sharedTree, 0, 1)

		self.buttonLayout = QtGui.QVBoxLayout()
		self.buttonLayout.addStretch(0)

		self.progressBar = QtGui.QProgressBar()
		self.progressBar.setOrientation(QtCore.Qt.Vertical)
		self.progressBar.setAlignment(QtCore.Qt.AlignHCenter)
		self.progressBar.setRange(0, 0)
		self.progressBar.hide()
		self.buttonLayout.addWidget(self.progressBar, 0, QtCore.Qt.AlignHCenter)

		self.upLoadButton = QtGui.QPushButton(QtCore.QString('&Up'))
		self.upLoadButton.setToolTip('UpLoad checked files\nof Shared Source')
		self.upLoadButton.setMaximumWidth(65)
		self.connect(self.upLoadButton, QtCore.SIGNAL('clicked()'), self.upLoad)
		self.buttonLayout.addWidget(self.upLoadButton, 0, QtCore.Qt.AlignHCenter)

		self.refreshButton = QtGui.QPushButton(QtCore.QString('&R'))
		self.refreshButton.setToolTip('Refresh own Avahi service')
		self.refreshButton.setMaximumWidth(65)
		self.connect(self.refreshButton, QtCore.SIGNAL('clicked()'), self.Obj.initAvahiService)
		self.buttonLayout.addWidget(self.refreshButton, 0, QtCore.Qt.AlignHCenter)

		self.layout.addItem(self.buttonLayout, 0, 2)

		self.setLayout(self.layout)

		self.currentTreeEncode = False

		self.complete.connect(self.hideProgressBar)
		self.tree.connect(self.showTree)

	def _showSharedSources(self, str_ = ''):
		if not self.progressBar.isVisible() : self.progressBar.show()
		path = str_
		#print path, ' representation structure file'
		self.treeModel = TreeModel('Name', 'Description', parent = self)
		self.threadSetupTree = SetupTree(self.treeProcessing, [path], self.treeModel.rootItem, self, False, self)
		#self.treeProcessing.setupItemData([path], self.treeModel.rootItem)
		self.threadSetupTree.start()

	def showSharedSources(self):
		self.progressBar.show()
		#print 'not cached'
		path = self.clientThread.getSharedSourceStructFile()
		self._showSharedSources(path)

	def hideProgressBar(self):
		self.progressBar.hide()

	def showTree(self, rootItem, c = None, d = None):
		self.treeModel.rootItem = rootItem
		self.sharedTree.setModel(self.treeModel)
		#self.sharedTree.reset()
		if self.currentTreeEncode :
			encode = 'Yes'
		else :
			encode = 'No'
		self.sharedTree.setToolTip('Shared Source :\n' + \
								str(d) + ' Byte(s)\nin ' + str(c) + ' file(s).' + \
								'\nEncode : ' + encode)

	def itemSharedSourceQuired(self, item):
		## print unicode(item.text()) , ' dClicked :', self.Obj.avahiBrowser.USERS[unicode(item.text())]
		pathExist = InCache(self.Obj.avahiBrowser.USERS[unicode(item.text())][4])
		if pathExist[0] :
			#print 'cached'
			self._showSharedSources(pathExist[1])
			return None
		""" caching currentServerSharedSourceXMLFile """
		path = pathPrefix() + '/dev/shm/LightMight/client/struct_' + self.Obj.currentRemoteServerState
		if not InCache(path)[0] :
			moveFile(path, '/dev/shm/LightMight/cache/' + self.Obj.currentRemoteServerState)
		""" run the getting new structure in QThread """
		if 'clientThread' in dir(self) :
			self.disconnect(self.clientThread, QtCore.SIGNAL('threadRunning'), self.showSharedSources)
			self.clientThread = None
		if self.Obj.avahiBrowser.USERS[unicode(item.text())][3] == 'Yes' :
			self.currentTreeEncode = True
		else :
			self.currentTreeEncode = False
		self.clientThread = ToolsThread(\
										xr_client(\
												str(self.Obj.avahiBrowser.USERS[unicode(item.text())][1]), \
												str(self.Obj.avahiBrowser.USERS[unicode(item.text())][2]), \
												self.Obj, \
												self, \
												self.currentTreeEncode), \
										self)

		self.connect(self.clientThread, QtCore.SIGNAL('threadRunning'), self.showSharedSources)
		self.clientThread.start()

	def upLoad(self):
		QtGui.QApplication.postEvent(self.Obj, QtCore.QEvent(1010))
