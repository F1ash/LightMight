# -*- coding: utf-8 -*-

from PyQt4.QtCore import pyqtSlot
from PyQt4.QtGui import QListWidgetItem

class Policy():
	def __init__(self, parent = None):
		self.Parent = parent
		self.Policy = enumerate(('Allowed', 'Confirm', 'Blocked'))
		self.Allowed = 0	# allow avatar, structFile, shared sources;
		self.Confirm = 1	# allow avatar, structFile;
							# getting of shared sources must to confirm
		self.Blocked = 2	# allow avatar only
		self.Current = 1

	@pyqtSlot(QListWidgetItem)
	@pyqtSlot(str)
	def getPolicy(self, item):
		return 'policy'

	@pyqtSlot(QListWidgetItem, int)
	@pyqtSlot(str, int)
	def setPolicy(self, item, policy):
		return 'accepted'
