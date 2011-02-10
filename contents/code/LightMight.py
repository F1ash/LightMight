# -*- coding: utf-8 -*-

import os, sys, os.path, gc, xml.parsers.expat
from PyQt4 import QtGui, QtCore
from Parser import Parser
from TreeProc import TreeItem, TreeModel, TreeProcessing

FileNameList = []
FileNameList2UpLoad = []

def createStructure():
	for nameDir in ['/dev/shm/LightMight', '/dev/shm/LightMight/cache', '/dev/shm/LightMight/structure'] :
		if not os.path.isdir(nameDir):
			os.mkdir(nameDir)

class MainWindow(QtGui.QMainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self)

		#self.resize(450, 350)
		self.setWindowTitle('LightMight')
		self.setWindowIcon(QtGui.QIcon('../icons/tux_partizan.png'))

		self.Settings = QtCore.QSettings('LightMight','LightMight')

		self.create_struct = QtGui.QAction(QtGui.QIcon('../icons/crst.png'),'&Create of Structure', self)
		self.create_struct.setShortcut('Ctrl+D')
		self.create_struct.setStatusTip('Create new structure for Backup')
		self.connect(self.create_struct, QtCore.SIGNAL('triggered()'), self.createStruct)

		self.base_ = QtGui.QAction(QtGui.QIcon('../icons/base.png'),'&Base of Backups', self)
		self.base_.setShortcut('Ctrl+B')
		self.base_.setStatusTip('List of backupping Path(s)')
		self.connect(self.base_, QtCore.SIGNAL('triggered()'), self.showBase)

		self.exit_ = QtGui.QAction(QtGui.QIcon('../icons/exit.png'), '&Exit', self)
		self.exit_.setShortcut('Ctrl+Q')
		self.exit_.setStatusTip('Exit application')
		self.connect(self.exit_, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))

		listHelp = QtGui.QAction(QtGui.QIcon('../icons/help.png'),'&About Backupper', self)
		listHelp.setStatusTip('Read help')
		self.connect(listHelp,QtCore.SIGNAL('triggered()'), self.showHelp_)

		serverSettings = QtGui.QAction(QtGui.QIcon('../icons/help.png'),'&Server Settings', self)
		serverSettings.setStatusTip('Read help')
		self.connect(serverSettings, QtCore.SIGNAL('triggered()'), self.showServerSettingsShield)

		clientSettings = QtGui.QAction(QtGui.QIcon('../icons/help.png'),'&Client Settings', self)
		clientSettings.setStatusTip('Read help')
		self.connect(clientSettings, QtCore.SIGNAL('triggered()'), self.showClientSettingsShield)

		self.statusBar()

		menubar = self.menuBar()

		file_ = menubar.addMenu('&File')
		file_.addAction(self.base_)
		file_.addAction(self.create_struct)
		file_.addAction(self.exit_)

		set_ = menubar.addMenu('&Settings')
		set_.addAction(serverSettings)
		set_.addAction(clientSettings)

		help_ = menubar.addMenu('&Help')
		help_.addAction(listHelp)

		self.menuTab = Box(self)
		#self.menuTab = BoxLayout(Box)
		#self.menuTab.setMaximumSize(800, 650)
		#self.menuTab.clear()
		#self.menuTab.setUsesScrollButtons(True)
		#self.create_menuTab(0)
		self.setCentralWidget(self.menuTab)

		self.trayIconMenu = QtGui.QMenu(self)
		show_hide = self.trayIconMenu.addAction(QtGui.QIcon('../icons/tux_partizan.png'), 'Hide / Show')
		self.connect(show_hide, QtCore.SIGNAL('triggered()'), self.show_n_hide)
		help_tray = self.trayIconMenu.addAction(QtGui.QIcon('../icons/help.png'), 'Help')
		self.connect(help_tray, QtCore.SIGNAL('triggered()'), self.showHelp_)
		exit_tray = self.trayIconMenu.addAction(QtGui.QIcon('../icons/exit.png'), '&Exit')
		self.connect(exit_tray, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))
		self.trayIconPixmap = QtGui.QPixmap('../icons/tux_partizan.png') # файл иконки
		self.trayIcon = QtGui.QSystemTrayIcon(self)
		self.trayIcon.setToolTip('LightMight')
		self.trayIcon.setContextMenu(self.trayIconMenu)
		self.trayIcon.setIcon(QtGui.QIcon(self.trayIconPixmap))
		self.connect(self.trayIcon, QtCore.SIGNAL("activated(QSystemTrayIcon::ActivationReason)"), \
																			self.trayIconClicked)
		self.trayIcon.show()

		# toolbar = self.addToolBar('Exit')
		# toolbar.addAction(exit_)

	def customEvent(self, event):
		if event.type() == 1010 :
			global FileNameList
			global FileNameList2UpLoad
			FileNameList2UpLoad = []
			f = open('maskFile', 'wb')
			self.menuTab.treeModel.getDataMask(self.menuTab.treeModel.rootItem, f)
			f.close()
			f = open('maskFile', 'rb')
			self.menuTab.treeModel.dataMaskToFileNameList(self.menuTab.treeModel.rootItem, f)
			f.close()
			print FileNameList2UpLoad
		elif event.type() == 1011 :
			pass

	def showBase(self):
		self.list_ = ListingBase(self)

	def createStruct(self): pass

	def refreshTab(self): pass

	def show_n_hide(self):
		if self.isVisible():
			self.hide()
		else:
			self.show()

	def create_menuTab(self, i):
		self.menuTab.setCurrentIndex(i)
		self.menuTab.currentChanged.connect(self.refreshTab)

	def trayIconClicked(self, reason):
		if reason == QtGui.QSystemTrayIcon.DoubleClick :
			self.show_n_hide()

	def showHelp_(self):
		showHelp = ListingText("MSG: LightMight.help", self)
		showHelp.exec_()

	def showClientSettingsShield(self):
		_ClientSettingsShield = ClientSettingsShield()
		_ClientSettingsShield.exec_()
		pass

	def showServerSettingsShield(self):
		_ServerSettingsShield = ServerSettingsShield()
		_ServerSettingsShield.exec_()
		pass

