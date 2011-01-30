# -*- coding: utf-8 -*-

from xmlrpclib import ServerProxy
from threading import Thread
import os, os.path, tarfile, string, random

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

class xr_client:
	def __init__(self):
		pass

	def _run(self):
		servaddr = 'http://localhost:35113'
		s = ServerProxy(servaddr)

		methods = s.system.listMethods()
		for m in methods:
			print(m), s.system.methodSignature(m)
		fileList = ["python_logo.jpg", 'clnt.py', 'iy']
		os.chdir('/tmp')
		for name in fileList :
			with open(str(name + '.my.tar'), "wb") as handle:
				handle.write(s.python_logo(name).data)
			s.python_clean(str(name + '.tar'))

		for name in fileList :
			tar = tarfile.open(str(name + '.my.tar'), 'r')
			tar.extractall()
			tar.close()
			os.remove(str(name + '.my.tar'))

	def run_(self):
		servaddr = 'http://localhost:35113'
		s = ServerProxy(servaddr)

		methods = s.system.listMethods()
		# получение ID сессии
		randomFileName = str('/dev/shm/' + randomString(24))
		with open(randomFileName, "wb") as handle:
			handle.write(s.sessionID().data)
		listRandomString = DataRendering().fileToList(randomFileName)
		s.python_clean(listRandomString[0])
		os.remove(randomFileName)
		print listRandomString
		sessionID = listRandomString[1]

		os.chdir('/tmp')
		fileList = ["python_logo.jpg", 'clnt.py', 'iy']
		for name in fileList :
			if s.typePath(name) :
				# print True
				# получаем структуру каталога со списком его файлов
				structFileName = str('/dev/shm/struct_' + sessionID)
				with open(structFileName, "wb") as handle:
					handle.write(s.requestCatalogStruct(name, sessionID).data)
				s.python_clean(str('/dev/shm/_struct_' + sessionID))
				# создаём структуру каталогов
				tar = tarfile.open(structFileName, 'r')
				tar.extractall()
				tar.close()
				# читаем список файлов
				listFiles = str(os.getcwd() + '/dev/shm/_listFiles_' + sessionID)
				catalogFileList = DataRendering().fileToList(listFiles)
				print catalogFileList
				os.remove(listFiles)
				os.remove(structFileName)
				# копируем файлы
				for name in catalogFileList :
					if name not in ['', ' ', '\n'] :
						with open(name, "wb") as handle:
							handle.write(s.python_file(name).data)
					else :
						print 'Path error'
			elif name not in ['', ' ', '\n'] :
				with open(name, "wb") as handle:
					handle.write(s.python_file(name).data)
			else :
				print 'Path error'

if __name__ == '__main__':
	t = xr_client()
	t.run_()
