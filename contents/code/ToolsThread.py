# -*- coding: utf-8 -*-

from PyQt4.QtCore import QThread, SIGNAL

class ToolsThread(QThread):
	def __init__(self, obj = None, parent = None):
		QThread.__init__(self, parent)

		self.Obj = obj
		self.Parent = parent

	def run(self):
		self.Obj.run()
		self.emit(SIGNAL('threadRunning'), self.Parent)

	def getSharedSourceStructFile(self):
		return self.Obj.getSharedSourceStructFile()

	def terminate(self):
		self.Obj._shutdown()
