# -*- coding: utf-8 -*-

from PyQt4.QtCore import QThread, QTimer, pyqtSignal, Qt
from PyQt4.QtGui import QIcon
from Functions import InitConfigValue, Path, DelFromCache, InCache, moveFile
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
		if Path.platform != 'win' :
			self.timer = QTimer()
			self.timer.setInterval(10000)
			self.timer.timeout.connect(self.initRefill)

	def run(self):
		self.setPriority(QThread.LowPriority)
		if Path.platform == 'win' :
			self.timer = QTimer()
			self.timer.setInterval(10000)
			self.timer.timeout.connect(self.initRefill)
		self.timer.start()

	def initRefill(self):
		if self.runState : print 'caching...'; return None
		self.runState = True
		self.Key = True
		for itemValue in self.USERS.iteritems() :
			#print itemValue, '-- current item in USERS for caching'
			if self.Key and not itemValue[1][5] :
				""" call for fill clients data """
				if itemValue[1][3] == 'Yes' :
					value = True
				else :
					value = False
				#print 'caching:', unicode(itemValue[1][1]), unicode(itemValue[1][2]), value, '--', itemValue[0]
				currAddr = unicode(itemValue[1][1])
				if hasattr(self, 'clnt') : self.clnt = None
				self.clnt = xr_client(addr = currAddr, \
								 port = unicode(itemValue[1][2]), \
								 parent = self, \
								 TLS = value)
				self.clnt.run()
				# get session ID if don`t it
				#print self.Obj.serverThread.Obj.currentSessionID, '\n', currAddr
				if currAddr not in self.Obj.serverThread.Obj.currentSessionID :
					self.clnt.getSessionID(self.Obj.server_addr)
				if currAddr not in self.Obj.serverThread.Obj.currentSessionID :
					self.USERS[itemValue[0]] = (itemValue[1][0], \
												itemValue[1][1], \
												itemValue[1][2], \
												itemValue[1][3], \
												'error', \
												True)
					self.Obj.menuTab.searchItem(itemValue[0])
					continue
				pathExist = InCache(itemValue[1][4])
				names = ('', '')
				sessionID = self.Obj.serverThread.Obj.currentSessionID[currAddr]
				if pathExist[0] :
					#print pathExist, 'in CacheData, inCache'
					""" if data cached """
					head, tail = os.path.split(str(pathExist[1]))
					if not moveFile(pathExist[1], \
									Path.tempCache(tail), \
									False) :
						#self.clnt.run()
						names = self.clnt.getSharedSourceStructFile(sessionID)
						#print 'download struct'
						if not moveFile(os.path.join(head, 'avatars', tail), \
										Path.tempAvatar(tail), \
										False) :
							self.clnt.getAvatar(sessionID)
							#print ' download avatar'
					elif not moveFile(os.path.join(head, 'avatars', tail), \
									Path.tempAvatar(tail), \
									False) :
						#self.clnt.run()
						self.clnt.getAvatar(sessionID)
						#print ' download avatar only'
				else :
					""" if data not cached """
					#print pathExist, 'in CacheData, not inCache'
					#self.clnt.run()
					self.clnt.getAvatar(sessionID)
					names = self.clnt.getSharedSourceStructFile(sessionID)
					#print 'download all'
				""" if remoteServerState is changed """
				#print names, itemValue[0]
				if names[1] != '' : DelFromCache(names[1])
				if itemValue[0] in self.USERS :
					self.USERS[itemValue[0]] = (itemValue[1][0], \
												itemValue[1][1], \
												itemValue[1][2], \
												itemValue[1][3], \
												itemValue[1][4], \
												True)
					count = self.Obj.menuTab.userList.count()
					for i in xrange(count) :
						item_ = self.Obj.menuTab.userList.item(i)
						if str(item_.data(Qt.AccessibleTextRole).toList()[0].toString()) == \
									str(itemValue[1][1] + ':' + itemValue[1][2]) :
							self.Obj.menuTab.setAvatar.emit(item_, itemValue[1][4])
			elif self.Key is False :
				#print 'cache key is locked...'
				break
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
