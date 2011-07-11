# -*- coding: utf-8 -*-

from PyQt4.QtCore import QThread, QTimer, pyqtSignal
from Functions import InitConfigValue, pathPrefix
from clnt import xr_client

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
		for itemValue in self.USERS.iteritems() :
			if not itemValue[1][5] and self.Key :
				""" call for fill clients data """
				if itemValue[1][3] == 'Yes' :
					value = True
				else :
					value = False
				clnt = xr_client(addr = unicode(itemValue[1][1]), \
								 port = unicode(itemValue[1][2]), \
								 parent = self, \
								 TLS = value)
				clnt.run()
				clnt.getAvatar()
				clnt.getSharedSourceStructFile(True)
				self.USERS[itemValue[0]] = (itemValue[1][0], \
											itemValue[1][1], \
											itemValue[1][2], \
											itemValue[1][3], \
											itemValue[1][4], \
											True)
				#print 'work accomplished'
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
		self.timer.stop()
		self.Key = False
		pass