class ClientSettingsShield(QtGui.QDialog):
	def __init__(self, parent = None):
		QtGui.QDialog.__init__(self, parent)

		self.setWindowTitle('LightMight Client Settings')
		self.setWindowIcon(QtGui.QIcon('../icons/tux_partizan.png'))

		form = QtGui.QGridLayout()

		self.listenPort = QtGui.QLabel('Listen Port Diapason :')
		form.addWidget(self.listenPort, 0, 1)

		self.checkMinPortBox = QtGui.QSpinBox()
		self.checkMinPortBox.setMinimum(0)
		self.checkMinPortBox.setMaximum(65535)
		self.checkMinPortBox.setValue(34100)
		self.checkMinPortBox.setSingleStep(1)
		form.addWidget(self.checkMinPortBox, 0, 2)

		self.checkMaxPortBox = QtGui.QSpinBox()
		self.checkMaxPortBox.setMinimum(0)
		self.checkMaxPortBox.setMaximum(65535)
		self.checkMaxPortBox.setValue(34200)
		self.checkMaxPortBox.setSingleStep(1)
		form.addWidget(self.checkMaxPortBox, 1, 2)

		self.useAvahi = QtGui.QLabel('Use Avahi Service (Zeroconf) :')
		form.addWidget(self.useAvahi, 2, 1)

		self.checkUseAvahi = QtGui.QCheckBox()
		self.checkUseAvahi.setCheckState(QtCore.Qt.Unchecked)
		form.addWidget(self.checkUseAvahi, 2, 2)

		self.upLoadPathLabel = QtGui.QLabel('DownLoad Path :')
		form.addWidget(self.upLoadPathLabel, 3, 0)

		self.upLoadPathString = QtGui.QLineEdit('/tmp/LightMight/DownLoad')
		form.addWidget(self.upLoadPathString, 4, 0, 4, 2)

		self.upLoadPathButton = QtGui.QPushButton('&Path')
		self.upLoadPathButton.setMaximumWidth(75)
		self.connect(self.upLoadPathButton, QtCore.SIGNAL('clicked()'), self.getPath)
		form.addWidget(self.upLoadPathButton, 3, 1)

		self.cancelButton = QtGui.QPushButton('&Cancel')
		self.cancelButton.setMaximumWidth(75)
		self.connect(self.cancelButton, QtCore.SIGNAL('clicked()'), self.cancel)
		form.addWidget(self.cancelButton, 4, 2, 4, 2)

		self.okButton = QtGui.QPushButton('&Ok')
		self.okButton.setMaximumWidth(75)
		self.connect(self.okButton, QtCore.SIGNAL('clicked()'), self.ok)
		form.addWidget(self.okButton, 3, 2)

		nullColumn = QtGui.QLabel('')
		nullColumn.setMaximumWidth(5)
		form.addWidget(nullColumn, 4, 3)

		self.setLayout(form)

	def getPath(self):
		nameDir = QtGui.QFileDialog.getExistingDirectory(self, 'Path_to_', '~', QtGui.QFileDialog.ShowDirsOnly)
		if os.access(nameDir, os.R_OK) and os.access(nameDir, os.W_OK) and os.access(nameDir, os.X_OK) :
			self.upLoadPathString.setText(nameDir)
		else :
			showHelp = ListingText("MSG: uncorrect Path (access denied)", self)
			showHelp.exec_()

	def ok(self):
		pass

	def cancel(self):
		self.done(0)

	def closeEvent(self, event):
		event.ignore()
		self.done(0)

