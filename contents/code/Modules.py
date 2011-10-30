# -*- coding: utf-8 -*-

from Functions import Path

class ModuleExist():
	def __init__(self, parent = None):
		self.AvahiAvailable = True

		try :
			if Path.platform == 'win' : import pybonjour
			else : import avahi, dbus
		except :
			self.AvahiAvailable = False
		finally : pass

ModuleExist = ModuleExist()