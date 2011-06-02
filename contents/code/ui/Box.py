# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
from TreeProc import TreeModel
from TreeProcess import TreeProcessing
from BoxLayout import BoxLayout
from ButtonPanel import ButtonPanel
from clnt import xr_client
from ToolsThread import ToolsThread
from simpleJob import SimpleJob

class Box(QtGui.QWidget):
	def __init__(self, Obj_, parent = None):
		QtGui.QWidget.__init__(self, parent)

		self.Obj = Obj_
		self.layout = QtGui.QGridLayout()

		self.userList = QtGui.QListWidget()
		self.userList.setMaximumWidth(250)
		#self.userList.setMinimumSize(100, 75)
		self.userList.sortItems()
		self.userList.setToolTip('Users in Web')
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

		self.buttonPanel = BoxLayout(ButtonPanel, self.Obj)
		self.buttonPanel.setMaximumWidth(65)
		self.layout.addWidget(self.buttonPanel, 0, 2)

		self.jobPanel = SimpleJob(self.Obj)
		self.jobPanel.setMinimumWidth(65)
		self.layout.addWidget(self.jobPanel, 0, 3)

		self.setLayout(self.layout)

	def showSharedSources(self):
		path = self.clientThread.getSharedSourceStructFile()
		print path, ' representation structure file'
		self.treeModel = TreeModel('Name', 'Description', parent = self)
		self.sharedTree.setModel(self.treeModel)
		self.treeProcessing.setupItemData([path], self.treeModel.rootItem)
		#self.sharedTree.reset()

	def itemSharedSourceQuired(self, item):
		""" clean currentServerSharedSourceXMLFile """
		## cleaning or caching
		print unicode(item.text()) , ' dClicked :', self.Obj.avahiBrowser.USERS[unicode(item.text())]
		""" run in QThread """
		self.clientThread = ToolsThread(xr_client(\
							str(self.Obj.avahiBrowser.USERS[unicode(item.text())][1]), \
							str(self.Obj.avahiBrowser.USERS[unicode(item.text())][2]), \
							self.Obj), \
							self)
		self.clientThread.start()
		self.connect( self.clientThread, QtCore.SIGNAL('threadRunning'), self.showSharedSources )
