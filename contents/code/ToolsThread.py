# -*- coding: utf-8 -*-

from PyQt4.QtCore import QThread, SIGNAL, pyqtSignal, QSettings
from Functions import *

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
		self.runned = self.Obj.runned
		''' NB : self.runned sets before the emit signal
				 for correct checking of the client start
		'''
		self.emit(SIGNAL('threadRunning'), self.Parent)
		if self.runned and self.flag == 'cache_now' :
			self.cache_now()

	def getSharedSourceStructFile(self, str_ = ''):
		return self.Obj.getSharedSourceStructFile(str_)

	def getSharedData(self):
		downLoadPath = unicode(InitConfigValue(QSettings('LightMight','LightMight'), \
											'DownLoadTo', Path.Temp))
		sessionID_ = self.Parent.sessionID
		_keyHash = self.Parent.pubKeyHash
		sessionID = createEncryptedSessionID(sessionID_, _keyHash)
		access = self.Obj.getAccess(sessionID, self.Parent.currentRemoteServerState)
		if access == SESSION_MISMATCH :
			self.Parent.errorString.emit('Session ID mismatched.\nRepeat, please.')
		elif access == SERVER_STATE_MISMATCH :
			self.Parent.errorString.emit('Server State mismatched.\nReinit self, please.')
		elif access < 0 :
			self.Parent.errorString.emit('Connect failed.\nRepeat, please.')
		else :
			if self.Obj.getSharedData(self.maskSet, downLoadPath, self, sessionID) :
				self.Parent.errorString.emit('Success.')
			else : self.Parent.errorString.emit('There are some problems in job.')
		self.complete.emit()

	def cache_now(self):
		addr = self.Obj.servaddr
		key = str(addr.split(':')[0])
		# get session ID if don`t it
		if hasattr(self.Parent.Obj, 'serverThread') and self.Parent.Obj.serverThread is not None \
				and key not in self.Parent.Obj.serverThread.Obj.currentSessionID :
			self.Obj.getSessionID(self.Parent.Obj.server_addr)
		if hasattr(self.Parent.Obj, 'serverThread') and self.Parent.Obj.serverThread is not None \
				and key in self.Parent.Obj.serverThread.Obj.currentSessionID :
			sessionID_ = self.Parent.Obj.serverThread.Obj.currentSessionID[key][0]
			_keyHash = self.Parent.Obj.serverThread.Obj.currentSessionID[key][3]
			sessionID = createEncryptedSessionID(sessionID_, _keyHash)
		else :
			sessionID = ''
		if addr in self.Parent.Obj.USERS and not avatarInCache(self.Parent.Obj.USERS[addr][4])[0] :
			self.Obj.getAvatar(sessionID)
		path, error = self.getSharedSourceStructFile(sessionID)
		self.Parent.cachedData.emit(path, error)

	def _terminate(self, str_ = '', loadFile = ''):
		self.Obj._shutdown(str_, loadFile)
