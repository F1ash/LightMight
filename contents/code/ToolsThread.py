# -*- coding: utf-8 -*-

from PyQt4.QtCore import QThread

class ToolsThread(QThread):
	def __init__(self, obj = None, parent = None):
		QThread.__init__(self, parent)

		self.Obj = obj

	def run(self):
		self.Obj.run()

	def terminate(self):
		self.Obj._shutdown()
