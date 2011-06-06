# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
from TreeItem import TreeItem

class TreeModel(QtCore.QAbstractItemModel):
	checkStateChanged = QtCore.pyqtSignal()
	def __init__(self, section1Name, section2Name, parent = None):
		QtCore.QAbstractItemModel.__init__(self, parent)

		self.rootItem = TreeItem(section1Name, section2Name, None, self)
		self.changeMe = True

	def index(self, row, column, prnt = QtCore.QModelIndex()):
		if (not self.hasIndex(row, column, prnt)) :
			return QtCore.QModelIndex()

		parentItem = self.rootItem;
		if prnt.isValid():
			parentItem = prnt.internalPointer()
			#print "=====> %s\t-\t%s" % (parentItem, parentItem.data(0))

		childItem = parentItem.child(row)
		if ( childItem is not None) :
			return self.createIndex(row, column, childItem)

		return QtCore.QModelIndex()

	def parent(self, child = QtCore.QModelIndex()):
		if ( not child.isValid() ) :
			return QtCore.QModelIndex()

		childItem = child.internalPointer()
		#print "--> %s" % type(childItem)
		if childItem is None:
			return QtCore.QModelIndex()

		parentItem = childItem.getParentItem()
		if ( parentItem is None or parentItem == self.rootItem ) :
			return QtCore.QModelIndex()

		return self.createIndex(parentItem.row(), 0, parentItem)

	def rowCount(self, parent = QtCore.QModelIndex()):
		if ( parent.column() > 0 ):
			return 0

		if ( not parent.isValid() ) :
			item = self.rootItem
		else :
			item = parent.internalPointer()

		return item.childCount()

	def columnCount(self, parent = QtCore.QModelIndex()):
		#if parent.isValid() :
		#	return parent.internalPointer().columnCount()
		#else :
		#	return self.rootItem.columnCount()
		return 2

	def data(self, index_, role):
		if (not index_.isValid()) :
			return QtCore.QVariant()

		item = index_.internalPointer()
		if role == QtCore.Qt.CheckStateRole :
				return item.data(index_.column(), role)
		elif (role != QtCore.Qt.DisplayRole) :
			return QtCore.QVariant()
		return item.data(index_.column(), role)

	def headerData(self, section, orientation = QtCore.Qt.Horizontal, role = QtCore.Qt.DisplayRole):
		if (orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole) :
			return self.rootItem.data(section)
		return QtCore.QVariant()

	def processCheckStateOfChildren(self, b):
		qua = b.childCount()
		checkState = b.checkState
		for i in range(0, qua):
			childItem = b.child(i)
			childItem.checkState = checkState
			self.processCheckStateOfChildren(childItem)

	def processCheckStateOfParents(self, b):
		parentItem = b.getParentItem()
		if parentItem is not None :
			qua = parentItem.childCount()
		else :
			return

		quaOfChecked = 0
		quaOfPartChecked = 0
		for i in range(0, qua) :
			if parentItem.child(i).checkState == QtCore.Qt.Checked :
				quaOfChecked += 1
			elif parentItem.child(i).checkState == QtCore.Qt.PartiallyChecked :
				quaOfPartChecked += 1

			if quaOfChecked == qua :
				checkState = QtCore.Qt.Checked
			elif quaOfChecked == 0 and quaOfPartChecked == 0 :
				checkState = QtCore.Qt.Unchecked
			else :
				checkState = QtCore.Qt.PartiallyChecked

			parentItem.checkState = checkState
			self.processCheckStateOfParents(parentItem)

	def setData(self, index_, value, role = QtCore.Qt.DisplayRole):
		if not index_.isValid() :
			return False

		if role == QtCore.Qt.CheckStateRole :
			item = index_.internalPointer()

			if item.checkState == QtCore.Qt.Unchecked :
				item.checkState = QtCore.Qt.Checked
			else :
				item.checkState = QtCore.Qt.Unchecked

			if self.changeMe and item is not None:
				self.changeMe = False
				self.processCheckStateOfChildren(item)
				self.processCheckStateOfParents(item)
				self.changeMe = True

			self.emit(QtCore.SIGNAL("checkStateChanged()"))
			self.emit(QtCore.SIGNAL("dataChanged(const QModelIndex&, const QModelIndex&)"), \
													index_.parent().parent(), index_.parent())
			return True

		return False

	def flags(self, index_):
		if not index_.isValid() :
			return QtCore.Qt.ItemIsEnabled

		return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable
		##/ | QtCore.Qt.ItemIsEditable


