# -*- coding: utf-8 -*-

from xmlrpclib import ServerProxy, ProtocolError, Fault
from httplib import HTTPException
from Functions import *
from ui.ListingText import ListingText
import os, os.path, string, socket

class xr_client:
	def __init__(self, addr = 'http://localhost', port = '34100', obj = None):
		self.servaddr = 'http://' + addr + ':' + port
		print self.servaddr
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
		except ProtocolError, err :
			print "A protocol error occurred"
			print "URL: %s" % err.url
			print "HTTP/HTTPS headers: %s" % err.headers
			print "Error code: %d" % err.errcode
			print "Error message: %s" % err.errmsg
			self.showMSG(err)
		except Fault, err:
			"""print "A fault occurred"
			print "Fault code: %d" % err.faultCode
			print "Fault string: %s" % err.faultString"""
			self.showMSG(err)
		except HTTPException, err :
			print 'HTTPLibError : ', err
			self.showMSG(err)
		except socket.error, err :
			print 'SocetError : ', err
			self.showMSG(err)
		finally :
			pass

	def getSharedSourceStructFile(self):
		# get Shared Sources Structure
		self.structFileName = str('/dev/shm/LightMight/client/struct_' + self.serverState) ## self.sessionID)
		print self.structFileName, ' struct'
		with open(self.structFileName, "wb") as handle:
			handle.write(self.s.requestSharedSourceStruct('sharedSource_' + self.serverState).data)
		return self.structFileName

	def getSharedData(self, maskSet, downLoadPath, emitter):
		for i in maskSet.iterkeys() :
			if maskSet[i][0] == '1' :
				path = os.path.dirname(downLoadPath + maskSet[i][1])
				print downLoadPath + maskSet[i][1], i, ' clnt'
				if not os.path.exists(path) :
					os.makedirs(path)
				try :
					with open(downLoadPath + maskSet[i][1], "wb") as handle:
						handle.write(self.s.python_file(str(i)).data)
						#print 'Downloaded : ', maskSet[i][1]
						size_ = int(maskSet[i][2])
						if size_ == 0 : size_ = 1
						emitter.nextfile.emit(size_)
				except ProtocolError, err :
					"""print "A protocol error occurred"
					print "URL: %s" % err.url
					print "HTTP/HTTPS headers: %s" % err.headers
					print "Error code: %d" % err.errcode
					print "Error message: %s" % err.errmsg"""
					self.showMSG(err)
				except Fault, err:
					"""print "A fault occurred"
					print "Fault code: %d" % err.faultCode
					print "Fault string: %s" % err.faultString"""
					self.showMSG(err)
				finally :
					pass
		emitter.complete.emit()

	def showMSG(self, str_):
		showHelp = ListingText("MSG: " + str(str_))
		showHelp.exec_()

	def _shutdown(self):
		#self.shutdown()		# method not exist
		pass

if __name__ == '__main__':
	t = xr_client()
	t.run()
