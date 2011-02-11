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
	
	def __del__(self):
		for c in self.childItems:
			c.__del__()
			self.childItems.remove(c)

	def child(self, row):
		if row <= len(self.childItems):
			return self.childItems[row]
		return None

	def childCount(self):
		return len(self.childItems)

	def columnCount(self):
		return len(self.itemData)

	def data(self, column, role = QtCore.Qt.DisplayRole):
		if role == QtCore.Qt.CheckStateRole and column == 0 :
			return self.checkState
		elif role != QtCore.Qt.CheckStateRole and column >= 0 :
			if column == 0 :
				#return self.itemData[column]
				return self.fileNameItemData
			elif column == 1 :
				return self.fileSizeItemData

	def childIndex(self, child_link = None):
		if child_link in self.childItems and child_link is not None:
			return self.childItems.index(child_link)

	def row(self):
		if (self.parentItem is not None):
			return self.parentItem.childIndex(self)
		return None

	def getParentItem(self):
		return self.parentItem

	def appendChild(self, item):
		if item is not None:
			self.childItems.append(item)

