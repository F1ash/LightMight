# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
from TreeProc import TreeModel
from TreeProcess import TreeProcessing
from PathToTree import PathToTree, SharedSourceTree2XMLFile
from ListingText import ListingText
from Functions import InitConfigValue, dateStamp, moveFile, randomString, Path
from mcastSender import _send_mcast as Sender
from Modules import ModuleExist
import os, stat, os.path

class ServerSettingsShield(QtGui.QDialog):
	def __init__(self, obj = None, parent = None):
		QtGui.QDialog.__init__(self, parent)

		self.Obj = obj
		self.SEP = os.sep

		self.setWindowTitle('LightMight Server Settings')
		self.setWindowIcon(QtGui.QIcon('..' + self.SEP + 'icons' + self.SEP + 'tux_partizan.png'))

		form = QtGui.QGridLayout()

		self.serverNameLabel = QtGui.QLabel('Server Name :')
		form.addWidget(self.serverNameLabel, 0, 0)

		self.defaultName  = InitConfigValue(self.Obj.Settings, 'ServerName', \
											os.path.basename(os.path.expanduser('~')) + \
											' LightMight Server')
		self.serverNameString = QtGui.QLineEdit(self.defaultName)
		form.addWidget(self.serverNameString, 0, 1, 1, 2)

		self.emittPort = QtGui.QLabel('Port Diapason :')
		form.addWidget(self.emittPort, 1, 1)

		self.checkMinPortBox = QtGui.QSpinBox()
		self.checkMinPortBox.setMinimum(0)
		self.checkMinPortBox.setMaximum(65535)
		value = InitConfigValue(self.Obj.Settings, 'MinPort', '34000' )
		self.checkMinPortBox.setValue(int(value))
		self.checkMinPortBox.setSingleStep(1)
		self.checkMinPortBox.setToolTip('Minimal Port')
		form.addWidget(self.checkMinPortBox, 1, 2)

		self.checkMaxPortBox = QtGui.QSpinBox()
		self.checkMaxPortBox.setMinimum(0)
		self.checkMaxPortBox.setMaximum(65535)
		value = InitConfigValue(self.Obj.Settings, 'MaxPort', '34100' )
		self.checkMaxPortBox.setValue(int(value))
		self.checkMaxPortBox.setSingleStep(1)
		self.checkMaxPortBox.setToolTip('Maximal Port')
		form.addWidget(self.checkMaxPortBox, 2, 2)

		self.detectionLabel = QtGui.QLabel('Use detection:')
		form.addWidget(self.detectionLabel, 4, 1)

		self.detectionPanel = QtGui.QHBoxLayout()

		self.useAvahiDetect = QtGui.QCheckBox()
		if InitConfigValue(self.Obj.Settings, 'AvahiDetect', 'True') == 'True' :
			value = QtCore.Qt.Checked
		else:
			value = QtCore.Qt.Unchecked
		self.useAvahiDetect.setToolTip('Avahi\Bonjour')
		self.useAvahiDetect.setCheckState(value)
		if not ModuleExist.AvahiAvailable : self.useAvahiDetect.Enabled(False)
		self.detectionPanel.addWidget(self.useAvahiDetect, 0, alignment=QtCore.Qt.AlignLeft)

		self.useBroadcastDetect = QtGui.QCheckBox()
		if InitConfigValue(self.Obj.Settings, 'BroadcastDetect', 'True') == 'True' :
			value = QtCore.Qt.Checked
		else:
			value = QtCore.Qt.Unchecked
		self.useBroadcastDetect.setToolTip('Broadcast(UDP)')
		self.useBroadcastDetect.setCheckState(value)
		self.detectionPanel.addWidget(self.useBroadcastDetect, 1, alignment=QtCore.Qt.AlignRight)

		form.addItem(self.detectionPanel, 4, 2)

		self.useTLSLabel = QtGui.QLabel('Use encrypt (TLSv1):')
		form.addWidget(self.useTLSLabel, 5, 1)

		self.useTLSCheck = QtGui.QCheckBox()
		if InitConfigValue(self.Obj.Settings, 'UseTLS', 'False') == 'True' :
			value = QtCore.Qt.Checked
		else:
			value = QtCore.Qt.Unchecked
		self.useTLSCheck.setCheckState(value)
		form.addWidget(self.useTLSCheck, 5, 2)

		self.saveLastStructureLabel = QtGui.QLabel('Save last Share Structure :')
		form.addWidget(self.saveLastStructureLabel, 6, 1)

		self.saveLastStructureCheck = QtGui.QCheckBox()
		if InitConfigValue(self.Obj.Settings, 'SaveLastStructure', 'True') == 'True' :
			value = QtCore.Qt.Checked
		else:
			value = QtCore.Qt.Unchecked
		self.saveLastStructureCheck.setCheckState(value)
		form.addWidget(self.saveLastStructureCheck, 6, 2)

		self.sharedSourceLabel = QtGui.QLabel('Shared Sources :')
		form.addWidget(self.sharedSourceLabel, 7, 0)

		self.treeModel = TreeModel('Name', 'Description', parent = self)
		self.sharedTree = QtGui.QTreeView()
		self.sharedTree.setRootIsDecorated(True)
		TreeProcessing().setupItemData([], self.treeModel.rootItem)
		self.sharedTree.setToolTip("<font color=red><b>Select path<br>for share it !</b></font>")
		self.sharedTree.setExpandsOnDoubleClick(True)
		self.sharedTree.setModel(self.treeModel)
		form.addWidget(self.sharedTree, 8, 0, 8, 2)

		self.addDirPathButton = QtGui.QPushButton('&Dir')
		self.addDirPathButton.setMaximumWidth(75)
		self.addDirPathButton.setToolTip('Add directory in Tree of Shared Sources')
		self.connect(self.addDirPathButton, QtCore.SIGNAL('clicked()'), self.addDirPath)
		form.addWidget(self.addDirPathButton, 8, 2)

		self.addFilePathButton = QtGui.QPushButton('&File')
		self.addFilePathButton.setMaximumWidth(75)
		self.addFilePathButton.setToolTip('Add file in Tree of Shared Sources')
		self.connect(self.addFilePathButton, QtCore.SIGNAL('clicked()'), self.addFilePaths)
		form.addWidget(self.addFilePathButton, 9, 2)

		self.delPathButton = QtGui.QPushButton('&Del')
		self.delPathButton.setMaximumWidth(75)
		self.delPathButton.setToolTip('Delete path from Tree of Shared Sources')
		self.connect(self.delPathButton, QtCore.SIGNAL('clicked()'), self.delPath)
		form.addWidget(self.delPathButton, 11, 2)

		self.loadTreeButton = QtGui.QPushButton('&Load')
		self.loadTreeButton.setMaximumWidth(75)
		self.loadTreeButton.setToolTip('Load saved Shared Sources Tree')
		self.connect(self.loadTreeButton, QtCore.SIGNAL('clicked()'), self.loadTree)
		form.addWidget(self.loadTreeButton, 12, 2)

		self.saveTreeButton = QtGui.QPushButton('&Save')
		self.saveTreeButton.setMaximumWidth(75)
		self.saveTreeButton.setToolTip('Save Shared Sources Tree')
		self.connect(self.saveTreeButton, QtCore.SIGNAL('clicked()'), self.saveTree)
		form.addWidget(self.saveTreeButton, 13, 2)

		self.okButton = QtGui.QPushButton('&Ok')
		self.okButton.setMaximumWidth(75)
		self.connect(self.okButton, QtCore.SIGNAL('clicked()'), self.ok)
		form.addWidget(self.okButton, 14, 2)

		self.cancelButton = QtGui.QPushButton('&Cancel')
		self.cancelButton.setMaximumWidth(75)
		self.connect(self.cancelButton, QtCore.SIGNAL('clicked()'), self.cancel)
		form.addWidget(self.cancelButton, 15, 2)

		self.setLayout(form)
		self.connect(self, QtCore.SIGNAL('refresh'), self.treeRefresh)
		self.connect(self, QtCore.SIGNAL('threadError'), self.threadMSG)
		self.useTLSCheck.stateChanged.connect(self.certificatePath)

	def certificatePath(self, i):
		if i == QtCore.Qt.Checked :
			#print '  checked'
			self.certFileName = QtGui.QFileDialog.getOpenFileName(self, 'Path_to_', '~', 'OpenSSL Certificate (*.pem);;')
			#print self.certFileName
			""" check certificate """
			self.verifyProcess = QtCore.QProcess()
			self.vrfProcOutput = Path.multiPath(Path.tempStruct, 'server', randomString(24))
			self.verifyProcess.setStandardOutputFile(self.vrfProcOutput)
			self.verifyProcess.setStandardErrorFile(self.vrfProcOutput)
			self.verifyProcess.finished.connect(self.readVrfProcOutput)
			self.verifyProcess.start('openssl', \
									QtCore.QStringList() << 'verify' << self.certFileName)
		else :
			#print '  unchecked'
			pass

	def readVrfProcOutput(self, i):
		#print '  finised : ', i
		with open(self.vrfProcOutput, 'rb') as output :
			str_ = output.read()
		if str_.find('unable to load certificate') == -1 :
			STR_ = "MSG: Exit code : " + str(i) + '\n' + str_
		else :
			self.useTLSCheck.setCheckState(QtCore.Qt.Unchecked)
			STR_ = 'MSG: Certificate is a unavailable or incorrect.\n' + str_
		showHelp = ListingText(STR_, self)
		showHelp.exec_()
		os.remove(self.vrfProcOutput)

	def addDirPath(self):
		_nameDir = QtGui.QFileDialog.getExistingDirectory(self, 'Path_to_', '~', QtGui.QFileDialog.ShowDirsOnly)
		nameDir = QtCore.QString(_nameDir).toUtf8().data()
		if os.access(nameDir, os.R_OK) and os.access(nameDir, os.X_OK) :    ## and os.access(nameDir, os.W_OK) :
			# print nameDir
			P = PathToTree(_nameDir, self.treeModel.rootItem, 'dir')
			self.treeModel.reset()
		else :
			showHelp = ListingText("MSG: uncorrect Path (or access denied): " + nameDir, self)
			showHelp.exec_()

	def addFilePaths(self):
		fileNames = QtGui.QFileDialog.getOpenFileNames(self, 'Path_to_', '~')
		for _name in fileNames :
			name_ = QtCore.QString(_name).toUtf8().data()
			if not stat.S_ISLNK(os.lstat(name_).st_mode) and os.access(name_, os.R_OK) :
				P = PathToTree(_name, self.treeModel.rootItem, 'file')
				self.treeModel.reset()
			else :
				showHelp = ListingText("MSG: uncorrect Path\n(access denied) or symLink : " + name_, self)
				showHelp.exec_()

	def treeRefresh(self):
		self.treeModel.reset()

	def threadMSG(self, str_):
		showHelp = ListingText("MSG: Available files not found in " + str_, self)
		showHelp.exec_()

	def delPath(self):
		item = self.sharedTree.selectionModel().currentIndex()
		if item.internalPointer() is not None :
			itemParent = item.internalPointer().parentItem
			if itemParent is not None : itemParent.removeChild(item)
			self.treeModel.reset()
		else :
			print 'Not select Item'

	def sentOfflinePost(self):
		if self.Obj.Settings.value('BroadcastDetect', True).toBool() :
			key = str(self.Obj.server_addr + ':' + str(self.Obj.server_port))
			if key in self.Obj.USERS :
				#print 'key :', key, ' in USERS'
				data = QtCore.QString('0' + '<||>' + \
									self.defaultName + '<||>' + \
									self.Obj.USERS[key][1] + '<||>' + \
									self.Obj.USERS[key][2] + '<||>' + \
									'' + '<||>' + \
									'' + '<||>' + \
									'*infoShare*')
				Sender(data)

	def loadTree(self):
		fileName = QtGui.QFileDialog.getOpenFileName(self, 'Path_to_', Path.config('treeBackup'))
		if fileName != '' :
			if 'serverThread' in dir(self.Obj) :
				self.Obj.serverThread.terminate()
				self.Obj.serverThread.exit()
			self.sentOfflinePost()
			self.saveData()
			self.Obj.initServer(loadFile = fileName)
			self.done(0)

	def saveTree(self):
		tmpFile = 'sharedSourceBackup_' + dateStamp()
		S = SharedSourceTree2XMLFile(tmpFile, self.treeModel.rootItem)

		fileName = QtGui.QFileDialog.getSaveFileName(self, 'Path_to_', Path.config('treeBackup'))

		if not moveFile(Path.multiPath(Path.tempStruct, 'server', tmpFile), \
						QtCore.QString(fileName).toUtf8().data()) :
			showHelp = ListingText("MSG: tree not saved.", self)
			showHelp.exec_()

	def ok(self):
		if 'serverThread' in dir(self.Obj) :
			self.Obj.serverThread._terminate('reINIT')
			#self.Obj.serverThread.exit()
		else : self.preInitServer()

	@QtCore.pyqtSlot(str, name = 'preInitServer')
	def preInitServer(self, str_):
		if str_ == 'reINIT' :
			print 'serverDown signal received'
		else :
			print 'alien signal'
			return None
		self.sentOfflinePost()
		self.saveData()
		self.Obj.initServeR.emit(self.treeModel, '', self.Obj.serverState)
		#self.Obj.initServer(self.treeModel, previousState = self.Obj.serverState)
		self.done(0)

	def cancel(self):
		self.done(0)

	def saveData(self):
		self.Obj.Settings.setValue('ServerName', self.serverNameString.text())
		self.Obj.Settings.setValue('MinPort', self.checkMinPortBox.value())
		self.Obj.Settings.setValue('MaxPort', self.checkMaxPortBox.value())
		if self.useAvahiDetect.isChecked() :
			value = 'True'
		else :
			value = 'False'
		self.Obj.Settings.setValue('AvahiDetect', value)
		if self.useBroadcastDetect.isChecked() :
			value = 'True'
		else :
			value = 'False'
		self.Obj.Settings.setValue('BroadcastDetect', value)
		if self.saveLastStructureCheck.isChecked() :
			value = 'True'
		else :
			value = 'False'
		self.Obj.Settings.setValue('SaveLastStructure', value)
		if self.useTLSCheck.isChecked() :
			value = 'True'
			if 'certFileName' in dir(self) :
				self.Obj.Settings.setValue('PathToCertificate', self.certFileName)
		else :
			value = 'False'
		self.Obj.Settings.setValue('UseTLS', value)
		self.Obj.Settings.sync()

	def closeEvent(self, event):
		event.ignore()
		self.done(0)

