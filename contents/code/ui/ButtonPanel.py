# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtCore


class ButtonPanel(QtGui.QWidget):
	def __init__(self, Obj_, count = 0, downLoadSize = 0, jobNumber = -1, parent = None):
		QtGui.QWidget.__init__(self, parent)

		self.Obj = Obj_
		self.jobNumber = jobNumber
		#print self.jobNumber , ' job'

		self.layout = QtGui.QVBoxLayout()

		self.progressBar = QtGui.QProgressBar()
		self.progressBar.setOrientation(QtCore.Qt.Vertical)
		self.progressBar.setAlignment(QtCore.Qt.AlignHCenter)
		""" to measure the number of files """
		self.progressBar.setRange(0, count)
		self.progressBar.setValue(0)
		""" to measure the volume of downloads """
		#self.progressBar.setRange(0, downLoadSize/100)
		self.layout.addWidget(self.progressBar, 0, QtCore.Qt.AlignHCenter)

		self.addButton = QtGui.QPushButton(QtCore.QString('Add'))
		self.addButton.setToolTip('Add Item to ItemList\nof Shared Source')
		self.connect(self.addButton, QtCore.SIGNAL('clicked()'), self.addItem)
		self.layout.addWidget(self.addButton, 0,  QtCore.Qt.AlignHCenter)

		self.delButton = QtGui.QPushButton(QtCore.QString('Del'))
		self.delButton.setToolTip('Delete Item from ItemList\nof Shared Source')
		self.connect(self.delButton, QtCore.SIGNAL('clicked()'), self.addItem)
		self.layout.addWidget(self.delButton, 0,  QtCore.Qt.AlignHCenter)

		self.upLoadButton = QtGui.QPushButton(QtCore.QString('Up'))
		self.upLoadButton.setToolTip('UpLoad ItemList\nof Shared Source')
		self.connect(self.upLoadButton, QtCore.SIGNAL('clicked()'), self.upLoad)
		self.layout.addWidget(self.upLoadButton, 0,  QtCore.Qt.AlignHCenter)

		self.setLayout(self.layout)
		#print self.progressBar.value(), ' init value'

	def addItem(self):
		pass

	def upLoad(self):
		QtGui.QApplication.postEvent(self.Obj, QtCore.QEvent(1010))


