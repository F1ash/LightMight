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
		self.currentSessionID = {}	## {remoteServerAddr : sessionID}
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
			self._srv.register_function(self.sessionClose, 'sessionClose')
			self._srv.register_function(self.python_clean, 'python_clean')
			self._srv.register_function(self.python_file, 'python_file')
			self._srv.register_function(self.requestSharedSourceStruct, 'requestSharedSourceStruct')
			self._srv.register_function(self.requestAvatar, 'requestAvatar')

	def sessionID(self, clientIP = ''):
		#print self._srv.client_address, clientIP, '--sessionID'
		if clientIP != self._srv.client_address[0] : return None
		fileName = randomString(DIGITS_LENGTH)
		_id = randomString(DIGITS_LENGTH)
		if clientIP not in self.currentSessionID :
			self.currentSessionID[clientIP] = _id
		else :
			return None
			#self.currentSessionID[clientIP] = _id
		#print 'current Sessions', self.currentSessionID
		list_ = [fileName, _id, self.serverState, self.Parent.previousState]
		#print list_
		DataRendering().listToFile(list_, fileName)
		with open(Path.tempStruct(fileName), "rb") as handle :
			return xmlrpclib.Binary(handle.read())

	def sessionClose(self, sessionID = ''):
		#print self._srv.client_address, '--sessionClose'
		#print sessionID, self.currentSessionID[self._srv.client_address[0]]
		addr = self._srv.client_address[0]
		if addr in self.currentSessionID :
			if sessionID != self.currentSessionID[addr] : return None
			del self.currentSessionID[addr]

	def python_clean(self, name, sessionID = ''):
		#print self._srv.client_address, '--python_clean'
		#print sessionID, self.currentSessionID[self._srv.client_address[0]]
		if self._srv.client_address[0] not in self.currentSessionID or \
				sessionID != self.currentSessionID[self._srv.client_address[0]] : return None
		path_ = Path.tempStruct(name)
		if os.path.isfile(path_) : os.remove(path_)

	def python_file(self, id_, sessionID = ''):
		#print self._srv.client_address, '--python_file'
		controlID = self.currentSessionID[self._srv.client_address[0]]
		#print [sessionID, controlID]
		if sessionID != controlID : return None
		#print id_, type(id_), str(self.commonSetOfSharedSource), '  serv'

		if int(id_) in self.commonSetOfSharedSource :
			fileName = str(self.commonSetOfSharedSource[int(id_)])
			if os.path.isfile(fileName) :
				with open(fileName, "rb") as handle :
					return xmlrpclib.Binary(handle.read())
		# return empty data for not raising exception
		# and not stopping download
		return xmlrpclib.Binary('')

	def requestSharedSourceStruct(self, name, sessionID = ''):
		#print self._srv.client_address, '--requestSharedSourceStruct'
		#print sessionID, self.currentSessionID[self._srv.client_address[0]]
		if sessionID != self.currentSessionID[self._srv.client_address[0]] : return None
		#print Path.multiPath(Path.tempStruct, 'server', name), ' in requestSharedSourceStruct'
		with open(Path.multiPath(Path.tempStruct, 'server', name), "rb") as handle:
			return xmlrpclib.Binary(handle.read())

	def requestAvatar(self, sessionID = ''):
		#print self._srv.client_address, '--requestAvatar'
		#print sessionID, self.currentSessionID[self._srv.client_address[0]]
		if sessionID != self.currentSessionID[self._srv.client_address[0]] : return None
		with open(unicode(self.Parent.avatarPath), "rb") as handle:
			return xmlrpclib.Binary(handle.read())

	def run(self):
		self._srv.serve_forever()

	def _shutdown(self, str_ = ''):
		self.currentSessionID.clear()
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
