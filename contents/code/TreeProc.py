# -*- coding: utf-8 -*-

import os, sys, os.path, gc, xml.parsers.expat
from xml.dom.minidom import Document, parse
from PyQt4 import QtGui, QtCore

class TreeItem(QtCore.QObject):
	def __init__(self, name_ = '_not_define_', size_ = '_not_define_', parentItem = None, parent = None):
		QtCore.QObject.__init__(self, parent)
		self.parentItem = parentItem
		self.fileNameItemData = name_
		self.fileSizeItemData = size_
		self.childItems = []
		self.checkState = QtCore.Qt.Unchecked

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

class TreeModel(QtCore.QAbstractItemModel):
	checkStateChanged = QtCore.pyqtSignal()
	def __init__(self, sectuion1Name, section2Name, parent = None):
		QtCore.QAbstractItemModel.__init__(self, parent)

		self.rootItem = TreeItem(sectuion1Name, section2Name, None, self)
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
																	index_.parent(), index_)
			return True

		return False

	def flags(self, index_):
		if not index_.isValid() :
			return QtCore.Qt.ItemIsEnabled

		return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable
		##/ | QtCore.Qt.ItemIsEditable

class TreeProcessing:
	def __init__(self, parent = None):
		pass

	def setupItemData(self, pathList, rootItem):
		print 'Создание отображения...'
		for path in pathList :
			datasource = open(path, 'rb')

			try :
				dom2 = parse(datasource, bufsize = 32768)
				print 'dom2 открыт'   # parse an open file
				self.parseFile_(dom2.childNodes, rootItem)
				print 'парсинг завершён'   # parse
				dom2.unlink()
				dom2 = None
				print 'dom2 -- deleted'
			except xml.parsers.expat.ExpatError , x:
				#возникает при неправильной кодировке имени файла (временно устранено)
				print x, '\nОшибка в пути к файлу.'
				showHelp = ListingText("MSG: Наличие некорректного имени каталога\файла.\nПриложение будет завершено.", main)
				showHelp.exec_()
				print "App exit."
				app.exit(0)
			finally :
				datasource.close()

		print 'Создание отображения завершено.'
		#self.debugPrintObj(rootItem)

	def parseFile_(self, listNodes, parent_obj, tab = '	'):
		#for i in xrange(listNodes.length):
		i = 0
		while i < listNodes.length :
			node = listNodes.item(i)
			if node is not None :
				name_ = node.localName

				if node.attributes.length >= 2 :
				#	print tab, 'name :', name_, \
				#			'attr :', node.attributes.item(0).value, node.attributes.item(1).value
					#_ddata = [node.attributes.item(0).value, node.attributes.item(1).value]  ##name_ + ' , ' +
					fileName = node.attributes.item(0).value
					fileSize = node.attributes.item(1).value
				else :
					#_ddata = [node.attributes.item(0).value, name_] ## временно для заполнения дерева в клиенте
					fileName = node.attributes.item(0).value
					fileSize = name_
				_newobj = TreeItem(fileName, fileSize, parent_obj, parent_obj)
				parent_obj.appendChild(_newobj)
				if name_ == 'dir':
					self.parseFile_(node.childNodes, _newobj, tab + '\t')
			i += 1

	def treeDataToXML(self, obj, tab = '	'):
		global FileNameList
		_str = obj.data(1)
		_name = obj.data(0)
		node = doc.createElement(_str)
		node.setAttribute('name', _name)
		i = 0
		while i < obj.childCount() :
		#for i in xrange(obj.childCount()):
			item = obj.child(i)
			str_ = item.data(1)
			name_ = item.data(0)
			elem = doc.createElement(str_)
			elem.setAttribute('name', name_)
			# print tab, name_, str_
			if item.childCount() > 0 :
				elem = self.treeDataToXML(item, tab = tab + '	')
				#print tab, 'dir'
			elif str_ == 'file' :
				#print tab, 'file'
				if _name == 'Name' :
					_prefix = ''
				else :
					_prefix = _name + '/'
				FileNameList += [ _prefix + name_ ]
			node.appendChild(elem)
		i += 1

		return node

	def getDataMask(self, obj, f, tab = '	'):
		i = 0
		while i < obj.childCount() :
		#for i in xrange(obj.childCount()):
			item = obj.child(i)
			str_ = item.data(1)
			name_ = item.data(0)
			# print tab, name_, str_, 'chkSt : ', obj.checkState
			if str_ == 'file' :
				if item.checkState == QtCore.Qt.Checked :
					#f.write(name_ + ' 1\n')
					f.write('1')
				else :
					#f.write(name_ + ' 0\n')
					f.write('0')
			elif str_ == 'dir' :
				self.getDataMask(item, f, tab = tab + '	')
		i += 1

	def setDataMask(self, obj, f, tab = '	'):
		i = 0
		while i < obj.childCount() :
		#for i in xrange(obj.childCount()):
			item = obj.child(i)
			str_ = item.data(1)
			name_ = item.data(0)
			# print tab, name_, str_, 'chkSt : ', obj.checkState
			if str_ == 'file' :
				if f.read(1) :
					item.checkState = QtCore.Qt.Checked
			elif str_ == 'dir' :
				self.setDataMask(item, f, tab = tab + '	')
		i += 1

	def dataMaskToFileNameList(self, obj, f, tab = '	'):
		global FileNameList
		global FileNameList2UpLoad
		i = 0
		fileSize = os.path.getsize(f.name)
		while i < fileSize :
			if f.read(1) == '1' :
				print FileNameList[i], ' selected'
				FileNameList2UpLoad += [FileNameList[i]]
			i += 1

	def debugPrintObj(self, some_obj, tab = '	'):
		return
		print "obj->%s", tab, some_obj.data(0)
		for child in some_obj.childItems:
			self.debugPrintObj(child, tab + '	')
