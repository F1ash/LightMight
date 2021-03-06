# -*- coding: utf-8 -*-

from PyQt4.QtGui import *
from PyQt4.QtCore import *
import os

class ModePanel(QWidget):
	def __init__(self, param, parent = None):
		QWidget.__init__(self, parent)
		self.prnt = parent
		self.SEP = os.sep

		self.layout = QVBoxLayout()
		self.layout.setSpacing(0)

		self.treeIcon = QPushButton(QIcon('..' + self.SEP + 'icons' + self.SEP + 'view-list-tree.png'), '')
		self.treeIcon.setToolTip('Tree Mode')
		if param == 'TreeMode' :  self.treeIcon.setEnabled(False)
		self.treeIcon.clicked.connect(self.setTreeMode)
		self.layout.addWidget(self.treeIcon, 0)

		self.listIcon = QPushButton(QIcon('..' + self.SEP + 'icons' + self.SEP + 'view-list-details.png'), '')
		self.listIcon.setToolTip('Detail Mode')
		if param == 'DetailMode' :  self.listIcon.setEnabled(False)
		self.listIcon.clicked.connect(self.setListMode)
		self.layout.addWidget(self.listIcon, 0)

		self.iconIcon = QPushButton(QIcon('..' + self.SEP + 'icons' + self.SEP + 'view-list-icons.png'), '')
		self.iconIcon.setToolTip('Icons Mode')
		if param == 'IconMode' :  self.iconIcon.setEnabled(False)
		self.iconIcon.clicked.connect(self.setIconMode)
		self.layout.addWidget(self.iconIcon, 0)

		self.setLayout(self.layout)

	def setTreeMode(self):
		#print 'tree'
		self.prnt.Parent.Obj.Settings.setValue('ViewMode', 'TreeMode')
		self.prnt.mode.emit()	##QString('TreeMode'))

	def setListMode(self):
		#print 'list'
		self.prnt.Parent.Obj.Settings.setValue('ViewMode', 'DetailMode')
		self.prnt.mode.emit()	##QString('DetailMode'))

	def setIconMode(self):
		#print 'icons'
		self.prnt.Parent.Obj.Settings.setValue('ViewMode', 'IconMode')
		self.prnt.mode.emit()	##QString('IconMode'))
