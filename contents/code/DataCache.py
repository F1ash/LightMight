# -*- coding: utf-8 -*-

from PyQt4.QtCore import QThread, QTimer, pyqtSignal, Qt
from PyQt4.QtGui import QIcon
from Functions import InitConfigValue, Path, DelFromCache, InCache, avatarInCache, moveFile
from clnt import xr_client
import os.path

class DataCache(QThread):
	newItem = pyqtSignal(unicode)
	def __init__(self, userList = {}, parent = None):
		QThread.__init__(self, parent)

		self.Obj = parent
		self.runState = False
		self.USERS = userList
		self.newItem.connect(self.refillCache)
		self.timer = QTimer()
		self.timer.setInterval(30000)
		self.timer.timeout.connect(self.initRefill)
		self.timer.start()

	def run(self):
		self.setPriority(QThread.LowPriority)
		#print self.timer.isActive()

	def initRefill(self):
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
					self.clnt.run()
					if not hasattr(self.clnt, 'runned') or not self.clnt.runned :
						self.clnt._shutdown()
						continue
					# get session ID if don`t it
					#print self.Obj.serverThread.Obj.currentSessionID, '\n', currAddr, 'Runned:', runned
					if currAddr not in self.Obj.serverThread.Obj.currentSessionID :
						self.clnt.getSessionID(self.Obj.server_addr)
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
					sessionID = self.Obj.serverThread.Obj.currentSessionID[currAddr][0]
					pathExist = avatarInCache(self.clnt.serverState)
					possibleAvatarTempPath = Path.tempAvatar(self.clnt.serverState)
					avatarTempOut = not os.path.isfile(possibleAvatarTempPath)
					avatarLoad = False
					#print 'avatarTempOut', avatarTempOut, ':', possibleAvatarTempPath
					if avatarTempOut and pathExist[0] :
						if not moveFile(pathExist[1], \
										possibleAvatarTempPath, \
										False) :
							loadAvatarPath = self.clnt.getAvatar(sessionID)
						avatarLoad = True
					elif avatarTempOut :
						loadAvatarPath = self.clnt.getAvatar(sessionID)
						avatarLoad = True
					#print 'avatarLoad', avatarLoad
					if avatarLoad and os.path.isfile(possibleAvatarTempPath) :
						count = self.Obj.menuTab.userList.count()
						for i in xrange(count) :
							item_ = self.Obj.menuTab.userList.item(i)
							if str(item_.data(Qt.AccessibleTextRole).toList()[0].toString()) == \
										str(itemValue[1][1] + ':' + itemValue[1][2]) :
								self.Obj.menuTab.setAvatar.emit(item_, itemValue[1][4])
					pathExist = InCache(self.clnt.serverState)
					res = ('', False)
					if pathExist[0] :
						if not moveFile(pathExist[1], \
										Path.tempCache(self.clnt.serverState), \
										False) :
							res = self.clnt.getSharedSourceStructFile(sessionID)
					else : res = self.clnt.getSharedSourceStructFile(sessionID)
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
		self.runState = False
		#print 'caching down'

	def refillCache(self, str_ = u''):
		#print 'signal about newItem :', str_
		if self.runState is False :
			""" fill cache for new clients data """
			pass

	def _shutdown(self):
		self.timer.timeout.disconnect(self.initRefill)
		self.newItem.disconnect(self.refillCache)
		self.timer.stop()
		self.Key = False
		if hasattr(self, 'clnt') : self.clnt._shutdown()
		self.Obj.cacheDown.emit()
