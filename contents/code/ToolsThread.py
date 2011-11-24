# -*- coding: utf-8 -*-

from PyQt4.QtCore import QThread, SIGNAL, pyqtSignal, QSettings
from Functions import InitConfigValue, Path, avatarInCache

class ToolsThread(QThread):
	""" custom signals for DownLoadClient """
	nextfile = pyqtSignal(int)
	complete = pyqtSignal()
	def __init__(self, obj = None, maskSet = None, parent = None):
		QThread.__init__(self, parent)

		self.Obj = obj
		self.Parent = parent
		self.maskSet = maskSet
		self.flag = ''

	def run(self):
		self.Obj.run()
		self.emit(SIGNAL('threadRunning'), self.Parent)
		if self.flag == 'cache_now' :
			self.cache_now()

	def getSharedSourceStructFile(self, str_ = ''):
		return self.Obj.getSharedSourceStructFile(str_)

	def getSharedData(self):
		downLoadPath = unicode(InitConfigValue(QSettings('LightMight','LightMight'), \
											'DownLoadTo', Path.Temp))
		self.Obj.getSharedData(self.maskSet, downLoadPath, \
							   self, self.Parent.currentRemoteServerState, \
							   self.Parent.sessionID)

	def cache_now(self):
		addr = self.Obj.servaddr
		key = str(addr.split(':')[0])
		# get session ID if don`t it
		if key not in self.Parent.Obj.serverThread.Obj.currentSessionID :
			self.Obj.getSessionID(self.Parent.Obj.server_addr)
		if key in self.Parent.Obj.serverThread.Obj.currentSessionID :
			sessionID = self.Parent.Obj.serverThread.Obj.currentSessionID[key][0]
		else :
			sessionID = ''
		if not avatarInCache(self.Parent.Obj.USERS[addr][4])[0] : self.Obj.getAvatar(sessionID)
		path, error = self.getSharedSourceStructFile(sessionID)
		self.Parent.cachedData.emit(path, error)

	def _terminate(self, str_ = '', loadFile = ''):
		self.Obj._shutdown(str_, loadFile)
