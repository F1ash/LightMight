# -*- coding: utf-8 -*-

from xml.dom.minidom import Document, parse
from TreeItem import TreeItem
from PyQt4 import QtCore
import os, os.path, string, xml.parsers.expat, xml.sax._exceptions

class TreeProcessing:
	def __init__(self, parent = None):
		pass

	def setupItemData(self, pathList, rootItem):
		print 'Создание отображения...'
		count = 0; downLoads = 0
		for path in pathList :
			try :
				if not os.path.isfile(path) :
					print '[in TreeProcessing.setupItemData : File not found] :', path, '.'
					continue
				with open(path, 'rb') as datasource :
					dom2 = parse(datasource, bufsize = 65536)
					#print 'dom2 открыт'   # parse an open file
					## *.childNodes[0].childNodes for ignoring rootItem_node
					count, downLoads = self.parseFile_(dom2.childNodes[0].childNodes, rootItem)
					#print 'парсинг завершён'   # parse
					dom2.unlink()
					dom2 = None
					#print 'dom2 -- deleted'
			except xml.parsers.expat.ExpatError , x:
				datasource.close()
				#возникает при неправильной кодировке имени файла (временно устранено)
				print x, '\nОшибка в пути к файлу.'
				showHelp = ListingText("MSG: Наличие некорректного имени каталога\файла.\nПриложение будет завершено.", main)
				showHelp.exec_()
				print "App exit."
				#app.exit(0)
			except xml.sax._exceptions.SAXParseException, err :
				print '[SAXParseException] :', str(err)
				datasource.close()
			except IOError, err :
				print '[in TreeProcessing.setupItemData] IOError:', err
			finally :
				pass

		print 'Создание отображения завершено.'
		#self.debugPrintObj(rootItem)
		return count, downLoads

	def parseFile_(self, listNodes, parent_obj, tab = '	'):
		i = 0; count = 0; downLoads = 0
		while i < listNodes.length :
			node = listNodes.item(i)
			if node is not None :
				name_ = node.localName

				if node.attributes.length >= 2 :
					#print tab, 'name :', name_, \
					#		'attr :', node.attributes.item(0).value, node.attributes.item(1).value
					#_ddata = [node.attributes.item(0).value, node.attributes.item(1).value]  ##name_ + ' , ' +
					fileName = node.attributes['name'].value
					fileSize = node.attributes['size'].value
					if name_ == 'file' :
						count += 1
						_str = string.split(fileSize, ' ')
						if len(_str) > 1 : downLoads += int(_str[0])
				else :
					#_ddata = [node.attributes.item(0).value, name_] ## временно для заполнения дерева в клиенте
					fileName = node.attributes['name'].value
					fileSize = name_
				_newobj = TreeItem(fileName, fileSize, parent_obj)
				if node.attributes.length == 3 : _newobj.Root = node.attributes['xRoot'].value
				parent_obj.appendChild(_newobj)
				if name_ == 'dir':
					_count, _downLoads = self.parseFile_(node.childNodes, _newobj, tab + '\t')
					count += _count
					downLoads += _downLoads
			i += 1
		return count, downLoads

	def getCommonSetOfSharedSource(self, obj, commonSet, pref = '', \
									j = 0, tab = '\t', checkItem = False, \
									f = None, diff = ''):
		downLoadSize = 0
		i = 0
		while i < obj.childCount() :
			item = obj.child(i)
			str_ = item.data(1)
			name_ = item.data(0)
			#print tab, pref + name_
			if hasattr(item, 'Root') :
				_name = os.path.join(item.Root, name_)
				diff = os.path.join(item.Root, '')
			else :
				_name = os.path.join(pref, name_)
			if str_ != ' dir' and str_ != 'no_regular_file' :
				if not checkItem :
					commonSet[j] = _name
					#print commonSet[j]
				if checkItem and item.checkState == QtCore.Qt.Checked :
					size_ = string.split(str_, ' ')[0]
					downLoadSize += int(size_)
					name = _name.split(diff)[1]
					f.write(('1<||>' + name + '<||>' + size_ + '<||>' + str(j) + '\n').encode('UTF-8'))
				j += 1
				i += 1
				continue
			elif str_ == ' dir' :
				j, _downLoadSize = self.getCommonSetOfSharedSource(\
										item, commonSet, os.path.join(_name, ''), \
										j, tab + '\t', checkItem, f, diff)
				downLoadSize += _downLoadSize
			if not checkItem :
				commonSet[j] = _name
				#print commonSet[j]
			if checkItem : f.write('0<||><||><||>\n')
			j += 1
			i += 1
		return j, downLoadSize

	def debugPrintObj(self, some_obj, tab = '\t'):
		return
		print "obj->%s", tab, some_obj.data(0)
		for child in some_obj.childItems:
			self.debugPrintObj(child, tab + '\t')
