# -*- coding: utf-8 -*-

import os, os.path, string, random, socket

char_set = string.ascii_letters + string.digits

def randomString( j = 1):
	#return "".join( [random.choice(string.letters) for i in xrange(j)] )
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
			fileName = str('/dev/shm/' + name_)
			l = string.join(list_, '\n')
			f=open(fileName, 'wb')
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
	for i in xrange(maxValue - minValue) :
		try :
			s.bind(('127.0.0.1', minValue + i))
		except socket.error, x :
			#print x
			continue
		break
	addr, port = s.getsockname()
	return port
