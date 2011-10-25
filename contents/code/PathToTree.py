# -*- coding: utf-8 -*-

import os, os.path, stat
from PyQt4 import QtGui, QtCore
from xml.dom.minidom import Document, parse
from TreeItem import TreeItem
from Functions import Path

class PathToTree(QtCore.QObject):
	def __init__(self, path, rootItem, typePath = 'file', parent = None):
		QtCore.QObject.__init__(self, parent)
		self.SEP = os.sep
		self.path = path
		self.rootItem = rootItem
		self.typePath = typePath
		self.listPrepare()

	def _proceed_dir(self, d, parentItem):
		#d = QtCore.QString(_d).toUtf8().data()
		if (not os.access(d, os.F_OK) or
			not os.access(d, os.R_OK) or
			not os.access(d, os.X_OK)):
			return

		try :
			for entry_dir in os.listdir(d):
				try:
					#print entry_dir, ':', d, QtCore.QString().fromUtf8(d), \
					#						QtCore.QString().fromUtf8(entry_dir)
					#fullpath = os.path.join(d, entry_dir)
					fullpath = QtCore.QString().fromUtf8(d) + self.SEP + \
											QtCore.QString().fromUtf8(entry_dir)
				except UnicodeEncodeError :
					#print 'UnicodeError_file'
					continue
				except UnicodeDecodeError :
					#print 'UnicodeError_file'
					continue
				if os.path.islink(unicode(fullpath)) or \
					not os.path.isdir(unicode(fullpath)): #FIXME: remove this line if you have add and files too
					continue

				entryItem = TreeItem(QtCore.QString().fromUtf8(entry_dir), self.typePath, parentItem)
				if os.path.isdir(unicode(fullpath)):
					self._proceed_dir(fullpath, entryItem)

				parentItem.appendChild(entryItem)
				entryItem.checkState = QtCore.Qt.Checked
		except OSError :
			print 'OSError'
			pass

	def listPrepare(self):
		str_path = self.path
		entryItem = TreeItem(str_path, self.typePath, self.rootItem, first = True)
		entryItem.checkState = QtCore.Qt.Checked
		self.rootItem.appendChild(entryItem)
		self._proceed_dir(str_path, entryItem)

class SharedSourceTree2XMLFile:
	def __init__(self, fileName = 'resultXML', obj = None, parent = None):
		self.fileName = fileName
		self.rootItem = obj
		self.SEP = os.sep
		self.doc = Document()
		self.filePrepare()

	def __del__(self):
		self.fileName = None
		self.rootItem = None
		self.doc = None

	def filePrepare(self):
		self.doc.appendChild(self.treeSharedDataToXML(self.rootItem))

		#print self.doc.toprettyxml()
		f = open(Path.multiPath(Path.tempStruct, 'server', self.fileName), 'wb')
		try :
			#f.write(doc.toprettyxml())   ## без доп параметров неправильно отображает дерево
			self.doc.writexml(f, encoding = 'utf-8')
		except UnicodeError :
			print 'SharedSourceTree2XMLFile.filePrepare : File not saved'
		f.close()
		self.doc.unlink()

	def treeSharedDataToXML(self, obj, prefix = '', tab = '\t'):
		_str = obj.data(1)
		_name = obj.data(0)
		node = self.doc.createElement(_str)
		node.setAttribute('name', QtCore.QString(_name).toUtf8().data())
		node.setAttribute('size', ' dir')
		#print tab, prefix, unicode(_name), 'parent'
		i = 0
		while i < obj.childCount() :
			item = obj.child(i)
			str_ = item.data(1)
			name_ = item.data(0)
			if hasattr(item, 'Root') : name_ = os.path.join(item.Root, name_)
			if item.checkState == QtCore.Qt.Checked :
				#print tab, str_, prefix + unicode(_name), unicode(name_), 'check'
				path_ = os.path.join(unicode(prefix) + unicode(_name), unicode(name_))
				#print QtCore.QString(path_).toUtf8().data(), ' path_'
				if os.path.isfile(path_) :
					#print 'path exist & file'
					elem = self.doc.createElement(str_)
					if hasattr(item, 'Root') : name_ = name_.split(os.path.join(item.Root, ''))[1]
					elem.setAttribute('name', QtCore.QString(name_).toUtf8().data())
					elem.setAttribute('size', str(os.path.getsize(path_)) + ' Byte(s)' + ' file')
				elif os.path.isdir(path_) :
					#print 'path exist & dir'
					if _name == 'Name' :
						prefix_ = ''
					else :
						prefix_ = prefix + _name + self.SEP
					listChild = []
					try:
						listChild = os.listdir(path_)
					except OSError :
						print 'OSerror_1'
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
					if hasattr(item, 'Root') : prefix_ = os.path.join(item.Root, '')
					if len(listChild) > 0 :
						elem = self.treeSharedDataToXML(item, prefix_, tab = tab + '\t')
					else :
						""" not create the node for empty directory """
						i += 1
						continue
				else :
					#print 'path exist & no regular'
					elem = self.doc.createElement(str_)
					elem.setAttribute('name', QtCore.QString(name_).toUtf8().data())
					elem.setAttribute('size', 'no_regular_file')
			elif item.checkState == QtCore.Qt.PartiallyChecked and item.childCount() > 0 :
				""" for parsing PartiallyChecked directory, not for all """
				if _name == 'Name' :
					prefix_ = ''
				else :
					prefix_ = prefix + _name + self.SEP
				#print tab, str_, prefix, name_, 'pref'
				elem = self.treeSharedDataToXML(item, prefix_, tab = tab + '\t')
			else :
				i += 1
				continue
			if hasattr(item, 'Root') : elem.setAttribute('xRoot', item.Root)
			node.appendChild(elem)
			i += 1

		return node
