# -*- coding: utf-8 -*-

from PyQt4.QtCore import QThread

class SetupTree(QThread):
	def __init__(self, obj = None, path_ = [], rootItem = None, emitter = None, key = False, parent = None):
		QThread.__init__(self, parent)

		self.Obj = obj
		self.path_ = path_
		self.rootItem = rootItem
		self.Emitter = emitter
		self.Key = key

	def run(self):
		count, downLoads = self.Obj.setupItemData(self.path_, self.rootItem)
		if self.Key :
			commonSet = {}
			self.Obj.getCommonSetOfSharedSource(self.rootItem, commonSet)
			self.Emitter.commonSet.emit(commonSet)
		else :
			self.Emitter.tree.emit(self.rootItem, count, downLoads)
			self.Emitter.complete.emit()
