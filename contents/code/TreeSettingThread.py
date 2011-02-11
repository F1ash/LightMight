# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore

class TreeSettingThread(QtCore.QThread):
	def __init__(self, obj = None, nameDir = None, rootItem = None, parent = None):
		QtCore.QThread.__init__(self, parent)

		self.Parent = obj
		self.setTerminationEnabled(False)
		#self.Timer = QTimer()
		#self.Timer.setSingleShot(True)
		#self.Timer.timeout.connect(self._terminate)
		#self.timeout = int(timeout) * 1000
		#self.accData = accountData
		self.nameDir = nameDir
		self.rootItem = rootItem

	def run(self):
		try:
			GeneralLOCK.lock()

			x = ''
			P = Parser()
			doc = P.listPrepare(self.nameDir)
			resultFileName = P.getResultFile(resultFileName = '_resultXMLFileOfAddSharedSource', \
																								doc = doc)
			doc.unlink(); doc = None
			del P; P = None
			if resultFileName is None :
				T = TreeProcessing()
				T.setupItemData([resultFileName], self.rootItem)
				del T; T = None
				print gc.collect()
				print gc.get_referrers()
				del gc.garbage[:]
			else :
				self.Parent.emit(QtCore.SIGNAL('threadError'), self.nameDir)

		except x :
			print x, '  thread'
			#tb = sys.exc_info()[2]
			#pdb.post_mortem(tb)
			pass
		finally :
			#self.Timer.stop()
			GeneralLOCK.unlock()
			#QApplication.postEvent(self.Parent, QEvent(1010))
			self.Parent.emit(QtCore.SIGNAL('refresh'))
			pass
		return

	def _terminate(self):
		print 'Mail thread timeout terminating...'
		#self.Timer.stop()
		GeneralLOCK.unlock()
		self.Parent.emit(QtCore.SIGNAL('refresh'))
		self.terminate()

