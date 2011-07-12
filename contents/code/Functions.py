# -*- coding: utf-8 -*-

import os, os.path, string, random, socket, ssl, time, sys

char_set = string.ascii_letters + string.digits

def createStructure():
	pathPref = pathPrefix()
	for nameDir in [pathPref + '/dev/shm/LightMight/cache', \
					pathPref + '/dev/shm/LightMight/cache/avatars/', \
					pathPref + '/dev/shm/LightMight/structure', \
					pathPref + '/dev/shm/LightMight/client', \
					pathPref + '/dev/shm/LightMight/server', \
					os.path.expanduser('~/.config/LightMight/treeBackup')] :
		if not os.path.isdir(nameDir):
			os.makedirs(nameDir)

def randomString( j = 1):
	return ''.join(random.sample(char_set, j))

class DataRendering:
	def __init__(self):
		pass

	def fileToList(self, path_ = ''):
		if os.path.isfile(path_) :
			f = open(path_, 'rb')
			l = f.read()
			f.close()
			s = string.split(l, '\n')
			for i in xrange(s.count('')) :
				s.remove('')
			return s
		else :
			return []

	def listToFile(self, list_ = [], name_ = ''):
		if name_ != '' :
			fileName = str(pathPrefix() + '/dev/shm/' + name_)
			l = string.join(list_, '\n')
			f = open(fileName, 'wb')
			f.write(l)
			f.close()
			return fileName
		else :
			return ''

def InitConfigValue(Settings = None, key = None, default = None):
	if not Settings is None and Settings.contains(key) :
		return Settings.value(key).toString()
	else :
		return default

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
	if os.path.isfile(pathPrefix() + '/dev/shm/LightMight/cache/' + str_) :
		return True, pathPrefix() + '/dev/shm/LightMight/cache/' + str_
	elif os.path.isfile(pathPrefix() + os.path.expanduser('~/.cache/LightMight/') + str_) :
		return True, pathPrefix() + os.path.expanduser('~/.cache/LightMight/') + str_
	return False, ''
