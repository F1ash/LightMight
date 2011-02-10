# -*- coding: utf-8 -*-

import os, os.path, stat, gc
from xml.dom.minidom import Document, parse

NodeType = {0:'ELEMENT_NODE', 1:'ATTRIBUTE_NODE', 2:'TEXT_NODE', 3:'CDATA_SECTION_NODE', 4:'ENTITY_NODE', \
 5:'PROCESSING_INSTRUCTION_NODE', 6:'COMMENT_NODE', 7:'DOCUMENT_NODE', 8:'DOCUMENT_TYPE_NODE', 9:'NOTATION_NODE'}

class Parser:
	def __init__(self, parent = None):
		pass

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

	def parseFile(self, listNodes, tab = '	'):
		for i in xrange(listNodes.length):
			node = listNodes.item(i)
			name_ = node.localName
			if name_ == 'dir' :
				lenAttr = node.attributes.length
				print tab, name_, node.attributes.item(0).value  #, NodeType[node.nodeType]
				self.parseFile(node.childNodes, tab + '	')
			elif name_ == 'file' :
				lenAttr = node.attributes.length
				print tab, name_, node.attributes.item(0).value  #, NodeType[node.nodeType]

	def listPrepare(self, _path):
		doc = Document()
		dirList = []
		# print [str(_path)]
		for path in [str(_path)] :
			for root, dirs, files in os.walk(str(path), followlinks = False):
				dirList += [(root, dirs, files)]
			if dirList == [] :
				dirList += [(str(path),[],[])]
				# print dirList

		print 'Список составлен'
		path_ = dirList[0][0]
		if os.access(path_, os.F_OK) and os.access(path_, os.R_OK) and os.access(path_, os.X_OK) :
			## and os.access(path_, os.W_OK) ) :
			str_ = 'dir'
			doc.appendChild( self.makenode(str(path_), str_, doc, dirList) )
		elif not stat.S_ISLNK(os.lstat(path_).st_mode) and os.access(path_, os.F_OK) \
														and os.access(path_, os.R_OK) :
			str_ = 'file'
			doc.appendChild( self.makenode(str(path_), str_, doc, dirList) )
		print 'Создание node завершено'
		del dirList[:]
		dirList = None
		return  doc

	def getResultFile(self, resultFileName, prefix = '/dev/shm/LightMight/cache/', doc = None):
		# print doc.toprettyxml()
		fileName = prefix + resultFileName
		f = open(fileName, 'wb')
		try :
			#f.write(doc.toprettyxml())   ## без доп параметров неправильно отображает дерево
			doc.writexml(f, encoding = 'utf-8')
		except UnicodeError :
			print 'File not saved'
			f.close()
			doc.unlink()
			doc = None
			gc.collect()
			return None
		f.close()
		doc.unlink()
		doc = None
		print gc.collect(), ' gc.collect()'
		print gc.get_referrers(), ' gc.get_referrers()'
		print gc.garbage, ' gc.garbage'

		if os.path.getsize(fileName) > 22 :
			#datasource = open(fileName)
			#dom2 = parse(datasource)   # parse an open file
			#parseFile(dom2.childNodes)
			#datasource.close()
			return fileName
		else :
			os.remove(fileName)
			print 'File was empty and removed'
			return None

def main(path, resultFileName, prefix):
	doc = Parser().listPrepare(path)
	return Parser().getResultFile(resultFileName, prefix, doc)

if __name__ == "__main__" :
	# Example action

	print main('/tmp', 'result', '/tmp/')