class ServerSettingsShield(QtGui.QDialog):
	def __init__(self, parent = None):
		QtGui.QDialog.__init__(self, parent)

		self.setWindowTitle('LightMight Server Settings')
		self.setWindowIcon(QtGui.QIcon('../icons/tux_partizan.png'))

		form = QtGui.QGridLayout()

		self.serverNameLabel = QtGui.QLabel('Server Name :')
		form.addWidget(self.serverNameLabel, 0, 0)

		defaultName = os.getlogin() + ' LightMight Server'
		self.serverNameString = QtGui.QLineEdit(defaultName)
		form.addWidget(self.serverNameString, 0, 1, 1, 2)

		self.emittPort = QtGui.QLabel('Emitt on Port Diapason :')
		form.addWidget(self.emittPort, 1, 1)

		self.checkMinPortBox = QtGui.QSpinBox()
		self.checkMinPortBox.setMinimum(0)
		self.checkMinPortBox.setMaximum(65535)
		self.checkMinPortBox.setValue(34100)
		self.checkMinPortBox.setSingleStep(1)
		form.addWidget(self.checkMinPortBox, 1, 2)

		self.checkMaxPortBox = QtGui.QSpinBox()
		self.checkMaxPortBox.setMinimum(0)
		self.checkMaxPortBox.setMaximum(65535)
		self.checkMaxPortBox.setValue(34200)
		self.checkMaxPortBox.setSingleStep(1)
		form.addWidget(self.checkMaxPortBox, 2, 2)

		self.pool = QtGui.QLabel('Pool :')
		form.addWidget(self.pool, 3, 1)

		self.checkPoolBox = QtGui.QSpinBox()
		self.checkPoolBox.setMinimum(1)
		self.checkPoolBox.setMaximum(300)
		self.checkPoolBox.setValue(100)
		self.checkPoolBox.setSingleStep(1)
		form.addWidget(self.checkPoolBox, 3, 2)

		self.useAvahi = QtGui.QLabel('Use Avahi Service (Zeroconf) :')
		form.addWidget(self.useAvahi, 4, 1)

		self.checkUseAvahi = QtGui.QCheckBox()
		self.checkUseAvahi.setCheckState(QtCore.Qt.Unchecked)
		form.addWidget(self.checkUseAvahi, 4, 2)

		self.sharedSourceLabel = QtGui.QLabel('Shared Sources :')
		form.addWidget(self.sharedSourceLabel, 5, 0)

		pathList = []    ## ['result1', 'result2', 'result3']
		self.treeModel = TreeModel('Name', 'Description', parent = self)
		self.sharedTree = QtGui.QTreeView()
		self.sharedTree.setRootIsDecorated(True)
		TreeProcessing().setupItemData(pathList, self.treeModel.rootItem)
		self.sharedTree.setToolTip("<font color=red><b>Select path<br>for share it !</b></font>")
		self.sharedTree.setExpandsOnDoubleClick(True)
		self.sharedTree.setModel(self.treeModel)
		form.addWidget(self.sharedTree, 6, 0, 7, 2)

		self.addPathButton = QtGui.QPushButton('&Add')
		self.addPathButton.setMaximumWidth(75)
		self.connect(self.addPathButton, QtCore.SIGNAL('clicked()'), self.addPath)
		form.addWidget(self.addPathButton, 6, 2)

		self.delPathButton = QtGui.QPushButton('&Del')
		self.delPathButton.setMaximumWidth(75)
		self.connect(self.delPathButton, QtCore.SIGNAL('clicked()'), self.delPath)
		form.addWidget(self.delPathButton, 7, 2)

		self.okButton = QtGui.QPushButton('&Ok')
		self.okButton.setMaximumWidth(75)
		self.connect(self.okButton, QtCore.SIGNAL('clicked()'), self.ok)
		form.addWidget(self.okButton, 8, 2)

		self.cancelButton = QtGui.QPushButton('&Cancel')
		self.cancelButton.setMaximumWidth(75)
		self.connect(self.cancelButton, QtCore.SIGNAL('clicked()'), self.cancel)
		form.addWidget(self.cancelButton, 9, 2)

		self.setLayout(form)
		self.connect(self, QtCore.SIGNAL('refresh'), self.treeRefresh)

	def addPath(self):
		nameDir = QtGui.QFileDialog.getExistingDirectory(self, 'Path_to_', '~', QtGui.QFileDialog.ShowDirsOnly)
		if os.access(nameDir, os.R_OK) and os.access(nameDir, os.X_OK) :    ## and os.access(nameDir, os.W_OK) :
			# print nameDir
			#P = Parser()
			#doc = P.listPrepare(nameDir)
			#resultFileName = P.getResultFile(resultFileName = '_resultXMLFileOfAddSharedSource', \
			#																					doc = doc)
			#doc.unlink(); doc = None
			#del P; P = None
			#if resultFileName is not None :
			#	T = TreeProcessing()
			#	T.setupItemData([resultFileName], self.treeModel.rootItem)
			#	del T; T = None
			#	self.treeModel.reset()
			#	print gc.collect()
			#	print gc.get_referrers()
			#	del gc.garbage[:]
			#else :
			#	showHelp = ListingText("MSG: Available files not found in " + nameDir, self)
			#	showHelp.exec_()
			global TSThread
			TSThread = TreeSettingThread(self, nameDir, self.treeModel.rootItem)
			TSThread.start()
			gc.collect()
		else :
			showHelp = ListingText("MSG: uncorrect Path (access denied).", self)
			showHelp.exec_()

	def treeRefresh(self):
		self.treeModel.reset()

	def delPath(self):
		item = self.sharedTree.selectionModel().currentIndex()
		itemParent = item.internalPointer().parentItem
		delItem = itemParent.childItems
		delItem.remove(item.internalPointer())
		self.sharedTree.reset()
		print gc.collect()
		print gc.get_referrers()
		del gc.garbage[:]

	def ok(self):
		#global FileNameList
		#doc = Document()
		#doc.appendChild(self.treeModel.treeDataToXML(self.treeModel.rootItem))
		#print doc.toprettyxml()
		#del FileNameList
		#doc.unlink()
		#del doc
		print gc.collect()
		print gc.get_referrers()
		del gc.garbage[:]

	def cancel(self):
		print gc.collect()
		print gc.get_referrers()
		del gc.garbage[:]
		self.done(0)

	def closeEvent(self, event):
		event.ignore()
		self.done(0)

