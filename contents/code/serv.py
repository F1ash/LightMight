# -*- coding: utf-8 -*-

import xmlrpclib, string, os, os.path, ssl, socket, time
from SSLOverloadClass import ThreadServer
from Functions import *

class ServerDaemon():
	def __init__(self, serveraddr = ('', 34000), commonSetOfSharedSource = None, \
				 parent = None, TLS = False, cert = '', restart = False):
		self.Parent = parent
		self.serverState = randomString(DIGITS_LENGTH) if not restart else self.Parent.previousState
		self.Parent.serverState = self.serverState
		self.commonSetOfSharedSource = commonSetOfSharedSource
		self.currentSessionID = {}	## {remoteServerAddr : (sessionID, customPolicy, temporarilySessionID)}
		self.WAIT = []	## list of blocked IP for getting sessionID
		try :
			error = False
			self._srv = ThreadServer(serveraddr, allow_none = True, \
									TLS = TLS, certificatePath = cert)
		except socket.error, err :
			print err, 'server init Error'
			error = True
		except socket.timeout, err :
			print err, 'server init Error'
			error = True
		finally : pass
		if not error :
			self._srv.register_introspection_functions()
			self._srv.register_function(self.sessionID, 'sessionID')
			self._srv.register_function(self.sessionClose, 'sessionClose')
			self._srv.register_function(self.accessRequest, 'accessRequest')
			self._srv.register_function(self.checkAccess, 'checkAccess')
			self._srv.register_function(self.checkServerState, 'checkServerState')
			self._srv.register_function(self.getSharedFile, 'getSharedFile')
			self._srv.register_function(self.requestSharedSourceStruct, 'requestSharedSourceStruct')
			self._srv.register_function(self.requestAvatar, 'requestAvatar')
			self.Parent.startServer.emit()
		else : self.Parent.initServeR.emit(self.Parent.threadSetupTree.treeModel, '', 'reStart', True)

	def sessionID(self, clientIP = ''):
		#print [self._srv.client_address, clientIP], ' --sessionID'
		if clientIP != self._srv.client_address[0] : return None
		_id = randomString(DIGITS_LENGTH)
		if clientIP not in self.currentSessionID :
			self.WAIT.append(clientIP)
			self.currentSessionID[clientIP] = (_id, self.Parent.Policy.Current)
			#print 'current Sessions', [self.currentSessionID, _id , self.serverState, self.Parent.previousState]
			data = ''.join((_id, str(self.serverState), str(self.Parent.previousState)))
			self.WAIT.remove(clientIP)
		else :
			data = 'ATTENTION:_REINIT_SERVER_FOR_MORE_STABILITY'
			#self.currentSessionID[clientIP] = _id
		#print [data], ' data'
		return xmlrpclib.Binary(data)

	def sessionClose(self, sessionID = ''):
		#print self._srv.client_address, '--sessionClose'
		#print sessionID, self.currentSessionID[self._srv.client_address[0]]
		addr = str(self._srv.client_address[0])
		if addr in self.currentSessionID :
			if sessionID == self.currentSessionID[addr][0] :
				del self.currentSessionID[addr]

	def accessRequest(self, sessionID = ''):
		address = str(self._srv.client_address[0])
		if address in self.currentSessionID :
			item = self.currentSessionID[address]
			if sessionID == item[0] :
				return item[1]
		return None

	def checkAccess(self, sessionID = ''):
		address = str(self._srv.client_address[0])
		if address not in self.currentSessionID : return xmlrpclib.Binary('ACCESS_DENIED')
		item = self.currentSessionID[address]
		if sessionID == item[0] :
			if item[1] == self.Parent.Policy.Allowed :
				return xmlrpclib.Binary('ACCESS_ALLOWED')
			elif item[1] == self.Parent.Policy.Confirm :
				self.Parent.setAccess.emit(address)
				timer = self._srv.timeout - 1
				i = 0
				while i < timer \
					  and (self.currentSessionID[address][1] == self.Parent.Policy.Confirm) \
					  and (len(self.currentSessionID[address]) < 3) :
					time.sleep(0.2)
					i += 0.2
				item = self.currentSessionID[address]
				if len(item) == 3 :
					if item[2] != 'CANCEL' :
						return xmlrpclib.Binary('TEMPORARILY_ALLOWED_ACCESS:' + item[2])
					else :
						newItem = (item[0], item[1])
						if address in self.Parent.serverThread.Obj.currentSessionID :
							self.currentSessionID[address] = newItem
				elif item[1] < self.Parent.Policy.Confirm :
					return xmlrpclib.Binary('ACCESS_ALLOWED')
		return xmlrpclib.Binary('ACCESS_DENIED')

	def checkServerState(self, sessionID = '', controlServerState = ''):
		addr = str(self._srv.client_address[0])
		if addr not in self.currentSessionID : return xmlrpclib.Boolean(False)
		controlID = self.currentSessionID[addr][0]
		if controlID != sessionID : return xmlrpclib.Boolean(False)
		if controlServerState != self.serverState :
			return xmlrpclib.Boolean(False)
		else : return xmlrpclib.Boolean(True)

	def getSharedFile(self, id_, sessionID = '', controlServerState = ''):
		#print self._srv.client_address, '--python_file'
		#print id_, type(id_), str(self.commonSetOfSharedSource), '  serv'
		addr = str(self._srv.client_address[0])
		if addr not in self.currentSessionID : return None
		item = self.currentSessionID[addr]
		if self.Parent.Policy.Blocked <= item[1] : return None
		elif self.Parent.Policy.Confirm == item[1] :
			if len(item) < 3 or sessionID != item[2] : return None
		elif self.Parent.Policy.Allowed == item[1] :
			if sessionID != item[0] : return None
		else : return None
		if id_.isalpha() and id_ == 'FINITA' :
			if len(item) == 3 :
				newItem = (item[0], item[1])
				self.currentSessionID[addr] = newItem
			return xmlrpclib.Binary('OK')
		elif int(id_) in self.commonSetOfSharedSource :
			fileName = str(self.commonSetOfSharedSource[int(id_)])
			if os.path.isfile(fileName) :
				with open(fileName, "rb") as handle :
					return xmlrpclib.Binary(handle.read())
		# return empty data for not raising exception
		# and not stopping download
		return xmlrpclib.Binary('')

	def requestSharedSourceStruct(self, name, sessionID = ''):
		#print self._srv.client_address, '--requestSharedSourceStruct; name :', name, 'sessionID', sessionID
		addr = str(self._srv.client_address[0])
		if addr not in self.currentSessionID : return None
		item = self.currentSessionID[addr]
		#print sessionID, item, self.Parent.Policy.Blocked
		if sessionID != item[0] : return None
		if self.Parent.Policy.Blocked <= item[1] : return None
		#elif self.Parent.Policy.Confirm == item[1] :
		#	if not self.confirmAction() : return None
		with open(Path.multiPath(Path.tempStruct, 'server', name), "rb") as handle:
			return xmlrpclib.Binary(handle.read())

	def requestAvatar(self, sessionID = ''):
		#print self._srv.client_address, '--requestAvatar'
		#print sessionID, self.currentSessionID[self._srv.client_address[0]]
		addr = str(self._srv.client_address[0])
		if addr not in self.currentSessionID or \
		   sessionID != self.currentSessionID[addr][0] : return None
		with open(unicode(self.Parent.avatarPath), "rb") as handle:
			return xmlrpclib.Binary(handle.read())

	def run(self):
		try :
			if hasattr(self, '_srv') : self._srv.serve_forever()
		except :
			print '[in run() ServerDaemon]: UnknownError'
			self._shutdown()
		finally : pass

	def _shutdown(self, str_ = '', loadFile = ''):
		self.currentSessionID.clear()
		if hasattr(self, '_srv') : self._srv.shutdown()
		print ' server terminated ...'
		if str_.startswith('REINIT') :
			self.Parent.serverDOWN.emit(self.serverState, loadFile)
		elif str_.startswith('reStart') :
			self.Parent.serverDown.emit(self.serverState)

	def __del__(self):
		self._shutdown()

if __name__ == '__main__':

	try :
		d = ServerDaemon()
		d.run()
	except KeyboardInterrupt :
		d._shutdown()
		print '\nexit'
