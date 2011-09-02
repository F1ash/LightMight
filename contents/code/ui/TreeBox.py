# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
from TreeProc import TreeModel
from ModePanel import ModePanel

class TreeBox(QtGui.QDialog):
	mode = QtCore.pyqtSignal(QtCore.QString)
	def __init__(self, treeModel = None, parent = None, viewMode = 'TreeMode', \
										  currentChain = [], \
										  currentIdx = None):
		QtGui.QDialog.__init__(self, parent)

		self.Parent = parent
		self.treeModel = treeModel
		self.parentItemChain = currentChain
		self.currentIdx = currentIdx
		self.layout = QtGui.QGridLayout()

		""" отображение в приложении списка расшаренных ресурсов """
		self.sharedTree = QtGui.QTreeView()

		if viewMode == 'DetailMode' :
			self.parentPath = QtGui.QPushButton()
			#self.parentPath = QtGui.QLineEdit()
			self.parentPath.setText(' >> ')
			#self.parentPath.setReadOnly(False)
			self.parentPath.clicked.connect(self.backToParent)
			self.layout.addWidget(self.parentPath, 0, 0)  ##, QtCore.Qt.AlignJustify)
			
			self.sharedTree.setRootIsDecorated(False)
			self.sharedTree.doubleClicked.connect(self.itemDoubleClick)
		else :
			self.sharedTree.setRootIsDecorated(True)

		self.sharedTree.setToolTip('Shared Source')
		self.sharedTree.setExpandsOnDoubleClick(True)
		self.sharedTree.setAnimated(True)
		self.sharedTree.setModel(treeModel)
		self.layout.addWidget(self.sharedTree, 1, 0)

		self.buttonLayout = QtGui.QVBoxLayout()
		self.buttonLayout.addStretch(0)

		self.modePanel = ModePanel(viewMode, self)
		self.buttonLayout.addWidget(self.modePanel, 0, QtCore.Qt.AlignHCenter)

		self.upLoadButton = QtGui.QPushButton(QtCore.QString('&Up'))
		self.upLoadButton.setToolTip('UpLoad checked files\nof Shared Source')
		self.upLoadButton.setMaximumWidth(65)
		self.connect(self.upLoadButton, QtCore.SIGNAL('clicked()'), self.upLoad)
		self.buttonLayout.addWidget(self.upLoadButton, 1, QtCore.Qt.AlignHCenter)

		self.layout.addItem(self.buttonLayout, 1, 1)

		self.setGeometry(parent.geometry())
		self.setLayout(self.layout)
		self.mode.connect(self.changeViewMode)

		if self.currentIdx is not None and viewMode != 'TreeMode':
			#print 'old state load :: ' + viewMode
			self.itemDoubleClick(self.currentIdx)

	def setModel(self, obj = None):
		self.sharedTree.setModel(obj)

	def upLoad(self):
		self.Parent.Obj.uploadSignal.emit(self.toolTip())

	def itemDoubleClick(self, index):
		'''if (index.internalPointer() is not None) :
			print index.data(QtCore.Qt.DisplayRole), index.model(), \
				index.internalPointer().data(0), index.internalPointer().data(1), \
				index.internalPointer().childCount()
		'''
		treeModel = TreeModel('Name', 'Description', parent = self)
		if index.internalPointer() is None :
			treeModel.rootItem = self.treeModel.rootItem
		elif bool(index.internalPointer().childCount()) :
			[treeModel.rootItem.appendChild(item) for item in index.internalPointer().childItems]
		else : return
		self.sharedTree.setModel(treeModel)
		#self.sharedTree.reset()
		if index.internalPointer() is None or index.internalPointer().parentItem is None :
			self.parentPath.setText(' >> ')
		else :
			self.parentPath.setText(' >> ' + index.internalPointer().data(0))
		self.parentItemChain.append(self.treeModel.parent(index))
		self.currentIdx = index

	def backToParent(self):
		if len(self.parentItemChain) < 1 :
			last = None
		else :
			last = self.parentItemChain.pop(len(self.parentItemChain) - 1)
		if last is not None :
			#print last.internalPointer().data(0)
			#self.parentPath.setText(' >> ' + last.internalPointer().data(0))
			self.itemDoubleClick(last)

	def changeViewMode(self, mode = 'TreeMode'):
		self.Parent.data.emit(self)
