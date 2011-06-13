# -*- coding: utf-8 -*-

from xmlrpclib import ServerProxy, ProtocolError, Fault
from httplib import HTTPException
from Functions import *
import os, os.path, string, socket

class xr_client:
	def __init__(self, addr = 'http://localhost', port = '34100', obj = None, parent = None):
		self.servaddr = 'http://' + addr + ':' + port
		self.serverState = ''
		self.Parent = parent
		print self.servaddr, ' clnt '
		if obj is not None :
			self.Obj = obj
			self.Obj.currentRemoteServerAddr = addr
			self.Obj.currentRemoteServerPort = port
			self.downLoadPath = unicode(InitConfigValue(self.Obj.Settings, 'DownLoadTo', '/tmp'))

	def run(self):
		try :
			self.s = ServerProxy(self.servaddr)

			# self.methods = self.s.system.listMethods()
			# get session Id & server State
			self.randomFileName = str('/dev/shm/LightMight/' + randomString(24))
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
			if 'Obj' in dir(self) :
				self.Obj.currentRemoteServerState = self.serverState
				print "Handshake succeeded."
		except ProtocolError, err :
			print "A protocol error occurred"
			print "URL: %s" % err.url
			print "HTTP/HTTPS headers: %s" % err.headers
			print "Error code: %d" % err.errcode
			print "Error message: %s" % err.errmsg
			if 'Obj' in dir(self) and parent is None :
				self.Obj.errorString.emit(str(err))
			else :
				self.Parent.errorString.emit(str(err))
		except Fault, err:
			"""print "A fault occurred"
			print "Fault code: %d" % err.faultCode
			print "Fault string: %s" % err.faultString"""
			if 'Obj' in dir(self) and parent is None :
				self.Obj.errorString.emit(str(err))
			else :
				self.Parent.errorString.emit(str(err))
		except HTTPException, err :
			print 'HTTPLibError : ', err
			if 'Obj' in dir(self) and parent is None :
				self.Obj.errorString.emit(str(err))
			else :
				self.Parent.errorString.emit(str(err))
		except socket.error, err :
			print 'SocetError : ', err
			if 'Obj' in dir(self) and parent is None :
				self.Obj.errorString.emit(str(err))
			else :
				self.Parent.errorString.emit(str(err))
		finally :
			pass

	def getSharedSourceStructFile(self):
		# get Shared Sources Structure
		self.structFileName = str('/dev/shm/LightMight/client/struct_' + self.serverState) ## self.sessionID)
		print self.structFileName, ' struct'
		with open(self.structFileName, "wb") as handle:
			handle.write(self.s.requestSharedSourceStruct('sharedSource_' + self.serverState).data)
		return self.structFileName

	def getSharedData(self, maskSet, downLoadPath, emitter, previousRemoteServerState = 'NOTHING'):
		""" check remote server state """
		print previousRemoteServerState, ' <state> ', self.serverState
		if previousRemoteServerState != self.serverState or previousRemoteServerState == '' :
			str_ = 'Status of the remote server has changed or not defined.\nUpdate his. Upload canceled.'
			self.Parent.errorString.emit(str_)
			emitter.complete.emit()
			return None
		if len(maskSet) == 0 :
			self.Parent.errorString.emit('Empty job. Upload canceled.')
			emitter.complete.emit()
			return None
		for i in maskSet.iterkeys() :
			if maskSet[i][0] == 1 :
				_path = downLoadPath + maskSet[i][1]
				path = os.path.dirname(_path)
				#print _path, i, ' clnt'
				if not os.path.exists(path) :
					os.makedirs(path)
				with open(_path, "wb") as handle:
					try :
						handle.write(self.s.python_file(str(i)).data)
						#print 'Downloaded : ', maskSet[i][1]
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

	def _shutdown(self):
		#self.shutdown()		# method not exist
		pass

if __name__ == '__main__':
	t = xr_client()
	t.run()
