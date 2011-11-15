# -*- coding: utf-8 -*-

from PyQt4.QtCore import QThread, SIGNAL, pyqtSignal, QSettings
from Functions import InitConfigValue, Path

class ToolsThread(QThread):
	""" custom signals for DownLoadClient """
	nextfile = pyqtSignal(int)
	complete = pyqtSignal()
	def __init__(self, obj = None, maskSet = None, parent = None):
		QThread.__init__(self, parent)

		self.Obj = obj
		self.Parent = parent
		self.maskSet = maskSet

	def run(self):
		self.Obj.run()
		self.emit(SIGNAL('threadRunning'), self.Parent)

	def getSharedSourceStructFile(self, str_ = ''):
		return self.Obj.getSharedSourceStructFile(str_)

	def getSharedData(self):
		downLoadPath = unicode(InitConfigValue(QSettings('LightMight','LightMight'), \
											'DownLoadTo', Path.Temp))
		self.Obj.getSharedData(self.maskSet, downLoadPath, \
							   self, self.Parent.currentRemoteServerState, \
							   self.Parent.sessionID)

	def _terminate(self, str_ = '', loadFile = ''):
		self.Obj._shutdown(str_, loadFile)
