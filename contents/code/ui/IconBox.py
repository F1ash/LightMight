# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
from TreeProc import TreeModel
from ModePanel import ModePanel

class IconBox(QtGui.QDialog):
	mode = QtCore.pyqtSignal(QtCore.QString)
	def __init__(self, treeModel = None, parent = None, \
										  currentChain = [], \
										  currentIdx = None):
		QtGui.QDialog.__init__(self, parent)

		self.Parent = parent
		self.treeModel = treeModel
		self.parentItemChain = currentChain
		self.currentIdx = currentIdx
		self.layout = QtGui.QGridLayout()
		self.layout.setSpacing(0)
		self.layout.setAlignment(QtCore.Qt.AlignLeft)

		self.parentLabel = QtGui.QLabel()
		self.parentLabel.setText('..')
		self.parentPath = QtGui.QPushButton()
		#self.parentPath = QtGui.QLineEdit()
		self.parentPath.setIcon(QtGui.QIcon('../icons/up.png'))
		self.parentPath.setFlat(True)
		self.parentPath.setStyleSheet('QPushButton { background: rgba(255,255,255,64);} ')
		#self.parentPath.setReadOnly(False)
		self.parentPath.clicked.connect(self.backToParent)
		self.layout.addWidget(self.parentLabel, 0, 0)
		self.layout.addWidget(self.parentPath, 0, 0)  ##, QtCore.Qt.AlignLeft)

		""" отображение в приложении списка расшаренных ресурсов """
		self.sharedTree = QtGui.QListView()
		self.sharedTree.setToolTip('Shared Source')
		self.sharedTree.setViewMode(QtGui.QListView.IconMode) # ListMode
		#self.sharedTree.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
		self.sharedTree.setModel(self.treeModel)
		self.layout.addWidget(self.sharedTree, 1, 0)

		self.buttonLayout = QtGui.QVBoxLayout()
		self.buttonLayout.addStretch(0)

		self.modePanel = ModePanel('IconMode', self)
		self.buttonLayout.addWidget(self.modePanel, 0, QtCore.Qt.AlignHCenter)

		self.upLoadButton = QtGui.QPushButton(QtCore.QString('&Up'))
		self.upLoadButton.setToolTip('UpLoad checked files\nof Shared Source')
		self.upLoadButton.setMaximumWidth(65)
		self.connect(self.upLoadButton, QtCore.SIGNAL('clicked()'), self.upLoad)
		self.buttonLayout.addWidget(self.upLoadButton, 1, QtCore.Qt.AlignHCenter)

		self.layout.addItem(self.buttonLayout, 1, 1)
		self.sharedTree.doubleClicked.connect(self.itemDoubleClick)

		self.setGeometry(parent.geometry())
		self.setLayout(self.layout)
		self.mode.connect(self.changeViewMode)

		if self.currentIdx is not None :
			#print 'old state load :: iconsMode'
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
		treeModel = TreeModel('..', '..', parent = self)
		if index.internalPointer() is None :
			treeModel.rootItem = self.treeModel.rootItem
		elif bool(index.internalPointer().childCount()) :
			treeModel.rootItem = index.internalPointer()
		else : return
		self.sharedTree.setModel(treeModel)
		#self.sharedTree.reset()
		if index.internalPointer() is None or index.internalPointer().parentItem is None :
			self.parentLabel.setText('..')
		else :
			self.parentLabel.setText('..' + index.internalPointer().data(0))
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
