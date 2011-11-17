# -*- coding: utf-8 -*-

from xmlrpclib import ProtocolError, Fault
from SSLOverloadClass import SSLServerProxy
from httplib import HTTPException
from Functions import *
import os, os.path, string, socket, ssl

class xr_client:
	def __init__(self, addr = 'http://localhost', port = '34100', obj = None, parent = None, TLS = False):
		self.servaddr = addr + ':' + port
		self.serverState = ''
		self.Parent = parent
		self.TLS = TLS
		#print self.servaddr, ' clnt '
		if obj is not None :
			self.Obj = obj
			self.downLoadPath = unicode(InitConfigValue(self.Obj.Settings, 'DownLoadTo', Path.Temp))
			if not os.path.isdir(self.downLoadPath) : self.downLoadPath = Path.Temp

	def run(self):
		try :
			str_ = ''
			self.s = SSLServerProxy(self.servaddr, self.TLS)
			# self.methods = self.s.system.listMethods()
		except socket.error, err :
			str_ = '[in run() clnt.py] SocketError1 : ' + err
		except socket.timeout, err :
			str_ = '[in run() clnt.py] SocketError2 : ' + err
		except Exception, err :
			str_ = '[in run() clnt.py] :' + err
		except :
			str_ = '[in run() UnknownError] '
		finally :
			self.sendErrorString(str_)

	def sendErrorString(self, str_ = '', fileName = None):
		if str_ != '' :
			print str_
			if fileName is not None and os.path.isfile(fileName) :
				os.remove(fileName)
			if 'Obj' in dir(self) and self.Parent is None :
				self.Obj.errorString.emit(str_)
			elif 'Obj' in dir(self.Parent) and self.Parent.Obj is not None :
				self.Parent.Obj.errorString.emit(str_)
			else :
				self.Parent.errorString.emit(str_)

	def getSessionID(self, ownIP = ''):
		#print [ownIP], ' own IP'
		try :
			str_ = ''
			# get session Id & server State
			try :
				randomString = self.s.sessionID(ownIP).data
			except AttributeError, err :
				self.sendErrorString('[in getSessionID() AddressMissMatch]:' + err)
				return False
			if randomString.startswith('ATTENTION:_REINIT_SERVER_FOR_MORE_STABILITY') :
				self.sendErrorString('ATTENTION:_REINIT_SERVER_FOR_MORE_STABILITY')
				return False
			sessionID = randomString[ : DIGITS_LENGTH ]
			self.serverState = randomString[DIGITS_LENGTH : 2*DIGITS_LENGTH ]
			self.previousState = randomString[2*DIGITS_LENGTH : ]
			#print randomString
			#print sessionID, ' session ID'
			#print self.serverState, ' server State'
			#print self.previousState, 'previous server State'
			self.Parent.Obj.serverThread.Obj.currentSessionID[str(self.servaddr.split(':')[0])] = \
					(sessionID, self.Parent.Obj.Policy.Current)
			#print self.Parent.Obj.serverThread.Obj.currentSessionID , '\n^^^current Sessions'
			if 'Obj' in dir(self) :
				self.Obj.currentRemoteServerState = self.serverState
				print "Handshake succeeded."
		except socket.error, err :
			str_ = '[in getSessionID()] SocketError1 : ' + err
		except socket.timeout, err :
			str_ = '[in getSessionID()] SocketError2 : ' + err
		except ProtocolError, err :
			'''print "[in getSessionID()] A protocol error occurred"
			print "URL: %s" % err.url
			print "HTTP/HTTPS headers: %s" % err.headers
			print "Error code: %d" % err.errcode
			print "Error message: %s" % err.errmsg'''
			str_ = '[in getSessionID()] ProtocolError: ' + str(err)
		except Fault, err :
			'''print "[in getSessionID()] A fault occurred"
			print "Fault code: %d" % err.faultCode
			print "Fault string: %s" % err.faultString'''
			str_ = '[in getSessionID()] FaultError: ' + str(err)
		except HTTPException, err :
			str_ = '[in getSessionID()] HTTPLibError : ' + err
		except IOError, err :
			str_ = '[in getSessionID()] IOError : ' + err
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
					try :
						handle.write(self.s.requestSharedSourceStruct(\
									remoteSharedStruct, \
									sessionID).data)
					except AttributeError, err :
						handle.close()
						str_ = '[in getSharedSourceStructFile() SessionMismatch' + str(err)
		except ProtocolError, err :
			'''print "A protocol error occurred"
			print "URL: %s" % err.url
			print "HTTP/HTTPS headers: %s" % err.headers
			print "Error code: %d" % err.errcode
			print "Error message: %s" % err.errmsg'''
			str_ = '[in getSharedSourceStructFile()] ProtocolError: ' + str(err)
		except Fault, err :
			'''print "A fault occurred"
			print "Fault code: %d" % err.faultCode
			print "Fault string: %s" % err.faultString'''
			str_ = '[in getSharedSourceStructFile()] FaultError: ' + str(err)
		except socket.error, err :
			str_ = '[in getSharedSourceStructFile()] SocketError1 : ' + err
		except socket.timeout, err :
			str_ = '[in getSharedSourceStructFile()] SocketError2 : ' + err
		except IOError, err :
			str_ = '[in getSharedSourceStructFile()] IOError : ' + err
		finally :
			self.sendErrorString(str_, self.structFileName)
		return self.structFileName, False if str_ == '' else True

	def getAvatar(self, sessionID = ''):
		self.avatarFileName = Path.tempAvatar(self.serverState)
		#print self.avatarFileName, ' avatarFileName, sessionID:', sessionID
		try :
			str_ = ''
			with open(self.avatarFileName, "wb") as handle :
					try :
						handle.write(self.s.requestAvatar(sessionID).data)
					except AttributeError, err :
						handle.close()
						str_ = '[in getAvatar() SessionMismatch]:' + err
					except ProtocolError, err :
						'''print "[in getAvatar() A protocol error occurred"
						print "URL: %s" % err.url
						print "HTTP/HTTPS headers: %s" % err.headers
						print "Error code: %d" % err.errcode
						print "Error message: %s" % err.errmsg'''
						str_ = '[in getAvatar() ProtocolError : ' + str(err)
					except Fault, err :
						'''print "[in getAvatar() A fault occurred"
						print "Fault code: %d" % err.faultCode
						print "Fault string: %s" % err.faultString'''
						str_ = '[in getAvatar() FaultError : ' + str(err)
					except socket.error, err :
						str_ = '[in getAvatar() SocketError1 : ' + err
					except socket.timeout, err :
						str_ = '[in getAvatar() SocketError2 : ' + err
					finally : pass
		except IOError, err :
			str_ = '[in getAvatar()] IOError : ' + err
		finally :
			self.sendErrorString(str_, self.avatarFileName)
		return self.avatarFileName

	def getSharedData(self, maskSet, downLoadPath, emitter, \
					  remoteServerState = 'NOTHING', \
					  sessionID = ''):
		if len(maskSet) == 0 :
			self.sendErrorString('Empty job. Upload canceled.')
			emitter.complete.emit()
			return None
		# check remote server state
		if not self.s.checkServerState(sessionID, remoteServerState) :
			str_ = 'Status of the remote server is changed or server is refused.\n Upload canceled.'
			self.sendErrorString(str_)
			emitter.complete.emit()
			return None 
		# check access
		access = self.s.checkAccess(sessionID).data
		if access == 'ACCESS_ALLOWED' :
			pass
		elif access == 'ACCESS_DENIED' :
			emitter.complete.emit()
			self.sendErrorString('ACCESS_DENIED')
			return None
		elif access.startswith('TEMPORARILY_ALLOWED_ACCESS:') :
			self.sendErrorString('TEMPORARILY_ALLOWED_ACCESS')
			sessionID = access.split(':')[1]
			print 'temporarySessionID', sessionID
		else :
			self.sendErrorString('ANSWER_INCORRECT')
			return None
		for i in maskSet.iterkeys() :
			if maskSet[i][0] == 1 :
				_path = os.path.join(downLoadPath, maskSet[i][1])
				path, tail = os.path.split(_path)
				#print downLoadPath, _path, i, ' clnt', path, tail
				if not os.path.exists(path) :
					try :
						os.makedirs(path)
					except IOError, err:
						self.sendErrorString('[in getSharedData()] IOError : ' + err)
						continue
				with open(_path, "wb") as handle :
					try :
						str_ = ''
						handle.write(self.s.getSharedFile(str(i), sessionID).data)
						#print 'Downloaded : ', maskSet[i][1]
					except AttributeError, err :
						str_ = '[in getSharedData() SessionMismatch] : ' + err
						emitter.complete.emit()
						self.sendErrorString(str_)
						return None
					except ProtocolError, err :
						str_ = '[in getSharedData()] ProtocolError : ' + str(err)
						"""print "A protocol error occurred"
						print "URL: %s" % err.url
						print "HTTP/HTTPS headers: %s" % err.headers
						print "Error code: %d" % err.errcode
						print "Error message: %s" % err.errmsg"""
					except Fault, err :
						str_ = '[in getSharedData()] FaultError : ' + str(err)
						"""print "A fault occurred"
						print "Fault code: %d" % err.faultCode
						print "Fault string: %s" % err.faultString"""
					except socket.error, err :
						str_ = '[in getSharedData()] SocketError1 : ' + str(err)
					except socket.timeout, err :
						str_ = '[in getSharedData()] SocketError2 : ' + str(err)
					finally :
						self.sendErrorString(str_)
					size_ = maskSet[i][2]
					if size_ == 0 : size_ = 1
					emitter.nextfile.emit(size_)
		if self.s.getSharedFile('FINITA', sessionID).data != 'OK' :
			self.sendErrorString('Loading was completed incorrectly.')
		emitter.complete.emit()

	def sessionClose(self, sessionID = ''):
		try :
			str_ = ''
			self.s.sessionClose(sessionID)
		except ProtocolError, err :
			str_ = '[in sessionClose()] ProtocolErrorError : ' + str(err)
			"""print "[in sessionClose()] A protocol error occurred"
			print "URL: %s" % err.url
			print "HTTP/HTTPS headers: %s" % err.headers
			print "Error code: %d" % err.errcode
			print "Error message: %s" % err.errmsg"""
		except Fault, err :
			str_ = '[in sessionClose()] FaultError : ' + str(err)
			"""print "[in sessionClose()] A fault occurred"
			print "Fault code: %d" % err.faultCode
			print "Fault string: %s" % err.faultString"""
		except HTTPException, err :
			str_ = '[in sessionClose()] HTTPLibError : ' + str(err)
		except socket.error, err :
			str_ = '[in sessionClose()] SocketError1 : ' + str(err)
		except socket.timeout, err :
			str_ = '[in sessionClose()] SocketError2 : ' + str(err)
		finally :
			self.sendErrorString(str_)

	def _shutdown(self, str_= '', nothing = ''):
		#print 'socket closing...'
		if hasattr(self, 's') :
			try :
				self.s.socket.shutdown(socket.SHUT_RDWR)
			except socket.error, err :
				print '[in _shutdown()] SocketError1 : ', err
			except socket.timeout, err :
				print '[in _shutdown()] SocketError2 : ', err
			finally :
				self.s.socket.close()

if __name__ == '__main__':
	t = xr_client()
	t.run()
