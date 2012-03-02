# -*- coding: utf-8 -*-

from xmlrpclib import ProtocolError, Fault
from SSLOverloadClass import SSLServerProxy
from httplib import HTTPException
from Functions import *
import os, os.path, socket

class xr_client:
	def __init__(self, addr = 'http://localhost', port = '34100', obj = None, parent = None, TLS = False):
		self.servaddr = addr + ':' + port
		self.serverState = ''
		self.Parent = parent
		if 'Obj' in dir(self) and self.Parent is None :
			pref = self.Obj
		elif 'Obj' in dir(self.Parent) and self.Parent.Obj is not None :
			pref = self.Parent.Obj
		else :
			pref = self.Parent
		self.servPrvKey = pref.servPrvKey
		self.servPubKey = pref.servPubKey
		self.servPubKeyHash = pref.servPubKeyHash if hasattr(pref, 'servPubKeyHash') \
												  else hashKey(self.servPubKey)
		#print [self.servPrvKey, self.servPubKey]
		self.TLS = False #TLS
		#print self.servaddr, ' clnt '
		if obj is not None :
			self.Obj = obj
			self.downLoadPath = unicode(InitConfigValue(self.Obj.Settings, 'DownLoadTo', Path.Temp))
			if not os.path.isdir(self.downLoadPath) : self.downLoadPath = Path.Temp

	def run(self):
		self.runned = False
		Settings = self.Obj.Settings if hasattr(self, 'Obj') else self.Parent.Obj.Settings
		self.showErrorMSGs = True if 'True' == Settings.value('ShowAllErrors', 'False').toString() else False
		count, succ = Settings.value('Probes', '5').toUInt()
		self.probeCount = count if succ else 5
		i = 0
		while i < self.probeCount :
			try :
				str_ = ''
				self.s = SSLServerProxy(self.servaddr, self.TLS)
				# self.methods = self.s.system.listMethods()
				if not self.s.Ready :
					str_ = '[in run() clnt.py ] Client not runned\nRepeat action.'
				else :
					self.runned = True
					break
			except socket.error, err :
				str_ = '[in run() clnt.py] SocketError1 : ' + str(err)
			except socket.timeout, err :
				str_ = '[in run() clnt.py] SocketError2 : ' + str(err)
			except Exception, err :
				str_ = '[in run() clnt.py] XXX : ' + str(err)
			except :
				str_ = '[in run() clnt.py ] UnknownError'
			finally : i += 1
		self.sendErrorString(str_)
		return True if str_ == '' else False

	def sendErrorString(self, str_ = '', fileName = None, show_ = True):
		if str_ != '' :
			print str_
			show = show_ if self.showErrorMSGs else False
			if fileName is not None and os.path.isfile(fileName) :
				os.remove(fileName)
			if 'Obj' in dir(self) and self.Parent is None :
				if show : self.Obj.errorString.emit(str_)
			elif 'Obj' in dir(self.Parent) and self.Parent.Obj is not None :
				if show : self.Parent.Obj.errorString.emit(str_)
			else :
				if show : self.Parent.errorString.emit(str_)

	def blockedIP(self, addr, checkSet):
		res = None
		while res is None :
			try :
				res = False
				for item in checkSet.itervalues() :
					if addr == item[0] :
						res = True
						break
			except RuntimeError, err :
				print '[in blockedIP() clnt.py ] RuntimeError :', err
				res = None
			finally : pass
		return res

	def getSessionID(self, ownIP = ''):
		#print [ownIP], ' own IP'
		addr = str(self.servaddr.split(':')[0])
		# check for address at processing in opposite side
		if hasattr(self.Parent, 'serverThread') :
			checkSet = self.Parent.serverThread.Obj.checkAddr
		elif hasattr(self.Parent.Obj, 'serverThread') :
			checkSet = self.Parent.Obj.serverThread.Obj.checkAddr
		elif hasattr(self.Parent.Parent, 'serverThread') :
			checkSet = self.Parent.Parent.serverThread.Obj.checkAddr
		else :
			self.sendErrorString('ATTENTION:_SET_OF_BLOCKED_IP_NOT_FOUND')
			return False
		if self.blockedIP(addr, checkSet) :
			self.sendErrorString('ATTENTION:_REQUEST_PROCESSING_IN_OPPOSITE_SERVER')
			return False
		# get session Id & server State
		try :
			str_ = ''
			try :
				if writeSocketReady(self.s.socket, self.s.timeout) :
					rndString = self.s.sessionID(ownIP, self.servPubKey, self.servPubKeyHash).data
				else :
					self.sendErrorString('[in getSessionID()] Socket_Not_Ready')
					return False
			except AttributeError, err :
				self.sendErrorString('[in getSessionID() clnt.py ] AddressMisMatch : ' + str(err))
				return False
			if rndString.startswith('ATTENTION:_REINIT_SERVER_FOR_MORE_STABILITY') :
				self.sendErrorString('ATTENTION:_REINIT_SERVER_FOR_MORE_STABILITY\n(IP in use OR received brocken data.)')
				return False
			#print [rndString], '-- server answer'
			answer = rndString.split('SERVER_PUB_KEY:')
			(remoteServPubKey, remoteServPubKeyHash) = answer[1].split('HASH:')
			if hashKey(remoteServPubKey) != remoteServPubKeyHash :
				self.sendErrorString('ATTENTION:_NETWORK_DATA_FAILURE')
				return False
			decrypted = prvKeyDecrypted(answer[0], self.servPrvKey)
			sessionID = decrypted[ : DIGITS_LENGTH ]
			encrypted = pubKeyEncrypted(''.join((sessionID, randomString(DIGITS_LENGTH))), remoteServPubKey)
			registered = self.s.clientRegAnswer(encrypted.encode('base64'))
			#print type(registered)
			if not registered :
				self.sendErrorString('ATTENTION:_CONNECT_NOT_REGISTERED')
				return False
			self.serverState = decrypted[2*DIGITS_LENGTH : 3*DIGITS_LENGTH ]
			self.previousState = decrypted[4*DIGITS_LENGTH : ]
			#print [decrypted, sessionID, self.serverState, self.previousState], '-- decrypted'
			policy = addToCertCache(remoteServPubKey, self.Parent.Obj.Policy.Current)
			self.Parent.Obj.serverThread.Obj.currentSessionID[addr] = \
					(sessionID, policy, None, remoteServPubKeyHash)
			#print [self.Parent.Obj.serverThread.Obj.currentSessionID] , '\n^^^current Sessions'
			if 'Obj' in dir(self) :
				self.Obj.currentRemoteServerState = self.serverState
				print "Handshake succeeded."
		except socket.error, err :
			str_ = '[in getSessionID() clnt.py ] SocketError1 : ' + str(err)
		except socket.timeout, err :
			str_ = '[in getSessionID() clnt.py ] SocketError2 : ' + str(err)
		except ProtocolError, err :
			'''print "[in getSessionID() clnt.py ] A protocol error occurred"
			print "URL: %s" % err.url
			print "HTTP/HTTPS headers: %s" % err.headers
			print "Error code: %d" % err.errcode
			print "Error message: %s" % err.errmsg'''
			str_ = '[in getSessionID() clnt.py ] ProtocolError : ' + str(err)
		except Fault, err :
			'''print "[in getSessionID() clnt.py ] A fault occurred"
			print "Fault code: %d" % err.faultCode
			print "Fault string: %s" % err.faultString'''
			str_ = '[in getSessionID() clnt.py ] FaultError : ' + str(err)
		except HTTPException, err :
			str_ = '[in getSessionID() clnt.py ] HTTPLibError : ' + str(err)
		except IOError, err :
			str_ = '[in getSessionID() clnt.py ] IOError : ' + str(err)
		finally :
			self.sendErrorString(str_)
		return True if str_ == '' else False

	def getSharedSourceStructFile(self, sessionID = ''):
		# get Shared Sources Structure
		self.structFileName = Path.tempCache(self.serverState)
		remoteSharedStruct = str('sharedSource_' + self.serverState)
		#print [self.structFileName], ' get structFile from ', [remoteSharedStruct]
		try :
			str_ = ''
			with open(self.structFileName, "wb") as handle :
				if writeSocketReady(self.s.socket, self.s.timeout) :
					try :
						handle.write(self.s.requestSharedSourceStruct(\
									remoteSharedStruct, \
									sessionID).data)
					except AttributeError, err :
						handle.close()
						str_ = '[in getSharedSourceStructFile() clnt.py ] SessionMismatch : ' + str(err)
				else :
					str_ = '[in getSharedSourceStructFile() clnt.py ] Socket_Not_Ready'
		except ProtocolError, err :
			'''print "A protocol error occurred"
			print "URL: %s" % err.url
			print "HTTP/HTTPS headers: %s" % err.headers
			print "Error code: %d" % err.errcode
			print "Error message: %s" % err.errmsg'''
			str_ = '[in getSharedSourceStructFile() ProtocolError] : ' + str(err)
		except Fault, err :
			'''print "A fault occurred"
			print "Fault code: %d" % err.faultCode
			print "Fault string: %s" % err.faultString'''
			str_ = '[in getSharedSourceStructFile() clnt.py ] FaultError : ' + str(err)
		except socket.error, err :
			str_ = '[in getSharedSourceStructFile() clnt.py ] SocketError1 : ' + str(err)
		except socket.timeout, err :
			str_ = '[in getSharedSourceStructFile() clnt.py ] SocketError2 : ' + str(err)
		except IOError, err :
			str_ = '[in getSharedSourceStructFile() clnt.py ] IOError : ' + str(err)
		finally :
			handle.close()
			self.sendErrorString(str_, self.structFileName)
		return self.structFileName, False if str_ == '' else True

	def getAvatar(self, sessionID = ''):
		self.avatarFileName = Path.tempAvatar(self.serverState)
		#print self.avatarFileName, ' avatarFileName, sessionID:', sessionID
		try :
			str_ = ''
			with open(self.avatarFileName, "wb") as handle :
				if writeSocketReady(self.s.socket, self.s.timeout) :
					try :
						handle.write(self.s.requestAvatar(sessionID).data)
					except AttributeError, err :
						handle.close()
						str_ = '[in getAvatar()] SessionMismatch : ' + str(err)
					except ProtocolError, err :
						'''print "[in getAvatar() clnt.py ] A protocol error occurred"
						print "URL: %s" % err.url
						print "HTTP/HTTPS headers: %s" % err.headers
						print "Error code: %d" % err.errcode
						print "Error message: %s" % err.errmsg'''
						str_ = '[in getAvatar() clnt.py ] ProtocolError : ' + str(err)
					except Fault, err :
						'''print "[in getAvatar() A fault occurred"
						print "Fault code: %d" % err.faultCode
						print "Fault string: %s" % err.faultString'''
						str_ = '[in getAvatar() clnt.py ] FaultError : ' + str(err)
					except socket.error, err :
						str_ = '[in getAvatar() clnt.py ] SocketError1 : ' + str(err)
					except socket.timeout, err :
						str_ = '[in getAvatar() clnt.py ] SocketError2 : ' + str(err)
					finally : handle.close()
				else :
					str_ = '[in getAvatar() clnt.py ] Socket_Not_Ready'
		except IOError, err :
			str_ = '[in getAvatar() clnt.py ] IOError : ' + str(err)
		finally :
			self.sendErrorString(str_, self.avatarFileName)
		return self.avatarFileName

	def getAccess(self, sessionID = '', remoteServerState = ''):
		try :
			str_ = ''
			if writeSocketReady(self.s.socket, self.s.timeout) :
				access = self.s.accessRequest(sessionID, remoteServerState)
			else :
				str_ == '[in getAccess() clnt.py ] Socket_Not_Ready'
				access = -1
		except AttributeError, err :
			self.sendErrorString('[in getAccess() clnt.py ] AttributeError : ' + str(err))
			access = -1
		except socket.error, err :
			str_ = '[in getAccess() clnt.py ] SocketError1 : ' + str(err)
			access = -1
		except socket.timeout, err :
			str_ = '[in getAccess() clnt.py ] SocketError2 : ' + str(err)
			access = -1
		except ProtocolError, err :
			'''print "[in getAccess() clnt.py ] A protocol error occurred"
			print "URL: %s" % err.url
			print "HTTP/HTTPS headers: %s" % err.headers
			print "Error code: %d" % err.errcode
			print "Error message: %s" % err.errmsg'''
			str_ = '[in getAccess() clnt.py ] ProtocolError : ' + str(err)
			access = -1
		except Fault, err :
			'''print "[in getAccess() clnt.py ] A fault occurred"
			print "Fault code: %d" % err.faultCode
			print "Fault string: %s" % err.faultString'''
			str_ = '[in getAccess() clnt.py ] FaultError : ' + str(err)
			access = -1
		except HTTPException, err :
			str_ = '[in getAccess() clnt.py ] HTTPLibError : ' + str(err)
			access = -1
		finally :
			self.sendErrorString(str_)
		return access

	def getSharedData(self, maskSet, downLoadPath, emitter, sessionID = ''):
		if len(maskSet) == 0 :
			self.sendErrorString('Empty job. Upload canceled.')
			return False
		# check remote server status
		if not hasattr(self, 's') or not writeSocketReady(self.s.socket, self.s.timeout) :
			self.sendErrorString('[in getSharedData()] Socket_Not_Ready')
			return False
		# check access
		access = self.s.checkAccess(sessionID).data
		tempSessionID = randomString(DIGITS_LENGTH)
		if access == 'ACCESS_ALLOWED' :
			pass
		elif access == 'ACCESS_DENIED' :
			self.sendErrorString('ACCESS_DENIED')
			return False
		elif access.startswith('TEMPORARILY_ALLOWED_ACCESS:') :
			self.sendErrorString('TEMPORARILY_ALLOWED_ACCESS')
			tempSessionID = access.split(':')[1]
			#print 'temporarySessionID', sessionID
		else :
			self.sendErrorString('ANSWER_INCORRECT')
			return False
		# get shared sources
		for i in maskSet.iterkeys() :
			if maskSet[i][0] == 1 :
				_path = os.path.join(downLoadPath, maskSet[i][1])
				path, tail = os.path.split(_path)
				#print downLoadPath, _path, i, ' clnt', path, tail
				try :
					if not os.path.exists(path) : os.makedirs(path)
				except IOError, err:
					self.sendErrorString('[in getSharedData() clnt.py ] IOError : ' + str(err))
					continue
				try :
						str_ = ''
						with open(_path, "wb") as handle :
							#if not(writeSocketReady(self.s.socket, self.s.timeout)) :
							#	handle.close()
							#	continue
							handle.write(self.s.getSharedFile(str(i), sessionID, tempSessionID).data)
						#print 'Downloaded : ', maskSet[i][1]
				except AttributeError, err :
						str_ = '[in getSharedData() clnt.py ] SessionMismatch : ' + str(err)
						self.sendErrorString(str_)
						return False
				except ProtocolError, err :
						str_ = '[in getSharedData() clnt.py ] ProtocolError : ' + str(err)
						"""print "A protocol error occurred"
						print "URL: %s" % err.url
						print "HTTP/HTTPS headers: %s" % err.headers
						print "Error code: %d" % err.errcode
						print "Error message: %s" % err.errmsg"""
				except Fault, err :
						str_ = '[in getSharedData() clnt.py ] FaultError : ' + str(err)
						"""print "A fault occurred"
						print "Fault code: %d" % err.faultCode
						print "Fault string: %s" % err.faultString"""
				except socket.error, err :
						str_ = '[in getSharedData() clnt.py ] SocketError1 : ' + str(err)
				except socket.timeout, err :
						str_ = '[in getSharedData() clnt.py ] SocketError2 : ' + str(err)
				finally :
						handle.close()
						self.sendErrorString(str_)
				size_ = maskSet[i][2]
				if size_ == 0 : size_ = 1
				emitter.nextfile.emit(size_)
		if self.s.getSharedFile('FINITA', sessionID, tempSessionID).data != 'OK' :
			self.sendErrorString('Loading was completed incorrectly.')
			return False
		return True

	def sessionClose(self, sessionID = ''):
		try :
			str_ = ''
			if writeSocketReady(self.s.socket, self.s.timeout) :
				self.s.sessionClose(sessionID)
			else : str_ = '[in sessionClose() clnt.py ] Socket_Not_Ready'
		except ProtocolError, err :
			str_ = '[in sessionClose() clnt.py ] ProtocolError : ' + str(err)
			"""print "[in sessionClose() clnt.py ] A protocol error occurred"
			print "URL: %s" % err.url
			print "HTTP/HTTPS headers: %s" % err.headers
			print "Error code: %d" % err.errcode
			print "Error message: %s" % err.errmsg"""
		except Fault, err :
			str_ = '[in sessionClose() clnt.py ] FaultError : ' + str(err)
			"""print "[in sessionClose() clnt.py ] A fault occurred"
			print "Fault code: %d" % err.faultCode
			print "Fault string: %s" % err.faultString"""
		except HTTPException, err :
			str_ = '[in sessionClose() clnt.py ] HTTPLibError : ' + str(err)
		except socket.error, err :
			str_ = '[in sessionClose() clnt.py ] SocketError1 : ' + str(err)
		except socket.timeout, err :
			str_ = '[in sessionClose() clnt.py ] SocketError2 : ' + str(err)
		finally :
			self.sendErrorString(str_)

	def _shutdown(self, str_= '', nothing = ''):
		#print 'socket closing...'
		if hasattr(self, 's') :
			try :
				self.s.socket.shutdown(socket.SHUT_WR)
			except socket.error, err :
				print '[in _shutdown() clnt.py ] SocketError1 : ', err
			except socket.timeout, err :
				print '[in _shutdown() clnt.py ] SocketError2 : ', err
			finally :
				self.s.socket.close()

	def __del__(self):
		self._shutdown()

if __name__ == '__main__':
	t = xr_client()
	t.run()
