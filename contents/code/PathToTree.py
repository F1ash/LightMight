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

	def listPrepare(self):
		str_path = unicode(self.path.toUtf8())
		entryItem = TreeItem(str_path, self.typePath, self.rootItem)
		self.rootItem.appendChild(entryItem)
		self._proceed_dir(str_path, entryItem)


	"""
	ORIGINAL UGLY CODE
	def currentList(self, path, dirList):
		Result = ('','','')
		i = 0
		while i < len(dirList) :
			root, dirs, files = dirList[i]
			if path == root :
				Result = (root, dirs, files)
				break
			i += 1
		return Result

	def makenode(self, path, str_, doc = None, dirList = []):
		node = doc.createElement(str_)
		node.setAttribute('name', path)
		root, dirs, files = self.currentList(path, dirList)
		i = 0
		#for dir_ in dirs :
		while i < len(dirs) :
			dir_ = dirs[i]
			try :
				_dir = dir_.encode('utf-8')
				fullname = os.path.join(root, _dir)
				if not stat.S_ISLNK(os.lstat(fullname).st_mode) and os.access(fullname, os.F_OK) and \
						os.access(fullname, os.R_OK) and os.access(fullname, os.X_OK) :
					elem = self.makenode(fullname, 'dir', doc, dirList)
					node.appendChild(elem)
			except UnicodeEncodeError :
				#print 'UnicodeError_dir'
				pass
			except UnicodeDecodeError :
				#print 'UnicodeError_dir'
				pass
			finally :
				pass
			i += 1
		j = 0
		#for file_ in files :
		while j < len(files) :
			file_ = files[j]
			try :
				#_file = unicode(file_, 'utf-8')
				_file = file_.encode('utf-8')
				fullname = os.path.join(root, str(_file))
				if not stat.S_ISLNK(os.lstat(fullname).st_mode) and os.access(fullname, os.F_OK) and \
																			os.access(fullname, os.R_OK) :
					elem = doc.createElement('file')
					elem.setAttribute('name', str(_file))
					elem.setAttribute('size', str(os.path.getsize(fullname)) + ' Byte(s)')
					node.appendChild(elem)
			except UnicodeEncodeError :
				#print 'UnicodeError_file'
				pass
			except UnicodeDecodeError :
				#print 'UnicodeError_file'
				pass
			finally :
				pass
			j += 1
		return node

	def listPrepare(self):
		dirList = []
		for root, dirs, files in os.walk(str(self.path), followlinks = False):
			dirList += [(root, dirs, files)]
		if type(dirList) == list :
			dirList += [(str(self.path),[],[])]
			# print dirList

		print 'Список составлен'
		path_ = dirList[0][0]
		if os.access(path_, os.F_OK) and os.access(path_, os.R_OK) and os.access(path_, os.X_OK) :
			## and os.access(path_, os.W_OK) ) :
			str_ = 'dir'
			self.doc.appendChild( self.makenode(str(path_), str_, self.doc, dirList) )
		elif not stat.S_ISLNK(os.lstat(path_).st_mode) and os.access(path_, os.F_OK) \
														and os.access(path_, os.R_OK) :
			str_ = 'file'
			self.doc.appendChild( self.makenode(str(path_), str_, self.doc, dirList) )
		print 'Создание node завершено'
		del dirList[:]
		#dirList = None
		self.setupTreeData(self.doc.childNodes, self.rootItem)

	def setupTreeData(self, listNodes, parent_obj, tab = '	'):
		#for i in xrange(listNodes.length):
		i = 0
		while i < listNodes.length :
			node = listNodes.item(i)
			if node is None :
				i += 1
				continue

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
				self.setupTreeData(node.childNodes, _newobj, tab + '\t')
			i += 1

	def __del__(self):
		self.doc.unlink()
		self.doc = None
	"""

class PathListToXMLFile:
	def __init__(self, pathList = '', fileName = 'resulXML', parent = None):
		self.pathList = pathList
		self.fileName = fileName
		self.doc = Document()
		self.listPrepare(pathList)

	def _proceed_dir(self, path_, doc):
		path = str(path_)
		if not stat.S_ISLNK(os.lstat(path).st_mode) and os.path.isfile(path) and os.access(path, os.F_OK) \
																			and os.access(path, os.R_OK) :
			node = doc.createElement('file')
			node.setAttribute('name', path)
			node.setAttribute('size', str(os.path.getsize(path)) + ' Byte(s)')
			return node
		elif not stat.S_ISLNK(os.lstat(path).st_mode) and os.path.isdir(path) and os.access(path, os.F_OK) and \
									os.access(path, os.R_OK) and os.access(path, os.X_OK) :
			node = doc.createElement('dir')
			node.setAttribute('name', path)
			node.setAttribute('size', '- - -')

			for path_ in os.listdir(path) :
				_path = os.path.join(path, path_)
				elem = self._proceed_dir(_path, doc)
				node.appendChild(elem)
			return node
		else :
			node = doc.createElement('None')
			node.setAttribute('name', path)
			node.setAttribute('size', 'None')
			return node

	def listPrepare(self, path):
		self.doc.appendChild(self._proceed_dir(path, self.doc))

		# print doc.toprettyxml()
		f = open(self.fileName, 'wb')
		try :
			#f.write(doc.toprettyxml())   ## без доп параметров неправильно отображает дерево
			self.doc.writexml(f, encoding = 'utf-8')
		except UnicodeError :
			print 'File not saved'
			f.close()
			self.doc.unlink()
			return None
		f.close()
		self.doc.unlink()
