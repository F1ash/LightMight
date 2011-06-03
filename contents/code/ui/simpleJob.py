# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
from ToolsThread import ToolsThread
from TreeProc import TreeModel
from ButtonPanel import ButtonPanel
from TreeProcess import TreeProcessing
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

	def jobProgressBarChange(self, jobNumber):
		#print 'dd', jobNumber
		number = -1
		for i in xrange(self.menuTab.count()) :
			if jobNumber == self.menuTab.widget(i).jobNumber :
				number = i
				break
		#print number , '  number of Tab'
		if number > -1 :
			prgBar = self.menuTab.widget(number).progressBar
			prgBar.setValue(prgBar.value() + 1)

	def _addJob(self, j, rootItem, serverState, addr, port, info = ''):
		"""
			; добавить прогрессбар (если возможно)
		"""
		count, downLoadSize = TreeProcessing().getCheckedItemDataSumm(rootItem)
		#print serverState, addr, port, count, downLoadSize, j
		self.menuTab.addTab(ButtonPanel(self, count, downLoadSize, j), \
							QtGui.QIcon('../icons/tux_partizan.png'), \
							'Job #' + str(j))
		i = self.menuTab.count()
		self.menuTab.setTabToolTip(i - 1, 'Job #' + str(j) + ':\n' + info)
		if i == 1 : self.show()
		simpleJob = ToolsThread(xr_client(addr, port, self.Obj), rootItem, self, jobNumber = j)
		simpleJob.start()
		self.connect( simpleJob, QtCore.SIGNAL('threadRunning'), simpleJob.getSharedData )
		simpleJob.nextfile.connect(self.jobProgressBarChange)

	def _delJob(self, i):
		""" предусмотреть прекращение задачи по закрытию закладки,
			по завершении работы приложения или ручной остановке
			в панели
		"""
		self.menuTab.removeTab(i)
		if self.menuTab.count() == 0:
			self.hide()
