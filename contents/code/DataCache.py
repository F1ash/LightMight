# -*- coding: utf-8 -*-

from PyQt4.QtCore import QThread, QTimer, pyqtSignal, Qt
from PyQt4.QtGui import QIcon
from Functions import InitConfigValue, pathPrefix, DelFromCache, InCache, moveFile
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
		self.timer.timeout.connect(self.initRefill)

	def run(self):
		self.setPriority(QThread.LowPriority)
		self.timer.start(10000)

	def initRefill(self):
		if self.runState : return None
		self.runState = True
		self.Key = True
		self.prefPath = pathPrefix()
		for itemValue in self.USERS.iteritems() :
			if not itemValue[1][5] and self.Key :
				""" call for fill clients data """
				if itemValue[1][3] == 'Yes' :
					value = True
				else :
					value = False
				print 'caching:', unicode(itemValue[1][1]), unicode(itemValue[1][2]), value
				clnt = xr_client(addr = unicode(itemValue[1][1]), \
								 port = unicode(itemValue[1][2]), \
								 parent = self, \
								 TLS = value)
				pathExist = InCache(itemValue[1][4])
				names = ('', '')
				if pathExist[0] :
					""" if data cached """
					head, tail = os.path.split(str(pathExist[1]))
					if not moveFile(pathExist[1], \
									self.prefPath + '/dev/shm/LightMight/cache/' + tail, \
									False) :
						clnt.run()
						names = clnt.getSharedSourceStructFile(True)
						#print 'download struct'
						if not moveFile(head + '/avatars/' + tail, \
										self.prefPath + '/dev/shm/LightMight/cache/avatars/' + tail, \
										False) :
							clnt.getAvatar()
							#print ' download avatar'
					elif not moveFile(head + '/avatars/' + tail, \
									self.prefPath + '/dev/shm/LightMight/cache/avatars/' + tail, \
									False) :
						clnt.run()
						clnt.getAvatar()
						#print ' download avatar only'
				else :
					""" if data not cached """
					clnt.run()
					clnt.getAvatar()
					names = clnt.getSharedSourceStructFile(True)
				""" if remoteServerState is changed """
				#print names
				if names[1] != '' : DelFromCache(names[1])
				self.USERS[itemValue[0]] = (itemValue[1][0], \
											itemValue[1][1], \
											itemValue[1][2], \
											itemValue[1][3], \
											itemValue[1][4], \
											True)
				item = None; count = self.Obj.menuTab.userList.count()
				for i in xrange(count) :
					item_ = self.Obj.menuTab.userList.item(i)
					if str(item_.data(Qt.AccessibleTextRole).toString()) == \
								 str(itemValue[1][1] + ':' + itemValue[1][2]) :
						item = item_
						break
				#print item, '&&'
				if item is not None :
					item.setIcon(QIcon(self.prefPath + '/dev/shm/LightMight/cache/avatars/' + itemValue[1][4]))
			elif self.Key is False :
				self.runState = False
				break
		self.runState = False

	def refillCache(self, str_ = u''):
		print 'signal about newItem :', str_
		if self.runState is False :
			""" fill cache for new clients data """
			pass

	def _shutdown(self):
		self.timer.timeout.disconnect(self.initRefill)
		self.timer.stop()
		self.Key = False
		pass
