# -*- coding: utf-8 -*-

import os, os.path, stat
from PyQt4 import QtGui, QtCore
from xml.dom.minidom import Document, parse
from TreeItem import TreeItem

class PathToTree(QtCore.QObject):
	def __init__(self, path, rootItem, typePath = 'file', parent = None):
		QtCore.QObject.__init__(self, parent)
		self.path = path
		self.rootItem = rootItem
		self.typePath = typePath
		self.listPrepare()

	def _proceed_dir(self, d, parentItem):
		if (not os.access(d, os.F_OK) or
			not os.access(d, os.R_OK) or
			not os.access(d, os.X_OK)):
			return

		try :
			for entry_dir in os.listdir(d):
				try:
					fullpath = os.path.join(d, entry_dir)
				except UnicodeEncodeError :
					#print 'UnicodeError_file'
					continue
				except UnicodeDecodeError :
					#print 'UnicodeError_file'
					continue
				if os.path.islink(fullpath) or \
					not os.path.isdir(fullpath): #FIXME: remove this line if you have add and files too
					continue

				entryItem = TreeItem(entry_dir, self.typePath, parentItem)
				if os.path.isdir(fullpath):
					self._proceed_dir(fullpath, entryItem)

				parentItem.appendChild(entryItem)
		except OSError :
			#print 'OSError'
			pass

	def listPrepare(self):
		str_path = unicode(self.path.toUtf8())		# *.toUtf8 -- Qt method; need useing standart Python method here
		entryItem = TreeItem(str_path, self.typePath, self.rootItem)
		self.rootItem.appendChild(entryItem)
		self._proceed_dir(str_path, entryItem)


class SharedSourceTree2XMLFile:
	def __init__(self, fileName = 'resultXML', obj = None, parent = None):
		self.fileName = fileName
		self.rootItem = obj
		self.doc = Document()
		self.filePrepare()

	def __del__(self):
		self.fileName = None
		self.rootItem = None
		self.doc = None

	def filePrepare(self):
		self.doc.appendChild(self.treeSharedDataToXML(self.rootItem))

		#print self.doc.toprettyxml()
		f = open('/dev/shm/LightMight/server/' + self.fileName, 'wb')
		try :
			#f.write(doc.toprettyxml())   ## без доп параметров неправильно отображает дерево
			self.doc.writexml(f, encoding = 'utf-8')
		except UnicodeError :
			print 'File not saved'
		f.close()
		self.doc.unlink()

	def treeSharedDataToXML(self, obj, prefix = '', tab = '\t'):
		_str = obj.data(1)
		_name = obj.data(0)
		#print tab, prefix, _name, 'parent'
		node = self.doc.createElement(_str)
		node.setAttribute('name', _name)
		node.setAttribute('size', ' dir')
		i = 0
		while i < obj.childCount() :
			item = obj.child(i)
			str_ = item.data(1)
			name_ = item.data(0)
			if item.checkState == QtCore.Qt.Checked :
				#print tab, str_, prefix + _name, name_, 'check'
				path_ = os.path.join(prefix + _name, name_)
				#print path_, ' path_'
				if os.path.isfile(path_) :
					elem = self.doc.createElement(str_)
					elem.setAttribute('name', name_)
					elem.setAttribute('size', str(os.path.getsize(path_)) + ' Byte(s)' + ' file')
					#node.appendChild(elem)
				elif os.path.isdir(path_) :
					if _name == 'Name' :
						prefix_ = ''
					else :
						prefix_ = prefix + _name + '/'
					try:
						listChild = os.listdir(path_)
					except OSError :
						# print 'OSerror'
						pass
					#print listChild, 'listChild'
					for _path in listChild :
						if not os.path.isdir(os.path.join(path_,_path)) :
							""" во избежание дублирования только для не_каталогов,
								потому что каталоги все и так представлены в дереве
							"""
							str__ = 'file'
							new_item = TreeItem(_path, str__, item)
							new_item.checkState = QtCore.Qt.Checked
							item.appendChild(new_item)
					if len(listChild) > 0 :
						elem = self.treeSharedDataToXML(item, prefix_, tab = tab + '	')
				else :
					elem = self.doc.createElement(str_)
					elem.setAttribute('name', name_)
					elem.setAttribute('size', 'no_regular_file')
			elif item.checkState == QtCore.Qt.PartiallyChecked and item.childCount() > 0 :
				""" for parsing PartiallyChecked directory, not for all """
				if _name == 'Name' :
					prefix_ = ''
				else :
					prefix_ = prefix + _name + '/'
				#print tab, str_, prefix, name_, 'pref'
				elem = self.treeSharedDataToXML(item, prefix_, tab = tab + '	')
			else :
				i += 1
				continue
			node.appendChild(elem)
			i += 1

		return node
