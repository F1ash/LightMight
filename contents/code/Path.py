#!/usr/bin/python 
# -*- coding: utf-8 -*-

import os.path, sys

class PathClass():
	def __init__(self):

		if sys.platform == 'win32' :
			print 'Platform : Win'
			self.platform = "win"
			self.tempPrefix = os.path.join(unicode(os.path.dirname(os.tempnam())))
			self.Temp = self.tempPrefix
		else :
			if sys.platform == 'darwin' :
				self.platform = "apl"
				print 'Platform : Apple'
				self.tempPrefix = os.path.join(unicode(os.path.dirname(os.tempnam())))
				self.Temp = self.tempPrefix
			else :
				print 'Platform : Linux'
				self.platform = "lin"
				self.tempPrefix = os.path.join('/dev', 'shm')
				self.Temp = '/tmp'
		self.TempStruct = os.path.join(self.tempPrefix, 'LightMight')
		self.TempCache = os.path.join(self.TempStruct, 'cache')
		self.TempAvatar = os.path.join(self.TempCache, 'avatars')
		self.Config = os.path.join(os.path.expanduser('~'), '.config', 'LightMight')
		self.Cache = os.path.join(os.path.expanduser('~'), '.cache', 'LightMight')
		self.Avatar = os.path.join(self.Cache, 'avatars')
		self.methodType = type(self.tempAvatar)

	def tempStruct(self, name = ''):
		return os.path.join(self.TempStruct, unicode(name))

	def tempCache(self, name = ''):
		return os.path.join(self.TempCache, unicode(name))

	def tempAvatar(self, name = ''):
		return os.path.join(self.TempAvatar, unicode(name))

	def config(self, name = ''):
		return os.path.join(self.Config, unicode(name))

	def cache(self, name = ''):
		return os.path.join(self.Cache, unicode(name))

	def avatar(self, name = ''):
		return os.path.join(self.Avatar, unicode(name))

	def multiPath(self, arg, name1 = '', name2 = ''):
		if isinstance(arg, self.methodType) :
			return os.path.join(arg(name1), unicode(name2))
		return ''

Path = PathClass()

