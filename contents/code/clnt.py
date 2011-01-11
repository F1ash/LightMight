# -*- coding: utf-8 -*-

from xmlrpclib import ServerProxy
from threading import Thread
import os, os.path, tarfile, string

class DataRendering:
	def __init__(self):
		pass

	def fileToList(self, path_ = ''):
		if os.path.isfile(path_) :
			f=open(path_, 'rb')
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
		os.chdir('/tmp')
		fileList = ["python_logo.jpg", 'clnt.py', 'iy']
		for name in fileList :
			if s.typePath(name) :
				# print True
				# получаем структуру каталога со списком его файлов
				with open('/dev/shm/struct_', "wb") as handle:
					handle.write(s.requestCatalogStruct(name).data)
				s.python_clean('/dev/shm/_struct')
				# создаём структуру каталогов
				tar = tarfile.open('/dev/shm/struct_', 'r')
				tar.extractall()
				tar.close()
				# читаем список файлов
				# f = open(str(os.getcwd() + '/dev/shm/_listFiles'), 'rb')
				# catalogFileList = f.readlines()
				# f.close()
				listFiles = str(os.getcwd() + '/dev/shm/_listFiles')
				catalogFileList = DataRendering().fileToList(listFiles)
				print catalogFileList
				os.remove(listFiles)
				os.remove(str('/dev/shm/struct_'))
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
