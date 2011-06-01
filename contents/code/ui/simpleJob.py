# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
from ToolsThread import ToolsThread
from TreeProc import TreeModel
from ButtonPanel import ButtonPanel
from clnt import xr_client

class SimpleJob(QtGui.QWidget):
	def __init__(self, obj = None, parent = None):
		QtGui.QWidget.__init__(self, parent)

		self.Obj = obj

		self.setWindowTitle('LightMight')
		self.setWindowIcon(QtGui.QIcon('../icons/tux_partizan.png'))
		self.layout = QtGui.QVBoxLayout()

		self.menuTab = QtGui.QTabWidget()
		self.menuTab.setUsesScrollButtons(True)
		self.menuTab.clear()
		self.menuTab.setTabsClosable(True)
		self.menuTab.tabCloseRequested.connect(self._delJob)
		self.layout.addWidget(self.menuTab)

		self.setLayout(self.layout)
		self.hide()

	def _addJob(self, j, rootItem, serverState, addr, port, info = ''):
		"""
			; добавить прогрессбар (если возможно)
		"""
		self.menuTab.addTab(ButtonPanel(self), QtGui.QIcon('../icons/tux_partizan.png'), 'Job #' + str(j))
		i = self.menuTab.count()
		self.menuTab.setTabToolTip(i - 1, 'Job #' + str(j) + ':\n' + info)
		if i == 1 : self.show()
		#print serverState, addr, port
		simpleJob = ToolsThread(xr_client(addr, port, self.Obj, 'getSharedData'), rootItem, self)
		simpleJob.start()
		self.connect( simpleJob, QtCore.SIGNAL('threadRunning'), simpleJob.getSharedData )

	def _delJob(self, i):
		""" предусмотреть прекращение задачи по закрытию закладки,
			по завершении работы приложения или ручной остановке
			в панели
		"""
		self.menuTab.removeTab(i)
		if self.menuTab.count() == 0:
			self.hide()
