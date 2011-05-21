# -*- coding: utf-8 -*-

import os, os.path, string, random, socket

def randomString( j = 1):
	return "".join( [random.choice(string.letters) for i in xrange(j)] )

class DataRendering:
	def __init__(self):
		pass

	def fileToList(self, path_ = ''):
		if os.path.isfile(path_) :
			f = open(path_, 'rb')
			l = f.read()
			f.close()
			return string.split(l, '\n')
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
		return Settings.valur(key).toString()
	else :
		return default

def getFreePort():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind(('127.0.0.1', 0))
	addr, port = s.getsockname()
	#print addr, port
	return port
