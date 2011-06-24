# -*- coding: utf-8 -*-

from PyQt4.QtCore import QThread, SIGNAL, pyqtSignal, QSettings
from Functions import InitConfigValue, pathPrefix

class ToolsThread(QThread):
	""" custom signals for DownLoadClient """
	nextfile = pyqtSignal(int)
	complete = pyqtSignal()
	def __init__(self, obj = None, maskSet = None, parent = None):
		QThread.__init__(self, parent)

		self.Obj = obj
		self.Parent = parent
		self.maskSet = maskSet
		self.pathPref = pathPrefix()

	def run(self):
		self.Obj.run()
		self.emit(SIGNAL('threadRunning'), self.Parent)

	def getSharedSourceStructFile(self):
		return self.Obj.getSharedSourceStructFile()

	def getSharedData(self):
		downLoadPath = unicode(InitConfigValue(QSettings('LightMight','LightMight'), \
											'DownLoadTo', self.pathPref + '/tmp/LightMight/DownLoad'))
		self.Obj.getSharedData(self.maskSet, downLoadPath, self, self.Parent.currentRemoteServerState)

	def terminate(self):
		self.Obj._shutdown()
