# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
from ToolsThread import ToolsThread
from ListingText import ListingText
from clnt import xr_client
import os, string

class ButtonPanel(QtGui.QWidget):
	# custom signal
	errorString = QtCore.pyqtSignal(str)
	def __init__(self, name_ = '', downLoadSize = 0, jobNumber = -1, \
					serverState = '', addr = '', port = '', info = '', TLS = 'False', parent = None):
		QtGui.QWidget.__init__(self, parent)

		self.nameMaskFile = name_
		self.jobNumber = jobNumber
		self.address = addr
		self.port = port
		self.currentRemoteServerState = serverState
		self.maskSet = {}
		if 'True' == TLS :
			self.TLS = True
		else :
			self.TLS = False
		#print name_, downLoadSize, jobNumber, serverState, addr, port, \
		#					'\nclnt args :\n', info, '\nEncrypt : ', TLS

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

		self.startButton = QtGui.QPushButton(QtCore.QString('&Start'))
		self.startButton.setToolTip('Restart DownLoad')
		self.connect(self.startButton, QtCore.SIGNAL('clicked()'), self.startJob)
		self.layout.addWidget(self.startButton, 0,  QtCore.Qt.AlignHCenter)

		self.closeButton = QtGui.QPushButton(QtCore.QString('&Close'))
		self.closeButton.setToolTip('Close DownloadClient')
		self.closeButton.hide()
		self.connect(self.closeButton, QtCore.SIGNAL('clicked()'), self.stopJob)
		self.layout.addWidget(self.closeButton, 0, QtCore.Qt.AlignHCenter)

		self.setLayout(self.layout)
		#print self.progressBar.value(), ' init value'
		self.setMaskSet()

	def setMaskSet(self):
		if not os.path.isfile('/dev/shm/LightMight/client/' + self.nameMaskFile) :
			print '  file not exist'
			return None
		with open('/dev/shm/LightMight/client/' + self.nameMaskFile) as f :
			for line in f :
				s = string.split(line, '<||>')
				if s[0] == '1' :
					self.maskSet[int(unicode(str(s[3].decode('utf-8')).replace('\n', '')))] = \
												(int(unicode(str(s[0].decode('utf-8')).replace('\n', ''))), \
												s[1].decode('utf-8'), \
												int(unicode(str(s[2].decode('utf-8')).replace('\n', ''))), \
												int(unicode(str(s[3].decode('utf-8')).replace('\n', ''))))
					#print self.maskSet[int(unicode(str(s[3].decode('utf-8')).replace('\n', '')))]

		os.remove('/dev/shm/LightMight/client/' + self.nameMaskFile)

	def startJob(self):
		self.startButton.hide()
		self.job = ToolsThread(xr_client(self.address, \
										self.port, \
										parent = self, \
										TLS = self.TLS), \
								self.maskSet, \
								self)
		self.job.start()
		self.connect( self.job, QtCore.SIGNAL('threadRunning'), self.job.getSharedData )
		self.job.nextfile.connect(self.jobProgressBarChangeVolume)
		self.job.complete.connect(self.showCloseButton)
		self.errorString.connect(self.showErrorMSG)

	def showCloseButton(self):
		self.closeButton.show()
		self.setToolTip("<font color=red>Job is complete</font><br>" + self.toolTip())

	def stopJob(self):
		if 'job' in dir(self) :
			self.job.terminate()
		self.close()

	def jobProgressBarChangeVolume(self, volume = 0):
		self.progressBar.setValue(self.progressBar.value() + volume)

	def showErrorMSG(self, str_):
		print 'Message : ', str(str_)
		showHelp = ListingText("MSG: " + str(str_), self)
		showHelp.exec_()


