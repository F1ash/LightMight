# -*- coding: utf-8 -*-

from PyQt4.QtCore import QThread, SIGNAL
from TreeProcess import TreeProcessing

class ToolsThread(QThread):
	def __init__(self, obj = None, rootItem = None, parent = None):
		QThread.__init__(self, parent)

		self.Obj = obj
		self.Parent = parent
		self.rootItem = rootItem

	def run(self):
		self.Obj.run()
		self.emit(SIGNAL('threadRunning'), self.Parent)

	def getSharedSourceStructFile(self):
		return self.Obj.getSharedSourceStructFile()

	def getSharedData(self):
		t = TreeProcessing()
		t.getDataMask(self.rootItem, self.Obj)

	def terminate(self):
		self.Obj._shutdown()
