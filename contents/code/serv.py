# -*- coding: utf-8 -*-

import xmlrpclib, string, os, os.path, ssl, socket, time
from SSLOverloadClass import ThreadServer
from Functions import *
from clnt import xr_client

class ServerDaemon():
	def __init__(self, serveraddr = ('', 34000), commonSetOfSharedSource = None, \
				 parent = None, TLS = False, cert = '', restart = False):
		self.Parent = parent
		self.serverState = randomString(DIGITS_LENGTH) if not restart else self.Parent.previousState
		self.Parent.serverState = self.serverState
		self.commonSetOfSharedSource = commonSetOfSharedSource
		## currentSessionID : set of registered client`s data
		##	{remoteServerAddr : (sessionID, customPolicy, temporarilySessionID, certHash)}
		self.currentSessionID = {}
		## checkAddr : set of blocked IP for getting sessionID
		##	{_id : (clientIP, time.time(), clientCert, certHash)}
		self.checkAddr = {}
		self.servPubKey = str(self.Parent.servPubKey)
		self.servPubKeyHash = self.Parent.servPubKeyHash
		self.servPrvKey = str(self.Parent.servPrvKey)
		#print [self.servPrvKey, self.servPubKey]
		try :
			error = False; err = ''
			self._srv = ThreadServer(serveraddr, allow_none = True, \
									TLS = TLS, certificatePath = cert)
			if not self._srv.Ready :
				print 'server init Error'
				error = True
		except socket.error, err :
			print err, 'server init Error'
			error = True
		except socket.timeout, err :
			print err, 'server init Error'
			error = True
		finally : pass
		if not error :
			self._srv.register_introspection_functions()
			self._srv.register_function(self.clientRegAnswer, 'clientRegAnswer')
			self._srv.register_function(self.sessionID, 'sessionID')
			self._srv.register_function(self.sessionClose, 'sessionClose')
			self._srv.register_function(self.accessRequest, 'accessRequest')
			self._srv.register_function(self.checkAccess, 'checkAccess')
			self._srv.register_function(self.getSharedFile, 'getSharedFile')
			self._srv.register_function(self.requestSharedSourceStruct, 'requestSharedSourceStruct')
			self._srv.register_function(self.requestAvatar, 'requestAvatar')
			self.Parent.startServer.emit()
		else :
			self._shutdown()
			self.Parent.showMSG(str(err) + '\nServer not runned.\nRestart it.')
			if hasattr(self.Parent, 'threadSetupTree') :
				self.Parent.initServeR.emit(self.Parent.threadSetupTree.treeModel, '', str(self.serverState), True)
			else :
				self.Parent.initServeR.emit(None, '', str(self.serverState), False)

	def sessionID_exist(self, sessionID):
		decrypt = prvKeyDecrypted(sessionID.decode('base64'), self.servPrvKey)
		chunk1 = decrypt[:DIGITS_LENGTH]
		chunk2 = decrypt[DIGITS_LENGTH:]
		exist = False
		thisItem = None
		for item in self.currentSessionID.iteritems() :
			if chunk1 == item[1][0] or chunk2 == item[1][0]:
				exist = True
				thisItem = item
		return exist, thisItem

	def checkMultiple(self, certHash):
		try :
			res1 = False; res2 = False
			## TODO : mutex lock
			for item in self.currentSessionID.itervalues() :
				if certHash == item[3] :
					res1 = True
					break
			for item in self.checkAddr.itervalues() :
				if certHash == item[3] :
					res2 = True
					break
			## mutex unlock
			res = res1 or res2
		except RuntimeError, err :
			print '[in checkMultiple() ServerDaemon]: ', err
			res = None
		finally : pass
		return res

	def clientRegAnswer(self, clientAnswer = ''):
		#print clientAnswer.decode('base64'), '-- CA'
		decrypt = prvKeyDecrypted(clientAnswer.decode('base64'), self.servPrvKey)
		_id = decrypt[:DIGITS_LENGTH]
		#print [clientAnswer, _id, self.checkAddr[_id]], '-- client answer'
		if _id in self.checkAddr and \
				((self.checkAddr[_id][1] + TIMEOUT - 1.0) > time.time()) :
			## TODO : mutex lock
			policy = readCashPolicy(self.checkAddr[_id][2], self.Parent.Policy.Current)
			self.currentSessionID[self.checkAddr[_id][0]] = \
				(_id, policy, None, self.checkAddr[_id][3])
			del self.checkAddr[_id]
			# clean delayed address
			key = True
			while key :
				delayed = []
				try :
					for key in self.checkAddr.keys() :
						if (self.checkAddr[key][1] + TIMEOUT - 1.0) < time.time() :
							delayed.append(key)
					for key in delayed : del self.checkAddr[key]
					key = False
				except RuntimeError, err :
					print '[in clientRegAnswer() ServerDaemon]: ', err
				finally : pass
			## mutex unlock
			return xmlrpclib.Boolean(True)
		else :
			return xmlrpclib.Boolean(False)

	def sessionID(self, clientIP = '', clientCert = '', certHash = ''):
		''' проверить по хешу сертификата & ip:port наличие активного контакта;
			при отсутствии создать пару {id:randomKey}, зашифровать ключём клиента ID сессии
			и передать со своим публичным ключём; ожидать TIMEOUT-1 подтверждение от клиента,
			расшифровав его своим приватным.
		'''
		#print [clientIP, clientCert, certHash], '-- session'
		if clientIP not in self.currentSessionID and certHash == hashKey(clientCert):
			multiple = None
			while multiple is None :
				multiple = self.checkMultiple(certHash)
			if not multiple :
				_id = randomString(DIGITS_LENGTH)
				#print [_id, self.serverState, str(self.Parent.previousState)]
				_str = ''.join((_id, randomString(DIGITS_LENGTH), str(self.serverState), \
								randomString(DIGITS_LENGTH), str(self.Parent.previousState)))
				encrypted = pubKeyEncrypted(_str, clientCert)
				#print [encrypted, self.servPubKey, self.servPubKeyHash], '-- before join'
				data = ''.join((encrypted, 'SERVER_PUB_KEY:', self.servPubKey, 'HASH:', self.servPubKeyHash))
				self.checkAddr[_id] = (clientIP, time.time(), clientCert, certHash)
			else : data = 'ATTENTION:_MULTIPLE_CONNECT'
		else :
			data = 'ATTENTION:_REINIT_SERVER_FOR_MORE_STABILITY'
			## TODO : make the check available clientIP
		#print [data], ' data'
		return xmlrpclib.Binary(data)

	def sessionClose(self, sessionID = ''):
		exist, item = self.sessionID_exist(str(sessionID))
		if exist :
				del self.currentSessionID[item[0]]

	def accessRequest(self, sessionID = ''):
		exist, item = self.sessionID_exist(str(sessionID))
		if exist : return item[1][1]
		return None

	def checkAccess(self, sessionID = ''):
		exist, _item = self.sessionID_exist(str(sessionID))
		if not exist : return xmlrpclib.Binary('ACCESS_DENIED')
		address = str(_item[0])
		item = _item[1]
		if item[1] == self.Parent.Policy.Allowed :
			return xmlrpclib.Binary('ACCESS_ALLOWED')
		elif item[1] == self.Parent.Policy.Confirm :
			self.Parent.setAccess.emit(address)
			timer = self._srv.timeout - 1
			i = 0
			while i < timer \
				  and (self.currentSessionID[address][2] is None) \
				  and (self.currentSessionID[address][1] > self.Parent.Policy.Allowed) :
				time.sleep(0.2)
				i += 0.2
			item = self.currentSessionID[address]
			if item[1] < self.Parent.Policy.Confirm :
				return xmlrpclib.Binary('ACCESS_ALLOWED')
			elif item[2] != 'CANCEL' :
				return xmlrpclib.Binary('TEMPORARILY_ALLOWED_ACCESS:' + item[2])
			else :
				newItem = (item[0], item[1], None, item[3])
				if address in self.Parent.serverThread.Obj.currentSessionID :
					self.currentSessionID[address] = newItem
		return xmlrpclib.Binary('ACCESS_DENIED')

	def getSharedFile(self, id_, sessionID = '', tempSessionID = ''):
		exist, _item = self.sessionID_exist(str(sessionID))
		if not exist : return None
		addr = str(_item[0])
		item = self.currentSessionID[addr]
		if self.Parent.Policy.Blocked <= item[1] : return None
		elif self.Parent.Policy.Confirm == item[1] :
			if tempSessionID != item[2] : return None
		if id_.isalpha() and id_ == 'FINITA' :
			newItem = (item[0], item[1], None, item[3])
			self.currentSessionID[addr] = newItem
			return xmlrpclib.Binary('OK')
		elif int(id_) in self.commonSetOfSharedSource :
			fileName = self.commonSetOfSharedSource[int(id_)]
			if os.path.isfile(fileName) :
				with open(fileName, "rb") as handle :
					return xmlrpclib.Binary(handle.read())
		# return empty data for not raising exception
		# and not stopping download
		return xmlrpclib.Binary('')

	def requestSharedSourceStruct(self, name, sessionID = ''):
		exist, _item = self.sessionID_exist(str(sessionID))
		if not exist : return None
		if self.Parent.Policy.Blocked <= _item[1][1] : return None
		with open(Path.multiPath(Path.tempStruct, 'server', name), "rb") as handle:
			return xmlrpclib.Binary(handle.read())

	def requestAvatar(self, sessionID = ''):
		exist, _item = self.sessionID_exist(str(sessionID))
		if not exist : return None
		with open(unicode(self.Parent.avatarPath), "rb") as handle:
			return xmlrpclib.Binary(handle.read())

	def run(self):
		try :
			self.runned = True
			if hasattr(self, '_srv') : self._srv.serve_forever()
			else : self.runned = False
		except :
			print '[in run() ServerDaemon]: UnknownError'
			self.runned = False
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
