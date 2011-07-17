# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
from TreeProc import TreeModel
from TreeItem import TreeItem
from TreeProcess import TreeProcessing
from clnt import xr_client
from ToolsThread import ToolsThread
from Wait import SetupTree
from Functions import InCache, pathPrefix, moveFile, DelFromCache
from os.path import basename as BaseName

class Box(QtGui.QWidget):
	complete = QtCore.pyqtSignal()
	tree = QtCore.pyqtSignal(TreeItem, int, int)
	def __init__(self, Obj_, parent = None):
		QtGui.QWidget.__init__(self, parent)

		self.Obj = Obj_

		self.treeModel = TreeModel('Name', 'Description', parent = self)
		self.treeProcessing = TreeProcessing()
		self.sharedTree = TreeBox(self.treeModel, self)

		self.layout = QtGui.QGridLayout()
		self.layout.setColumnStretch(0, 0)

		self.userList = QtGui.QListWidget()
		self.userList.setToolTip('Users in Web')
		self.userList.setMaximumWidth(250)
		#self.userList.setMinimumSize(100, 75)
		self.userList.sortItems()
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

		self.treeButton = QtGui.QPushButton(QtCore.QString('&Tree'))
		self.treeButton.setToolTip('Show Tree \nof Shared Source')
		self.treeButton.setMaximumWidth(65)
		self.connect(self.treeButton, QtCore.SIGNAL('clicked()'), self.hide_n_showTree)
		self.buttonLayout.addWidget(self.treeButton, 0, QtCore.Qt.AlignHCenter)

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

	def showSharedSources(self, str_ = ''):
		if not self.progressBar.isVisible() : self.progressBar.show()
		path = str_
		#print path, ' representation structure file'
		self.treeModel = TreeModel('Name', 'Description', parent = self)
		self.threadSetupTree = SetupTree(self.treeProcessing, [path], self.treeModel.rootItem, self, False, self)
		#self.treeProcessing.setupItemData([path], self.treeModel.rootItem)
		self.threadSetupTree.start()

	def _showSharedSources(self):
		self.progressBar.show()
		#print 'not cached'
		path, previousState = self.clientThread.getSharedSourceStructFile()
		""" search USERS key with desired value for set it in "cached" """
		currentKey = ''; Value = BaseName(path)
		for itemValue in self.Obj.avahiBrowser.USERS.iteritems() :
			if itemValue[1][4] == Value :
				self.Obj.avahiBrowser.USERS[itemValue[0]] = (itemValue[1][0], \
															 itemValue[1][1], \
															 itemValue[1][2], \
															 itemValue[1][3], \
															 itemValue[1][4], \
															 True)
				break
		DelFromCache(previousState)
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
		## print unicode(item.text()) , ' dClicked :', self.Obj.avahiBrowser.USERS[unicode(item.text())]
		pathExist = InCache(self.Obj.avahiBrowser.USERS[unicode(item.text())][4])
		self.sharedTree.setToolTip(item.toolTip())
		if pathExist[0] :
			#print 'cached'
			self.showSharedSources(pathExist[1])
			return None
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

		self.connect(self.clientThread, QtCore.SIGNAL('threadRunning'), self._showSharedSources)
		self.clientThread.start()

	def hide_n_showTree(self):
		if self.sharedTree.isVisible():
			self.sharedTree.hide()
		else:
			self.sharedTree.show()

class TreeBox(QtGui.QDialog):
	def __init__(self, treeModel = None, parent = None):
		QtGui.QDialog.__init__(self, parent)

		self.Parent = parent 
		self.layout = QtGui.QGridLayout()

		""" отображение в приложении списка расшаренных ресурсов """
		self.sharedTree = QtGui.QTreeView()
		self.sharedTree.setRootIsDecorated(True)
		self.sharedTree.setToolTip('Shared Source')
		self.sharedTree.setExpandsOnDoubleClick(True)
		self.sharedTree.setModel(treeModel)
		self.layout.addWidget(self.sharedTree, 0, 0)

		self.buttonLayout = QtGui.QVBoxLayout()
		self.buttonLayout.addStretch(0)

		self.upLoadButton = QtGui.QPushButton(QtCore.QString('&Up'))
		self.upLoadButton.setToolTip('UpLoad checked files\nof Shared Source')
		self.upLoadButton.setMaximumWidth(65)
		self.connect(self.upLoadButton, QtCore.SIGNAL('clicked()'), self.upLoad)
		self.buttonLayout.addWidget(self.upLoadButton, 0, QtCore.Qt.AlignHCenter)

		self.layout.addItem(self.buttonLayout, 0, 1)

		self.setGeometry(parent.geometry())
		self.setLayout(self.layout)

	def setModel(self, obj = None):
		self.sharedTree.setModel(obj)

	def upLoad(self):
		self.Parent.Obj.uploadSignal.emit(self.toolTip())
