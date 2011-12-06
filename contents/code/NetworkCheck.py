# -*- coding: utf-8 -*-

from PyQt4.QtCore import QThread
from Functions import getIP

class NetworkCheck(QThread):
	def __init__(self, parent = None):
		QThread.__init__(self, parent)
		self.Parent = parent

	def run(self):
		ip, msg, netState = getIP()
		self.Parent.netState.emit(ip, msg, netState)
