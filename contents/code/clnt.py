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
			self.Obj.currentRemoteServerAddr = addr
			self.Obj.currentRemoteServerPort = port
			self.downLoadPath = unicode(InitConfigValue(self.Obj.Settings, 'DownLoadTo', Path.Temp))
			if not os.path.isdir(self.downLoadPath) : self.downLoadPath = Path.Temp
			#print '	run for get structure only '

	def run(self):
		try :
			self.s = SSLServerProxy(self.servaddr, self.TLS)
			# self.methods = self.s.system.listMethods()
		except socket.error, err :
			print 'SocetError : ', err
			if 'Obj' in dir(self) and self.Parent is None :
				self.Obj.errorString.emit(str(err))
			else :
				self.Parent.Obj.errorString.emit(str(err))
		except :
			err = 'UnknownError in init ServerProxy '
			print err
			if 'Obj' in dir(self) and self.Parent is None :
				self.Obj.errorString.emit(str(err))
			else :
				self.Parent.Obj.errorString.emit(str(err))

	def getSessionID(self, ownIP = ''):
		try :
			success = True
			# get session Id & server State
			self.randomFileName = Path.tempStruct(randomString(DIGITS_LENGTH))
			#print self.randomFileName, '   clnt random string'
			with open(self.randomFileName, "wb") as handle :
				try :
					handle.write(self.s.sessionID(ownIP).data)
				except AttributeError, err :
					print '[in getSessionID() AddressMissMatch]:', err
					return False
			self.listRandomString = DataRendering().fileToList(self.randomFileName)
			#print self.listRandomString, ' list of randomStrings'
			#print [self.listRandomString[0]]
			sessionID = self.listRandomString[1]
			#print sessionID, ' session ID'
			self.s.python_clean(self.listRandomString[0], sessionID)
			if os.path.exists(self.randomFileName) : os.remove(self.randomFileName)
			self.Parent.Obj.serverThread.Obj.currentSessionID[self.servaddr.split(':')[0]] = sessionID
			#print self.Parent.Obj.serverThread.Obj.currentSessionID , '\n^^^current Sessions'
			self.serverState = self.listRandomString[2]
			if len(self.listRandomString) > 3 :
				self.previousState = self.listRandomString[3]
			else :
				self.previousState = ''
			#print self.serverState, ' server State'
			if 'Obj' in dir(self) :
				self.Obj.currentRemoteServerState = self.serverState
				print "Handshake succeeded."
				""" caching avatar """
				#self.getAvatar()
		except socket.error, err :
			print '[in getSessionID()] SocketError : ', err
			success = False
			if 'Obj' in dir(self) and self.Parent is None :
				self.Obj.errorString.emit(str(err))
			else :
				self.Parent.Obj.errorString.emit(str(err))
		except ProtocolError, err :
			"""print "A protocol error occurred"
			print "URL: %s" % err.url
			print "HTTP/HTTPS headers: %s" % err.headers
			print "Error code: %d" % err.errcode
			print "Error message: %s" % err.errmsg"""
			success = False
			if 'Obj' in dir(self) and self.Parent is None :
				self.Obj.errorString.emit(str(err))
			else :
				self.Parent.Obj.errorString.emit(str(err))
		except Fault, err:
			"""print "A fault occurred"
			print "Fault code: %d" % err.faultCode
			print "Fault string: %s" % err.faultString"""
			success = False
			if 'Obj' in dir(self) and self.Parent is None :
				self.Obj.errorString.emit(str(err))
			else :
				self.Parent.Obj.errorString.emit(str(err))
		except HTTPException, err :
			print 'HTTPLibError : ', err
			success = False
			if 'Obj' in dir(self) and self.Parent is None :
				self.Obj.errorString.emit(str(err))
			else :
				self.Parent.Obj.errorString.emit(str(err))
		except IOError, err :
			print '[in getSessionID()] IOError : ', err
			success = False
			if 'Obj' in dir(self) and self.Parent is None :
				self.Obj.errorString.emit(str(err))
			else :
				self.Parent.Obj.errorString.emit(str(err))
		#finally :
		#	pass
		return success

	def getSharedSourceStructFile(self, sessionID = ''):
		# get Shared Sources Structure
		self.structFileName = Path.tempCache(self.serverState)
		#print self.structFileName, ' struct'
		try :
			with open(self.structFileName, "wb") as handle:
					try :
						handle.write(self.s.requestSharedSourceStruct(\
									'sharedSource_' + self.serverState, \
									sessionID).data)
					except AttributeError, err :
						print '[in getSharedSourceStructFile() SessionMismatch]:', err
					except ProtocolError, err :
						"""print "A protocol error occurred"
						print "URL: %s" % err.url
						print "HTTP/HTTPS headers: %s" % err.headers
						print "Error code: %d" % err.errcode
						print "Error message: %s" % err.errmsg"""
						self.Parent.Obj.errorString.emit(str(err))
					except Fault, err:
						"""print "A fault occurred"
						print "Fault code: %d" % err.faultCode
						print "Fault string: %s" % err.faultString"""
						self.Parent.Obj.errorString.emit(str(err))
					except socket.error, err :
						#print 'SocetError : ', err
						self.Parent.Obj.errorString.emit(str(err))
					finally :
						pass
		except IOError, err :
			print '[in getSharedSourceStructFile()] IOError : ', err
			if 'previousState' not in dir(self) : self.previousState = ''
		#finally : pass
		return self.structFileName, self.previousState

	def getAvatar(self, sessionID = ''):
		self.avatarFileName = Path.tempAvatar(self.serverState)
		#print self.avatarFileName, ' avatarFileName', sessionID
		try :
			with open(self.avatarFileName, "wb") as handle:
					try :
						handle.write(self.s.requestAvatar(sessionID).data)
					except AttributeError, err :
						print '[in getAvatar() SessionMismatch]:', err
					except ProtocolError, err :
						"""print "A protocol error occurred"
						print "URL: %s" % err.url
						print "HTTP/HTTPS headers: %s" % err.headers
						print "Error code: %d" % err.errcode
						print "Error message: %s" % err.errmsg"""
						#self.Parent.Obj.errorString.emit(str(err))
						pass
					except Fault, err:
						"""print "A fault occurred"
						print "Fault code: %d" % err.faultCode
						print "Fault string: %s" % err.faultString"""
						#self.Parent.Obj.errorString.emit(str(err))
						pass
					except socket.error, err :
						#print 'SocetError : ', err
						#self.Parent.Obj.errorString.emit(str(err))
						pass
					finally :
						pass
		except IOError, err :
			print '[in getAvatar()]IOError : ', err
			pass
		#finally : pass
		return self.avatarFileName

	def getSharedData(self, maskSet, downLoadPath, emitter, \
					  previousRemoteServerState = 'NOTHING', \
					  sessionID = ''):
		""" check remote server state """
		#print previousRemoteServerState, ' <state> ', self.serverState
		'''if previousRemoteServerState != self.serverState or previousRemoteServerState == '' :
			str_ = 'Status of the remote server has changed or not defined.\nUpdate his. Upload canceled.'
			self.Parent.errorString.emit(str_)
			emitter.complete.emit()
			return None'''
		if len(maskSet) == 0 :
			self.Parent.errorString.emit('Empty job. Upload canceled.')
			emitter.complete.emit()
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
						print '[in getSharedData()]IOError : ', err
						continue
				with open(_path, "wb") as handle:
					try :
						handle.write(self.s.python_file(str(i), sessionID).data)
						#print 'Downloaded : ', maskSet[i][1]
					except AttributeError, err :
						print '[in getSharedData() SessionMismatch]:', err
						emitter.complete.emit()
						self.Parent.errorString.emit('in getSharedData() SessionMismatch')
						return None
					except ProtocolError, err :
						"""print "A protocol error occurred"
						print "URL: %s" % err.url
						print "HTTP/HTTPS headers: %s" % err.headers
						print "Error code: %d" % err.errcode
						print "Error message: %s" % err.errmsg"""
						self.Parent.errorString.emit(str(err))
					except Fault, err:
						"""print "A fault occurred"
						print "Fault code: %d" % err.faultCode
						print "Fault string: %s" % err.faultString"""
						self.Parent.errorString.emit(str(err))
					finally :
						pass
					size_ = maskSet[i][2]
					if size_ == 0 : size_ = 1
					emitter.nextfile.emit(size_)
		emitter.complete.emit()

	def sessionClose(self, sessionID = ''):
		try :
			self.s.sessionClose(sessionID)
		except ProtocolError, err :
			"""print "A protocol error occurred"
			print "URL: %s" % err.url
			print "HTTP/HTTPS headers: %s" % err.headers
			print "Error code: %d" % err.errcode
			print "Error message: %s" % err.errmsg"""
			if 'Obj' in dir(self) and self.Parent is None :
				self.Obj.errorString.emit(str(err))
			else :
				self.Parent.errorString.emit(str(err))
		except Fault, err:
			"""print "A fault occurred"
			print "Fault code: %d" % err.faultCode
			print "Fault string: %s" % err.faultString"""
			if 'Obj' in dir(self) and self.Parent is None :
				self.Obj.errorString.emit(str(err))
			else :
				self.Parent.errorString.emit(str(err))
		except HTTPException, err :
			print 'HTTPLibError : ', err
			if 'Obj' in dir(self) and self.Parent is None :
				self.Obj.errorString.emit(str(err))
			else :
				self.Parent.errorString.emit(str(err))
		except socket.error, err :
			print 'SocetError : ', err
			if 'Obj' in dir(self) and self.Parent is None :
				self.Obj.errorString.emit(str(err))
			else :
				self.Parent.errorString.emit(str(err))

	def _shutdown(self, str_= ''):
		#print 'socket closing...'
		if hasattr(self, 's') :
			try :
				self.s.socket.shutdown(socket.SHUT_RDWR)
			except socket.error, err :
				print '[in getSessionID()] SocketError : ', err
			finally :
				self.s.socket.close()

if __name__ == '__main__':
	t = xr_client()
	t.run()