class ButtonPanel(QtGui.QWidget):
	def __init__(self, Obj_, job_key = None, parent = None):
		QtGui.QWidget.__init__(self, parent)

		self.Obj = Obj_

		self.layout = QtGui.QVBoxLayout()
		self.layout.addStretch(1)

		self.addButton = QtGui.QPushButton(QtCore.QString('Add'))
		self.addButton.setToolTip('Add Item to ItemList\nof Shared Source')
		self.connect(self.addButton, QtCore.SIGNAL('clicked()'), self.addItem)
		self.layout.addWidget(self.addButton)

		self.delButton = QtGui.QPushButton(QtCore.QString('Del'))
		self.delButton.setToolTip('Delete Item from ItemList\nof Shared Source')
		self.connect(self.delButton, QtCore.SIGNAL('clicked()'), self.addItem)
		self.layout.addWidget(self.delButton)

		self.upLoadButton = QtGui.QPushButton(QtCore.QString('Up'))
		self.upLoadButton.setToolTip('UpLoad ItemList\nof Shared Source')
		self.connect(self.upLoadButton, QtCore.SIGNAL('clicked()'), self.upLoad)
		self.layout.addWidget(self.upLoadButton)

		self.setLayout(self.layout)

	def addItem(self):
		pass

	def upLoad(self):
		QtGui.QApplication.postEvent(self.Obj, QtCore.QEvent(1010))
		pass

