# -*- coding: utf-8 -*-

from PyQt4.QtCore import QThread, SIGNAL, pyqtSignal, QSettings
from Functions import InitConfigValue

class ToolsThread(QThread):
	""" custom signal for progressBar """
	nextfile = pyqtSignal(int)
	def __init__(self, obj = None, maskSet = None, parent = None):
		QThread.__init__(self, parent)

		self.Obj = obj
		self.Parent = parent
		self.maskSet = maskSet

	def run(self):
		self.Obj.run()
		self.emit(SIGNAL('threadRunning'), self.Parent)

	def getSharedSourceStructFile(self):
		return self.Obj.getSharedSourceStructFile()

	def getSharedData(self):
		""" проверить неизменённость статуса сервера
		"""
		downLoadPath = unicode(InitConfigValue(QSettings('LightMight','LightMight'), 'DownLoadTo', '/tmp'))
		self.Obj.getSharedData(self.maskSet, downLoadPath, self)

	def terminate(self):
		self.Obj._shutdown()
