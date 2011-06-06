# -*- coding: utf-8 -*-

from xml.dom.minidom import Document, parse
from TreeItem import TreeItem
from PyQt4 import QtCore
import os, os.path, xml.parsers.expat, string

class TreeProcessing:
	def __init__(self, parent = None):
		pass

	def setupItemData(self, pathList, rootItem):
		print 'Создание отображения...'
		for path in pathList :
			with open(path, 'rb') as datasource :

				try :
					dom2 = parse(datasource, bufsize = 32768)
					print 'dom2 открыт'   # parse an open file
					## *.childNodes[0].childNodes for ignoring rootItem_node
					self.parseFile_(dom2.childNodes[0].childNodes, rootItem)
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
		i = 0
		while i < listNodes.length :
			node = listNodes.item(i)
			if node is not None :
				name_ = node.localName

				if node.attributes.length >= 2 :
					#print tab, 'name :', name_, \
					#		'attr :', node.attributes.item(0).value, node.attributes.item(1).value
					#_ddata = [node.attributes.item(0).value, node.attributes.item(1).value]  ##name_ + ' , ' +
					fileName = node.attributes.item(0).value
					fileSize = node.attributes.item(1).value
				else :
					#_ddata = [node.attributes.item(0).value, name_] ## временно для заполнения дерева в клиенте
					fileName = node.attributes.item(0).value
					fileSize = name_
				_newobj = TreeItem(fileName, fileSize, parent_obj)
				parent_obj.appendChild(_newobj)
				if name_ == 'dir':
					self.parseFile_(node.childNodes, _newobj, tab + '\t')
			i += 1

	def getSharedData(self, obj, f, emitter, jobNumber, downLoadPath, tab = '	', pref = ''):
		i = 0
		while i < obj.childCount() :
			item = obj.child(i)
			str_ = item.data(1)
			name_ = item.data(0)
			# print tab, name_, str_, 'chkSt : ', obj.checkState
			if str_ != ' dir' and str_ != 'no_regular_file' :
				if item.checkState == QtCore.Qt.Checked :
					path = os.path.dirname(pref + name_)
					if not os.path.isdir(downLoadPath + path) :
						os.makedirs(downLoadPath + path)
					""" call downLoad client method """
					f.getSharedData(pref + name_)
					#emitter.nextfile.emit(jobNumber)
					emitter.nextfile.emit(jobNumber, int(string.split(str_, ' ')[0]))
			elif str_ == ' dir' and \
				(item.checkState == QtCore.Qt.PartiallyChecked or item.checkState == QtCore.Qt.Checked) :
				if not os.path.exists(downLoadPath + '/' + pref + name_) :
					os.makedirs(downLoadPath + '/' + pref + name_)
				self.getSharedData(item, f, emitter, jobNumber, downLoadPath, \
									tab = tab + '	', pref = pref + name_ + '/')
			i += 1

	def getCheckedItemDataSumm(self, obj, f, pref = ''):
		downLoadSize = 0
		i = 0
		while i < obj.childCount() :
			item = obj.child(i)
			str_ = item.data(1)
			name_ = item.data(0)
			if item.checkState == QtCore.Qt.Checked and str_ != ' dir' and str_ != 'no_regular_file' :
				size_ = string.split(str_, ' ')[0]
				downLoadSize += int(size_)
				f.write('1<||>' + pref + name_ + '<||>' + size_ + '\n')
				i += 1
				continue
			elif str_ == ' dir' :
				_downLoadSize = self.getCheckedItemDataSumm(item, f, pref + name_ + '/')
				downLoadSize += _downLoadSize
			f.write('0<||>' + pref + name_ + '<||>\n')
			i += 1
		return downLoadSize

	def getCommonSetOfSharedSource(self, obj, commonSet, pref = '', \
									j = 0, tab = '	', checkItem = False, f = None):
		downLoadSize = 0
		i = 0
		while i < obj.childCount() :
			item = obj.child(i)
			str_ = item.data(1)
			name_ = item.data(0)
			#print tab, pref + name_
			if str_ != ' dir' and str_ != 'no_regular_file' :
				if not checkItem :
					commonSet[j] = pref + name_
					#print commonSet
				if checkItem and item.checkState == QtCore.Qt.Checked :
					size_ = string.split(str_, ' ')[0]
					downLoadSize += int(size_)
					f.write('1<||>' + pref + name_ + '<||>' + size_ + '<||>' + str(j) + '\n')
				j += 1
				i += 1
				continue
			elif str_ == ' dir' :
				j, _downLoadSize = self.getCommonSetOfSharedSource(\
										item, commonSet, pref + name_ + '/', \
										j, tab + '	', checkItem, f)
				downLoadSize += _downLoadSize
			if not checkItem :
				commonSet[j] = pref + name_
				#print commonSet
			if checkItem : f.write('0<||><||><||>\n')
			j += 1
			i += 1
		return j, downLoadSize

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
