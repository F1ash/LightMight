# -*- coding: utf-8 -*-

from PyQt4.QtCore import QThread, SIGNAL, pyqtSignal
from TreeProcess import TreeProcessing
from Functions import InitConfigValue

class ToolsThread(QThread):
	""" custom signals for progressBar """
	nextfile = pyqtSignal(int)
	nextfile = pyqtSignal(int, int)
	def __init__(self, obj = None, rootItem = None, parent = None, jobNumber = 0):
		QThread.__init__(self, parent)

		self.Obj = obj
		self.Parent = parent
		self.rootItem = rootItem
		self.jobNumber = jobNumber

	def run(self):
		self.Obj.run()
		self.emit(SIGNAL('threadRunning'), self.Parent)

	def getSharedSourceStructFile(self):
		return self.Obj.getSharedSourceStructFile()

	def getSharedData(self):
		t = TreeProcessing()
		t.getSharedData(self.rootItem, self.Obj, self, self.jobNumber, \
			downLoadPath = unicode(InitConfigValue(self.Obj.Obj.Settings, 'DownLoadTo', '/tmp')))

	def terminate(self):
		self.Obj._shutdown()
