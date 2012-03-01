# -*- coding: utf-8 -*-

from Functions import Path

class ModuleExist():
	def __init__(self, parent = None):
		self.AvahiAvailable = True

		try :
			if Path.platform in ('win', 'apl') : import pybonjour
			else : import avahi, dbus
		except ImportError , err :
			print '[in ModuleExist] ImportError: ', err
			self.AvahiAvailable = False
		except Exception , err :
			print '[in ModuleExist] InitiateError'
			self.AvahiAvailable = False
		finally : pass

ModuleExist = ModuleExist()
