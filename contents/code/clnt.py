# -*- coding: utf-8 -*-

from xmlrpclib import ServerProxy
from Functions import *
import os, os.path, string

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
		self.s = ServerProxy(self.servaddr)

		self.methods = self.s.system.listMethods()
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

	def getSharedSourceStructFile(self):
		# get Shared Sources Structure
		self.structFileName = str('/dev/shm/LightMight/client/struct_' + self.serverState) ## self.sessionID)
		print self.structFileName, ' struct'
		with open(self.structFileName, "wb") as handle:
			handle.write(self.s.requestSharedSourceStruct('sharedSource_' + self.serverState).data)
		return self.structFileName

	def getSharedData(self, maskSet, downLoadPath, emitter):
		i = 0
		while i < len(maskSet) :
			if maskSet[i][0] == '1' :
				path = os.path.dirname(downLoadPath + maskSet[i][1])
				#print path, i
				if not os.path.exists(path) :
					os.makedirs(path)
				with open(downLoadPath + maskSet[i][1], "wb") as handle:
					handle.write(self.s.python_file(str(i)).data)
				#print 'Downloaded : ', name
				emitter.nextfile.emit(int(maskSet[i][2]))
			i += 1

	def _shutdown(self):
		#self.shutdown()		# method not exist
		pass

if __name__ == '__main__':
	t = xr_client()
	t.run()