class BoxLayout(QtGui.QWidget):
	def __init__(self, Obj_ = None, job_key = None, parent = None):
		QtGui.QWidget.__init__(self, parent)

		self.setWindowTitle('box layout')

		self.boxTable = Obj_(job_key)

		hbox = QtGui.QHBoxLayout()
		hbox.addStretch(1)

		vbox = QtGui.QVBoxLayout()
		vbox.addStretch(1)
		vbox.addLayout(hbox)

		hbox.addWidget(self.boxTable)

		self.setLayout(vbox)

class ListingText(QtGui.QDialog):
	def __init__(self, path_, parent = None):
		QtGui.QDialog.__init__(self, parent)

		self.setWindowTitle('LightMight Message')
		self.setWindowIcon(QtGui.QIcon('../icons/tux_partizan.png'))

		browseText = QtGui.QTextEdit()
		browseText.setReadOnly(True)

		if path_[:3] != 'MSG':
			f = open(path_,'rU')
			data_ = f.readlines()
			f.close()
			raw_data = string.join(data_)
			megadata = QtCore.QString.fromUtf8(raw_data)
			browseText.setText(megadata)
			width_ = '450'
		else:
			path_ = QtCore.QString.fromUtf8(path_)
			browseText.setText(path_)
			width_ = '750'

		form = QtGui.QGridLayout()
		form.addWidget(browseText,0,0)
		self.setLayout(form)
		self.resize(int(width_, 10), 100)

	def closeEvent(self, event):
		event.ignore()
		self.done(0)

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

			P = Parser()
			doc = P.listPrepare(self.nameDir)
			resultFileName = P.getResultFile(resultFileName = '_resultXMLFileOfAddSharedSource', \
																								doc = doc)
			doc.unlink(); doc = None
			del P; P = None
			if resultFileName is not None :
				T = TreeProcessing()
				T.setupItemData([resultFileName], self.rootItem)
				del T; T = None
				print gc.collect()
				print gc.get_referrers()
				del gc.garbage[:]
			else :
				showHelp = ListingText("MSG: Available files not found in " + nameDir, self)
				showHelp.exec_()

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

class Box(QtGui.QWidget):
	def __init__(self, Obj_, job_key = None, parent = None):
		QtGui.QWidget.__init__(self, parent)

		self.Obj = Obj_
		self.layout = QtGui.QGridLayout()

		self.userList = QtGui.QListWidget()
		self.userList.setMaximumWidth(250)
		#self.userList.setMinimumSize(100, 75)
		self.userList.setToolTip('Users in Web')
		self.layout.addWidget(self.userList, 0, 0)

		pathList = ['result1', 'result2', 'result3']
		self.treeModel = TreeModel('Name', 'Description', parent = self)
		self.sharedTree = QtGui.QTreeView()
		#self.sharedTree.setRootIndex(treeModel.index(0, 0))
		self.sharedTree.setRootIsDecorated(True)
		TreeProcessing().setupItemData(pathList, self.treeModel.rootItem)
		self.sharedTree.setToolTip('Shared Source')
		self.sharedTree.setExpandsOnDoubleClick(True)
		self.sharedTree.setModel(self.treeModel)
		self.layout.addWidget(self.sharedTree, 0, 1)

		self.buttunPanel = BoxLayout(ButtonPanel, self.Obj)
		self.buttunPanel.setMaximumWidth(100)
		self.layout.addWidget(self.buttunPanel, 0, 2)

		self.setLayout(self.layout)

#os.system('cd $HOME && xauth merge /dev/shm/dsa && rm /dev/shm/dsa')
gc.enable()
gc.set_debug(gc.DEBUG_UNCOLLECTABLE)
name_ = os.path.basename(sys.argv[0])
#print sys.argv[0][:-len(name_)]
os.chdir(sys.argv[0][:-len(name_)])
createStructure()
GeneralLOCK = QtCore.QMutex()
TSThread = TreeSettingThread()
app = QtGui.QApplication(sys.argv)
main = MainWindow()
main.show()
sys.exit(app.exec_())
