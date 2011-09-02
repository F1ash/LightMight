# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore

class TreeItem(QtCore.QObject):
	def __init__(self, name_ = '_not_define_', size_ = '_not_define_', parentItem = None, parent = None):
		QtCore.QObject.__init__(self, parent)
		self.parentItem = parentItem
		self.fileNameItemData = name_
		self.fileSizeItemData = size_
		self.childItems = []
		self.checkState = QtCore.Qt.Unchecked
		self.fileIcon = QtGui.QIcon('../icons/document.png')
		self.dirIcon = QtGui.QIcon('../icons/folder.png')

	def child(self, row):
		if row <= len(self.childItems):
			return self.childItems[row]
		return 0

	def childCount(self):
		return len(self.childItems)

	def columnCount(self):
		return len(self.itemData)

	def data(self, column, role = QtCore.Qt.DisplayRole):
		if role == QtCore.Qt.CheckStateRole and column == 0 :
			return self.checkState
		#elif role != QtCore.Qt.CheckStateRole and role != QtCore.Qt.DecorationRole and column >= 0 :
		elif role == QtCore.Qt.DisplayRole and column >= 0 :
			if column == 0 :
				#return self.itemData[column]
				return self.fileNameItemData
			elif column == 1 :
				return self.fileSizeItemData
		elif role == QtCore.Qt.DecorationRole and column == 0 :
			if self.fileSizeItemData not in {'dir', ' dir'} :
				return self.fileIcon
			else :
				return self.dirIcon

	def childIndex(self, child_link = None):
		if child_link in self.childItems and child_link is not None:
			return self.childItems.index(child_link)

	def row(self):
		if (self.parentItem is not None):
			return self.parentItem.childIndex(self)
		return 0

	def getParentItem(self):
		if 'parentItem' in dir(self) :
			return self.parentItem
		else :
			return None

	def appendChild(self, item):
		if item is not None:
			self.childItems.append(item)

	def removeChild(self, item):
		if item is not None:
			self.childItems.remove(item.internalPointer())

