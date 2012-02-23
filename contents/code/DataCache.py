# -*- coding: utf-8 -*-

from PyQt4.QtCore import QThread, pyqtSignal, Qt
from PyQt4.QtGui import QIcon
from Functions import *
from clnt import xr_client
import os.path, threading

class DataCache(QThread):
	newItem = pyqtSignal(unicode)
	def __init__(self, userList = {}, parent = None):
		QThread.__init__(self, parent)

		self.Obj = parent
		self.runState = False
		self.USERS = userList

	def run(self):
		self.setPriority(QThread.LowPriority)
		self.Key = True
		while self.Key :
			t = threading.Thread(target = self.initRefill)
			t.start()
			self.msleep(30000)

	def initRefill(self):
		#print 'new cache loop'
		if self.runState : print 'caching...'; return None
		self.runState = True
		self.Key = True
		for itemValue in self.USERS.iteritems() :
			try :
				#print itemValue, '-- current item in USERS for caching'
				if self.Key and not itemValue[1][5] :
					""" call for fill clients data """
					if itemValue[1][3] == 'Yes' :
						value = True
					else :
						value = False
					#print 'caching:', unicode(itemValue[1][1]), unicode(itemValue[1][2]), value, '--', itemValue[0]
					currAddr = unicode(itemValue[1][1])
					if hasattr(self, 'clnt') : del self.clnt; self.clnt = None
					self.clnt = xr_client(addr = currAddr, \
									port = unicode(itemValue[1][2]), \
									parent = self, \
									TLS = value)
					self.clnt.serverState = itemValue[1][4]
					#print itemValue[1][4], 'remote server state'
					if self.Key : self.clnt.run()
					else :
						self.clnt._shutdown()
						break
					if not hasattr(self.clnt, 'runned') or not self.clnt.runned :
						self.clnt._shutdown()
						continue
					# get session ID if don`t it
					#print self.Obj.serverThread.Obj.currentSessionID, '\n', currAddr, 'Runned:', runned
					if self.Key and hasattr(self.Obj, 'serverThread') and self.Obj.serverThread is not None \
								and currAddr not in self.Obj.serverThread.Obj.currentSessionID :
						self.clnt.getSessionID(self.Obj.server_addr)
					else :
						self.clnt._shutdown()
						break
					if currAddr not in self.Obj.serverThread.Obj.currentSessionID :
						''' brocken contact '''
						self.USERS[itemValue[0]] = (itemValue[1][0], \
													itemValue[1][1], \
													itemValue[1][2], \
													itemValue[1][3], \
													'error', \
													True)
						self.Obj.menuTab.searchItem(itemValue[0])
						self.clnt._shutdown()
						continue
					sessionID_ = self.Obj.serverThread.Obj.currentSessionID[currAddr][0]
					_keyHash = self.Obj.serverThread.Obj.currentSessionID[currAddr][3]
					sessionID = createEncryptedSessionID(sessionID_, _keyHash)
					pathExist = avatarInCache(self.clnt.serverState)
					possibleAvatarTempPath = Path.tempAvatar(self.clnt.serverState)
					avatarTempOut = not os.path.isfile(possibleAvatarTempPath)
					avatarLoad = False
					#print 'avatarTempOut', avatarTempOut, ':', possibleAvatarTempPath
					if self.Key and avatarTempOut and pathExist[0] :
						if not moveFile(pathExist[1], \
										possibleAvatarTempPath, \
										False) :
							loadAvatarPath = self.clnt.getAvatar(sessionID)
						avatarLoad = True
					elif self.Key and avatarTempOut :
						loadAvatarPath = self.clnt.getAvatar(sessionID)
						avatarLoad = True
					else :
						self.clnt._shutdown()
						break
					#print 'avatarLoad', avatarLoad
					if avatarLoad and os.path.isfile(possibleAvatarTempPath) :
						count = self.Obj.menuTab.userList.count()
						for i in xrange(count) :
							item_ = self.Obj.menuTab.userList.item(i)
							if str(item_.data(Qt.AccessibleTextRole).toList()[0].toString()) == \
										str(itemValue[1][1] + ':' + itemValue[1][2]) :
								if self.Key :
									self.Obj.menuTab.setAvatar.emit(item_, itemValue[1][4])
								else : break
					pathExist = InCache(self.clnt.serverState)
					res = ('', False)
					if self.Key and pathExist[0] :
						if not moveFile(pathExist[1], \
										Path.tempCache(self.clnt.serverState), \
										False) :
							res = self.clnt.getSharedSourceStructFile(sessionID)
					elif self.Key : res = self.clnt.getSharedSourceStructFile(sessionID)
					else :
						self.clnt._shutdown()
						break
					#print res, itemValue[0], 'res'
					if res[1] : cached = False
					else : cached = True
					if itemValue[0] in self.USERS :
						self.USERS[itemValue[0]] = (itemValue[1][0], \
													itemValue[1][1], \
													itemValue[1][2], \
													itemValue[1][3], \
													itemValue[1][4], \
													cached)
					self.clnt._shutdown()
				elif self.Key is False :
					#print 'cache key is locked...'
					break
			except RuntimeError, err :
				print '[in initRefill() DataCache]:', err
				continue
			finally : pass
		self.runState = False
		#print 'caching down'

	def _shutdown(self):
		self.Key = False
		if hasattr(self, 'clnt') : self.clnt._shutdown()
		self.Obj.cacheDown.emit()
