# -*- coding: utf-8 -*-

from xmlrpclib import ServerProxy
from threading import Thread
from Functions import *
import os, os.path, tarfile, string

class xr_client:
	def __init__(self, servaddr = 'http://localhost:34100'):
		self.servaddr = servaddr

	""" old variant
	def _run(self):
		s = ServerProxy(self.servaddr)

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
	"""

	def run(self):
		self.s = ServerProxy(self.servaddr)

		self.methods = self.s.system.listMethods()
		# get session Id & server State
		self.randomFileName = str('/dev/shm/' + randomString(24))
		with open(self.randomFileName, "wb") as handle:
			handle.write(self.s.sessionID().data)
		self.listRandomString = DataRendering().fileToList(self.randomFileName)
		self.s.python_clean(self.listRandomString[0])
		os.remove(self.randomFileName)
		print self.listRandomString, ' list of randomStrings'
		self.sessionID = self.listRandomString[1]
		print self.sessionID, ' session ID'
		self.serverState = self.listRandomString[2]
		print self.serverState, ' server State'

	def getSharedSourceStructFile(self):
		# get Shared Sources Structure
		self.structFileName = str('/dev/shm/LightMight/client/struct_' + self.sessionID)
		print self.structFileName, ' struct'
		with open(self.structFileName, "wb") as handle:
			handle.write(self.s.requestSharedSourceStruct('sharedSource_' + self.serverState).data)
		return self.structFileName

	def someFunc(self):
			if True :
				# создаём структуру каталогов
				tar = tarfile.open(self.structFileName, 'r')
				tar.extractall()
				tar.close()
				# читаем список файлов
				listFiles = str(os.getcwd() + '/dev/shm/_listFiles_' + self.sessionID)
				self.catalogFileList = DataRendering().fileToList(listFiles)
				print self.catalogFileList, ' catalog'
				os.remove(listFiles)
				os.remove(self.structFileName)
				# копируем файлы
				for name in self.catalogFileList :
					if name not in ['', ' ', '\n'] :
						with open(name, "wb") as handle:
							handle.write(self.s.python_file(name).data)
					else :
						print 'Path error'
			elif name not in ['', ' ', '\n'] :
				with open(name, "wb") as handle:
					handle.write(self.s.python_file(name).data)
			else :
				print 'Path error'

	def getSharedData(self, mask):
		""" после проверки неизменности статуса сервера отослать запрос на передачу
			данных маской выбранных ресурсов
		"""
		pass

	def _shutdown(self):
		self.shutdown()

if __name__ == '__main__':
	t = xr_client()
	t.run()
