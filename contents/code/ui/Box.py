# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtCore
from TreeProc import TreeModel
from TreeProcess import TreeProcessing
from BoxLayout import BoxLayout
from ButtonPanel import ButtonPanel

class Box(QtGui.QWidget):
	def __init__(self, Obj_, job_key = None, parent = None):
		QtGui.QWidget.__init__(self, parent)

		self.Obj = Obj_
		self.layout = QtGui.QGridLayout()

		self.userList = QtGui.QListWidget()
		self.userList.setMaximumWidth(250)
		#self.userList.setMinimumSize(100, 75)
		self.userList.setToolTip('Users in Web')
		self.layout.addWidget(self.userList, 0, 0)

		pathList = []    ##['result1', 'result2', 'result3']
		self.treeModel = TreeModel('Name', 'Description', parent = self)
		self.sharedTree = QtGui.QTreeView()
		#self.sharedTree.setRootIndex(treeModel.index(0, 0))
		self.sharedTree.setRootIsDecorated(True)
		TreeProcessing().setupItemData(pathList, self.treeModel.rootItem)
		self.sharedTree.setToolTip('Shared Source')
		self.sharedTree.setExpandsOnDoubleClick(True)
		self.sharedTree.setModel(self.treeModel)
		self.layout.addWidget(self.sharedTree, 0, 1)

		self.buttunPanel = BoxLayout(ButtonPanel, self.Obj)
		self.buttunPanel.setMaximumWidth(100)
		self.layout.addWidget(self.buttunPanel, 0, 2)

		self.setLayout(self.layout)

