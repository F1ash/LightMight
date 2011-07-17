# -*- coding: utf-8 -*-

import xmlrpclib, string, os, os.path, ssl, socket
from DocXMLRPCServer import DocXMLRPCServer, DocXMLRPCRequestHandler
from SocketServer import ThreadingMixIn
from SSLOverloadClass import ThreadServer
from Functions import *

class ServerDaemon():
	def __init__(self, serveraddr = ('', 34000), commonSetOfSharedSource = None, \
				 parent = None, TLS = False, cert = ''):
		self.pathPref = pathPrefix()
		self.serverState = randomString(24)
		self.Parent = parent
		self.Parent.serverState = self.serverState
		self.commonSetOfSharedSource = commonSetOfSharedSource
		self._srv = ThreadServer(serveraddr, DocXMLRPCRequestHandler, allow_none = True, \
								 TLS = TLS, certificatePath = cert)
		self._srv.register_introspection_functions()
		self._srv.register_function(self.sessionID, 'sessionID')
		self._srv.register_function(self.python_clean, 'python_clean')
		self._srv.register_function(self.python_file, 'python_file')
		self._srv.register_function(self.requestSharedSourceStruct, 'requestSharedSourceStruct')
		self._srv.register_function(self.requestAvatar, 'requestAvatar')

	def sessionID(self):
		fileName = randomString(24)
		_id = randomString(24)
		#print '/dev/shm/LightMight/' + fileName, '  temporary file in sessionId'
		with open(self.pathPref + '/dev/shm/LightMight/' + fileName, 'wb') as f :
			#print fileName + '\n' + _id + '\n' + self.serverState + '\n' + self.Parent.previousState + '\n'
			f.write(fileName + '\n' + _id + '\n' + self.serverState + '\n' + self.Parent.previousState + '\n')
		with open(self.pathPref + '/dev/shm/LightMight/' + fileName, "rb") as handle :
			return xmlrpclib.Binary(handle.read())

	def python_clean(self, name):
		if os.path.isfile(self.pathPref + '/dev/shm/LightMight/' + name) :
			os.remove(self.pathPref + '/dev/shm/LightMight/' + name)

	def python_file(self, id_):
		""" добавить обработчик ошибок соединения и существования файлов """
		#print id_, type(id_), str(self.commonSetOfSharedSource[int(id_)]), '  serv'

		if int(id_) in self.commonSetOfSharedSource :
				with open(str(self.commonSetOfSharedSource[int(id_)]), "rb") as handle :
					return xmlrpclib.Binary(handle.read())

	def requestSharedSourceStruct(self, name):
		#print '/dev/shm/LightMight/server/' + name, ' in requestSharedSourceStruct'
		with open(self.pathPref + '/dev/shm/LightMight/server/' + name, "rb") as handle:
			return xmlrpclib.Binary(handle.read())

	def requestAvatar(self):
		with open(self.pathPref + unicode(self.Parent.avatarPath), "rb") as handle:
			return xmlrpclib.Binary(handle.read())

	def run(self):
		self._srv.serve_forever()

	def _shutdown(self):
		self._srv.shutdown()
		print ' server terminated'

if __name__ == '__main__':

	try :
		d = ServerDaemon()
		d.run()
	except KeyboardInterrupt :
		d._shutdown()
		print '\nexit'
