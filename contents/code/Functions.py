# -*- coding: utf-8 -*-

import os, os.path, string, random, socket, ssl, time, sys
from Path import  Path

char_set = string.ascii_letters + string.digits

def createStructure():
	for nameDir in [Path.TempAvatar, \
					Path.tempStruct('structure'), \
					Path.tempStruct('client'), \
					Path.tempStruct('server'), \
					Path.config('treeBackup'), \
					Path.Avatar] :
		if not os.path.isdir(nameDir):
			os.makedirs(nameDir)

def randomString( j = 1):
	return ''.join(random.sample(char_set, j))

class DataRendering:
	def __init__(self):
		pass

	def fileToList(self, path_ = ''):
		s = []
		if os.path.isfile(path_) :
			with open(path_, 'rb') as f :
				while True :
					s.append(f.readline(24))
					if s[len(s) - 1] == '' : break
		return s

	def listToFile(self, list_ = [], name_ = ''):
		fileName = ''
		if name_ != '' :
			#fileName = str(pathPrefix() + '/dev/shm/LightMight/' + name_)
			fileName = Path.tempStruct(name_)
			with open(fileName, 'wb') as f :
				f.writelines(list_)
		return fileName

def InitConfigValue(Settings = None, key = None, default = None):
	return Settings.value(key, default).toString()

def getIP():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	msg = ''
	Addr = '127.0.0.1'
	addressList = [("gmail.com", 80), ('0.0.0.0', 34001)]
	for address in addressList :
		for i in xrange(5) :
			try :
				error = False
				s.connect(address)
				addr = s.getsockname()[0]
				s.close()
			except socket.gaierror, err:
				print err
				error = True
			except : error = True
			finally : pass
			if not error :
				Addr = addr
				break
		if Addr not in ['', '0.0.0.0', '127.0.0.1'] : break
	return Addr

def getFreePort(minValue, maxValue):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	number_ = -1
	for i in xrange(maxValue - minValue) :
		try :
			s.bind(('127.0.0.1', minValue + i))
		except socket.error, x :
			#print x
			continue
		number_ = i
		break
	if number_ != -1 :
		addr, port = s.getsockname()
		s.close()
		return addr, port
	return '', 0

def dateStamp():
	return time.strftime("%Y.%m.%d_%H:%M:%S", time.localtime())

def moveFile(src, dst, delete = True):
	if os.path.isfile(src) :
		dst_dir = os.path.dirname(dst)
		if not os.path.isdir(dst_dir) :
			try :
				os.makedirs(dst_dir)
			except OSError, err :
				return False
		#print src, dst
		if src == dst : return True
		with open(src, 'rb') as srcFile :
			with open(dst, 'wb') as dstFile :
				dstFile.write(srcFile.read())
			if delete : os.remove(srcFile.name)
		return True
	else :
		return False

def pathPrefix():
	if sys.platform == 'win32':
		return unicode(os.path.dirname(os.tempnam()))
	else:
		return u''

def toolTipsHTMLWrap(iconPath = '', text = ''):
	return \
	'<table width="100%" border="0">\
		<col align="center" />\
		<col align="left"  width="100%" />\
		<tr>\
			<td><img src="' + iconPath + '" alt="" /></td>\
			<td>' + text + '</td>\
		</tr>\
	</table>'

def InCache(str_ = ''):
	if os.path.isfile(Path.tempCache(str_)) :
		return True, Path.tempCache(str_)
	elif os.path.isfile(Path.cache(str_)) :
		return True, Path.cache(str_)
	return False, ''

def DelFromCache(str_):
	i = 0
	result = [False, False, False, False]
	for path_ in [Path.TempCache, \
				 Path.TempAvatar, \
				 Path.Cache, \
				 Path.Avatar] :
		path = os.path.join(path_, str_)
		if os.path.isfile(path) :
			os.remove(path)
			result[i] = True
		i += 1
	return result

def getFolderSize(folder):
	total_size = os.path.getsize(folder)
	for item in os.listdir(folder) :
		itempath = os.path.join(folder, item)
		if os.path.isfile(itempath) :
			total_size += os.path.getsize(itempath)
		elif os.path.isdir(itempath) :
			total_size += getFolderSize(itempath)
	return total_size
