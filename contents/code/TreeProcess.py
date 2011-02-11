# -*- coding: utf-8 -*-

from TreeItem import TreeItem
from PyQt4 import QtCore
import os.path

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

	def getCheckedItemList(self, obj, prefix = '', tab = '	'):
		Result = []
		i = 0
		while i < obj.childCount() :
		#for i in xrange(obj.childCount()):
			item = obj.child(i)
			str_ = item.data(1)
			name_ = item.data(0)
			#print tab, name_, str_, 'chkSt : ', item.checkState
			if item.checkState == QtCore.Qt.Checked :
				Result += [os.path.join(prefix, name_)]
			elif str_ == 'dir' :
				_result = self.getCheckedItemList(item, os.path.join(prefix, name_), tab = tab + '	')
				if _result != [] :
					Result += _result
			i += 1
		return Result

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
