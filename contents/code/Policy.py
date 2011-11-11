# -*- coding: utf-8 -*-

from PyQt4.QtCore import pyqtSlot
from Functions import InitConfigValue

class Policy():
	def __init__(self, parent = None):
		self.Parent = parent
		self.PolicyName = ('Allowed', 'Confirm', 'Blocked')
		self.Allowed = 0	# allow avatar, structFile, shared sources;
		self.Confirm = 1	# allow avatar, structFile;
							# getting of shared sources must to confirm
		self.Blocked = 2	# allow avatar only
		self.Current = self.PolicyName.index(InitConfigValue(self.Parent.Settings, 'CommonPolicy', 'Blocked'))

	def setPolicy(self, policyName):
		try :
			self.Current = self.PolicyName.index(policyName)
			self.Parent.Settings.setValue('CommonPolicy', policyName)
			return True
		except ValueError, err :
			print err
			return False
