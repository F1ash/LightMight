# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
from TreeProc import TreeModel
from ModePanel import ModePanel
from ViewPanel import ViewPanel

class TreeBox(QtGui.QDialog):
	mode = QtCore.pyqtSignal()
	def __init__(self, treeModel = None, parent = None, viewMode = 'TreeMode', \
										  currentChain = [], \
										  currentIdx = None):
		QtGui.QDialog.__init__(self, parent)

		self.Parent = parent
		self.treeModel = treeModel
		self.viewMode = viewMode
		self.parentItemChain = currentChain
		self.currentIdx = currentIdx
		self.layout = QtGui.QGridLayout()
		self.layout.setSpacing(0)
		self.layout.setAlignment(QtCore.Qt.AlignLeft)

		""" отображение в приложении списка расшаренных ресурсов """
		self.sharedTree = QtGui.QTreeView()

		if viewMode != 'TreeMode' :
			self.upPanel = QtGui.QLabel()
			self.layout.addWidget(self.upPanel, 0, 0)
			
			self.parentPath = QtGui.QPushButton()
			self.parentPath.setToolTip('Back to ..')
			self.parentPath.setStyleSheet('QPushButton { background: rgba(190,190,255,64);} ')
			self.parentPath.setFlat(True)
			self.parentPath.clicked.connect(self.backToParent)
			self.layout.addWidget(self.parentPath, 0, 0)

			if viewMode == 'DetailMode' :
				self.sharedTree.setRootIsDecorated(False)
			else :
				self.sharedTree = QtGui.QListView()
				self.sharedTree.setViewMode(QtGui.QListView.IconMode)

			self.sharedTree.doubleClicked.connect(self.itemDoubleClick)
			self.viewPanel = ViewPanel(self.sharedTree, self)
			self.layout.addWidget(self.viewPanel, 1, 0)
		else :
			self.sharedTree.setRootIsDecorated(True)
			self.sharedTree.setExpandsOnDoubleClick(True)
			self.sharedTree.setAnimated(True)
			self.layout.addWidget(self.sharedTree, 1, 0)

		self.sharedTree.setToolTip('Shared Source')
		self.sharedTree.setModel(treeModel)

		self.buttonLayout = QtGui.QVBoxLayout()
		self.buttonLayout.addStretch(0)

		self.modePanel = ModePanel(viewMode, self)
		self.buttonLayout.addWidget(self.modePanel, 0, QtCore.Qt.AlignHCenter)

		self.upLoadButton = QtGui.QPushButton(QtGui.QIcon('../icons/download.png'), '')
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
			self.itemDoubleClick(self.currentIdx, False)

	def setModel(self, obj = None):
		self.sharedTree.setModel(obj)

	def upLoad(self):
		self.Parent.Obj.uploadSignal.emit(self.toolTip())

	@QtCore.pyqtSlot(QtCore.QModelIndex, name = 'itemDoubleClick')
	def itemDoubleClick(self, index, key = True):
		treeModel = TreeModel('Name', 'Description', parent = self)
		if 'internalPointer' in dir(index) and index.internalPointer() is None :
			treeModel.rootItem = self.treeModel.rootItem
		elif 'internalPointer' in dir(index) and bool(index.internalPointer().childCount()) :
			if self.viewMode == 'IconMode' :
				treeModel.rootItem = index.internalPointer()
			else :
				[treeModel.rootItem.appendChild(item) for item in index.internalPointer().childItems]
		else : return
		self.sharedTree.setModel(treeModel)
		#self.sharedTree.reset()
		if index.internalPointer() is None :
				self.upPanel.setText('..')
		else :
			str_ = index.internalPointer().data(0)
			if str_ == 'Name' : str_ = ''
			self.upPanel.setText('../' + str_)
		if key :
			self.parentItemChain.append(self.treeModel.parent(index))
		self.currentIdx = index
		#print self.parentItemChain

	def backToParent(self):
		#print self.parentItemChain
		if len(self.parentItemChain) < 1 :
			last = self.currentIdx
		else :
			last = self.parentItemChain.pop(len(self.parentItemChain) - 1)
		#print self.parentItemChain, '===' 
		self.itemDoubleClick(last, False)

	def changeViewMode(self):
		self.Parent.data.emit(self)
