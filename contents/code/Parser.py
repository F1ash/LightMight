# -*- coding: utf-8 -*-

import os, os.path
from xml.dom.minidom import Document, parse

doc = Document()

NodeType = {0:'ELEMENT_NODE', 1:'ATTRIBUTE_NODE', 2:'TEXT_NODE', 3:'CDATA_SECTION_NODE', 4:'ENTITY_NODE', \
 5:'PROCESSING_INSTRUCTION_NODE', 6:'COMMENT_NODE', 7:'DOCUMENT_NODE', 8:'DOCUMENT_TYPE_NODE', 9:'NOTATION_NODE'}

dirList = []

def currentList(path):
	global dirList
	Result = ('','','')
	for root, dirs, files in dirList :
		if path == root :
			Result = (root, dirs, files)
			break
	return Result

def makenode(path, str_ = 'dir'):
<<<<<<< HEAD
	global doc
=======
>>>>>>> 46bff2157961195c7960685f6de9a7766f0d6932
	node = doc.createElement(str_)
	node.setAttribute('name', path)
	root, dirs, files = currentList(path)
	for dir_ in dirs :
<<<<<<< HEAD
		try :
			_dir = dir_.encode('utf-8')
			fullname = os.path.join(root, _dir)
			if not os.path.islink(fullname) and os.access(fullname, os.F_OK) and os.access(fullname, os.R_OK) \
																			and os.access(fullname, os.X_OK) :
				elem = makenode(fullname)
				node.appendChild(elem)
		except UnicodeEncodeError :
			#print 'UnicodeError_dir'
			pass
		except UnicodeDecodeError :
			#print 'UnicodeError_dir'
			pass
		finally :
			pass
	for file_ in files :
		try :
			#_file = unicode(file_, 'utf-8')
			_file = file_.encode('utf-8')
			fullname = os.path.join(root, str(_file))
			if not os.path.islink(fullname) and os.access(fullname, os.F_OK) and os.access(fullname, os.R_OK) :
				elem = doc.createElement('file')
				elem.setAttribute('name', str(_file))
				elem.setAttribute('size', str(os.path.getsize(fullname)/1024) + ' kByte(s)')
				node.appendChild(elem)
		except UnicodeEncodeError :
			#print 'UnicodeError_file'
			pass
		except UnicodeDecodeError :
			#print 'UnicodeError_file'
			pass
		finally :
			pass
=======
		fullname = os.path.join(root, dir_)
		if ( os.path.isdir(fullname) and os.access(fullname, os.R_OK) and \
			os.access(fullname, os.W_OK) and os.access(fullname, os.X_OK) ) :
			elem = makenode(fullname)
			node.appendChild(elem)
	for file_ in files :
		fullname = os.path.join(root, file_)
		if os.path.isfile(fullname) and os.access(fullname, os.R_OK) :
			elem = doc.createElement('file')
			elem.setAttribute('name', file_)
			node.appendChild(elem)
>>>>>>> 46bff2157961195c7960685f6de9a7766f0d6932
	return node

def parseFile(listNodes, tab = '	'):
	for i in xrange(listNodes.length):
		node = listNodes.item(i)
		name_ = node.localName
		if name_ == 'dir' :
			lenAttr = node.attributes.length
			print tab, name_, node.attributes.item(0).value  #, NodeType[node.nodeType]
			parseFile(node.childNodes, tab + '	')
		elif name_ == 'file' :
			lenAttr = node.attributes.length
			print tab, name_, node.attributes.item(0).value  #, NodeType[node.nodeType]

<<<<<<< HEAD
def listPrepare(_path):
	global dirList
	global doc
	#for node in doc.childNodes :
	#	doc.removeChild(node)
	doc = Document()
	dirList = []
	# print [str(_path)]
	for path in [str(_path)] :
		for root, dirs, files in os.walk(str(path), followlinks = False):
			dirList += [(root, dirs, files)]
		if dirList == [] :
			dirList += [(str(path),[],[])]
			# print dirList

	path_ = dirList[0][0]
	if os.access(path_, os.F_OK) and os.access(path_, os.R_OK) and os.access(path_, os.X_OK) :
		## and os.access(path_, os.W_OK) ) :
		str_ = 'dir'
		doc.appendChild(makenode(str(path_), str_))
	elif os.access(path_, os.F_OK) and os.access(path_, os.R_OK) :
		str_ = 'file'
		doc.appendChild(makenode(str(path_), str_))

def getResultFile(resultFileName):
	global doc
	# print doc.toprettyxml()
	fileName = str('/dev/shm/LightMight/cache/' + resultFileName)
	#os.remove(fileName)
	f = open(fileName, 'wb')
	try :
		#f.write(doc.toprettyxml())   ##
		doc.writexml(f, encoding = 'utf-8')
	except UnicodeError :
		print 'File not saved'
		f.close()
		return None
	f.close()

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

if __name__ == "__main__" :
	# Example action

	listPrepare('/tmp')
	print getResultFile('result')
=======
if __name__ == "__main__" :
	# Example action
	for path in [ '/tmp'] :
		for root, dirs, files in os.walk(path):
			dirList += [(root, dirs, files)]
		if dirList == [] :
			dirList += [(path,[],[])]
			print dirList

	path_ = dirList[0][0]
	if ( os.path.isdir(path_) and os.access(path_, os.R_OK) and os.access(path_, os.W_OK) and \
																			os.access(path_, os.X_OK) ) :
		str_ = 'dir'
		doc.appendChild(makenode(path_, str_))
	elif os.path.isfile(path_) and os.access(path_, os.R_OK) :
		str_ = 'file'
		doc.appendChild(makenode(path_, str_))

	print doc.toprettyxml()
	f = open('result', 'wb')
	#f.write(doc.toprettyxml())
	doc.writexml(f)
	f.close()

	if os.path.getsize('result') > 22 :
		datasource = open('result')
		dom2 = parse(datasource)   # parse an open file
		parseFile(dom2.childNodes)
		datasource.close()
	else :
		os.remove('result')
		print 'File was empty and removed'
>>>>>>> 46bff2157961195c7960685f6de9a7766f0d6932
