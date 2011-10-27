# -*- coding: utf-8 -*-

import xmlrpclib, string, os, os.path, ssl, socket
from SSLOverloadClass import ThreadServer
from Functions import *

class ServerDaemon():
	def __init__(self, serveraddr = ('', 34000), commonSetOfSharedSource = None, \
				 parent = None, TLS = False, cert = ''):
		self.serverState = randomString(DIGITS_LENGTH)
		self.Parent = parent
		self.Parent.serverState = self.serverState
		self.commonSetOfSharedSource = commonSetOfSharedSource
		try :
			exception = False
			self._srv = ThreadServer(serveraddr, allow_none = True, \
									TLS = TLS, certificatePath = cert)
		except socket.error, err :
			print err, 'server init Error'
			exceptin = True
			self.Parent.reinitServer.emit()
		if not exception :
			self._srv.register_introspection_functions()
			self._srv.register_function(self.sessionID, 'sessionID')
			self._srv.register_function(self.python_clean, 'python_clean')
			self._srv.register_function(self.python_file, 'python_file')
			self._srv.register_function(self.requestSharedSourceStruct, 'requestSharedSourceStruct')
			self._srv.register_function(self.requestAvatar, 'requestAvatar')

	def sessionID(self):
		print self._srv.client_address, '--sessionID'
		fileName = randomString(DIGITS_LENGTH)
		_id = randomString(DIGITS_LENGTH)
		list_ = [fileName, _id, self.serverState, self.Parent.previousState]
		DataRendering().listToFile(list_, fileName)
		with open(Path.tempStruct(fileName), "rb") as handle :
			return xmlrpclib.Binary(handle.read())

	def sessionClose(self, sessionID = ''):
		print self._srv.client_address, '--sessionClose'
		pass

	def python_clean(self, name, sessionID = ''):
		print self._srv.client_address, '--python_clean'
		path_ = Path.tempStruct(name)
		if os.path.isfile(path_) : os.remove(path_)

	def python_file(self, id_, sessionID = ''):
		print self._srv.client_address, '--python_file'
		""" добавить обработчик ошибок соединения и существования файлов """
		#print id_, type(id_), str(self.commonSetOfSharedSource[int(id_)]), '  serv'

		if int(id_) in self.commonSetOfSharedSource :
				with open(str(self.commonSetOfSharedSource[int(id_)]), "rb") as handle :
					return xmlrpclib.Binary(handle.read())

	def requestSharedSourceStruct(self, name, sessionID = ''):
		print self._srv.client_address, '--requestSharedSourceStruct'
		#print Path.multiPath(Path.tempStruct, 'server', name), ' in requestSharedSourceStruct'
		with open(Path.multiPath(Path.tempStruct, 'server', name), "rb") as handle:
			return xmlrpclib.Binary(handle.read())

	def requestAvatar(self, sessionID = ''):
		print self._srv.client_address, '--requestAvatar'
		with open(unicode(self.Parent.avatarPath), "rb") as handle:
			return xmlrpclib.Binary(handle.read())

	def run(self):
		self._srv.serve_forever()

	def _shutdown(self, str_ = ''):
		self._srv.shutdown()
		print ' server terminated'
		self.Parent.serverDown.emit(str_)

if __name__ == '__main__':

	try :
		d = ServerDaemon()
		d.run()
	except KeyboardInterrupt :
		d._shutdown()
		print '\nexit'
