# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
from ToolsThread import ToolsThread
from clnt import xr_client
import os, string

class ButtonPanel(QtGui.QWidget):
	def __init__(self, name_ = '', downLoadSize = 0, jobNumber = -1, \
					serverState = '', addr = '', port = '', info = '', parent = None):
		QtGui.QWidget.__init__(self, parent)

		self.nameMaskFile = name_
		self.jobNumber = jobNumber
		self.address = addr
		self.port = port
		self.serverState = serverState
		self.maskSet = {}
		print name_, downLoadSize, jobNumber, serverState, addr, port, info

		self.setWindowTitle('LightMight Job')
		self.setWindowIcon(QtGui.QIcon('../icons/tux_partizan.png'))
		self.setToolTip('Job #' + str(jobNumber) + ':\n' + QtCore.QString().fromUtf8(info) + \
						'\nDownload : ' + downLoadSize + ' Byte(s)')

		self.layout = QtGui.QVBoxLayout()

		self.progressBar = QtGui.QProgressBar()
		self.progressBar.setOrientation(QtCore.Qt.Vertical)
		self.progressBar.setAlignment(QtCore.Qt.AlignHCenter)
		""" to measure the number of files """
		#self.progressBar.setRange(0, count)
		self.progressBar.setValue(0)
		""" to measure the volume of downloads """
		range_ = int(downLoadSize)
		if range_ == 0 : range_ = 1
		self.progressBar.setRange(0, range_)
		self.layout.addWidget(self.progressBar, 0, QtCore.Qt.AlignHCenter)

		self.startButton = QtGui.QPushButton(QtCore.QString('Start'))
		self.startButton.setToolTip('Restart DownLoad')
		self.connect(self.startButton, QtCore.SIGNAL('clicked()'), self.startJob)
		self.layout.addWidget(self.startButton, 0,  QtCore.Qt.AlignHCenter)

		self.stopButton = QtGui.QPushButton(QtCore.QString('Stop'))
		self.stopButton.setToolTip('Close DownloadClient')
		self.connect(self.stopButton, QtCore.SIGNAL('clicked()'), self.stopJob)
		self.layout.addWidget(self.stopButton, 0,  QtCore.Qt.AlignHCenter)

		self.setLayout(self.layout)
		#print self.progressBar.value(), ' init value'
		self.setMaskSet()

	def setMaskSet(self):
		with open('/dev/shm/LightMight/client/' + self.nameMaskFile) as f :
			for line in f :
				s = string.split(line, '<||>')
				#print s
				if s[0] == '1' :
					self.maskSet[int(s[3])] = (s[0], s[1], s[2], s[3])

		os.remove('/dev/shm/LightMight/client/' + self.nameMaskFile)

	def startJob(self):
		self.startButton.hide()
		self.job = ToolsThread(xr_client(self.address, self.port), self.maskSet, self)
		self.job.start()
		self.connect( self.job, QtCore.SIGNAL('threadRunning'), self.job.getSharedData )
		self.job.nextfile.connect(self.jobProgressBarChangeVolume)

	def stopJob(self):
		if 'job' in dir(self) :
			self.job.terminate()
		self.close()

	def jobProgressBarChangeVolume(self, volume = 0):
		self.progressBar.setValue(self.progressBar.value() + volume)


