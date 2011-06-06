# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
from Box import Box
from ServerSettingsShield import ServerSettingsShield
from ClientSettingsShield import ClientSettingsShield
from ListingText import ListingText
from AvahiTools import AvahiBrowser, AvahiService
from serv import ServerDaemon
from Functions import *
from ToolsThread import ToolsThread
from TreeProc import TreeModel
from PathToTree import SharedSourceTree2XMLFile
from TreeProcess import TreeProcessing
import shutil, os.path

class MainWindow(QtGui.QMainWindow):
	def __init__(self, parent = None):
		QtGui.QMainWindow.__init__(self, parent)

		self.serverState = ''
		self.currentRemoteServerState = ''
		self.currentRemoteServerAddr = ''
		self.currentRemoteServerPort = ''
		self.jobCount = 0
		self.commonSetOfSharedSource = {}

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
		self.connect(self.exit_, QtCore.SIGNAL('triggered()'), self._close)

		listHelp = QtGui.QAction(QtGui.QIcon('../icons/help.png'),'&About LightMight', self)
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
		self.connect(exit_tray, QtCore.SIGNAL('triggered()'), self._close)
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
		self.initServer()
		self.initAvahiTools()

	def initAvahiTools(self):
		self.initAvahiBrowser()
		self.initAvahiService()

	def initAvahiBrowser(self):
		if 'avahiBrowser' in dir(self) :
			self.avahiBrowser.__del__(); self.avahiBrowser = None
			#self.menuTab.userList.clear()
		self.avahiBrowser = AvahiBrowser(self.menuTab)

	def initAvahiService(self):
		if 'avahiService' in dir(self) :
			self.avahiService.__del__(); self.avahiService = None
		name_ = InitConfigValue(self.Settings, 'ServerName', 'Own Avahi Server')
		self.avahiService = AvahiService(self.menuTab, name = name_, port = self.server_port)

	def initServer(self, sharedSourceTree = None):
		if 'serverThread' in dir(self) :
			treeModel = sharedSourceTree
			firstRun = False
			self.serverThread = None
		else :
			treeModel = TreeModel('Name', 'Description')
			firstRun = True

		self.server_port = getFreePort(int(InitConfigValue(self.Settings, 'MinPort', '34000')), \
										int(InitConfigValue(self.Settings, 'MaxPort', '34100')))
		print self.server_port, 'free'
		self.serverThread = ToolsThread(ServerDaemon( ('', self.server_port), \
										self.commonSetOfSharedSource, self ), parent = self)

		""" должен сохранить результат как файл для передачи на запрос клиентов """
		if firstRun :
			if os.path.exists(os.path.expanduser('~/.config/LightMight/lastSharedSource')) :
				shutil.move(os.path.expanduser('~/.config/LightMight/lastSharedSource'), \
							'/dev/shm/LightMight/server/sharedSource_' + self.serverState)
			else :
				S = SharedSourceTree2XMLFile('sharedSource_' + self.serverState, treeModel.rootItem)
				S.__del__(); S = None
		else :
			S = SharedSourceTree2XMLFile('sharedSource_' + self.serverState, treeModel.rootItem)
			S.__del__(); S = None
		""" создать словарь соответствия {number : fileName}
		"""
		treeModel = TreeModel('Name', 'Description')		## cleaned treeModel.rootItem
		TreeProcessing().setupItemData(['/dev/shm/LightMight/server/sharedSource_' + self.serverState], \
										treeModel.rootItem)
		TreeProcessing().getCommonSetOfSharedSource(treeModel.rootItem, self.commonSetOfSharedSource)

		self.serverThread.start()
		if 'avahiService' in dir(self) :
			self.avahiService.__del__(); self.avahiService = None
		name_ = InitConfigValue(self.Settings, 'ServerName', 'Own Avahi Server')
		self.avahiService = AvahiService(self.menuTab, name = name_, port = self.server_port)

	def customEvent(self, event):
		if event.type() == 1010 :
			self.jobCount += 1
			job = QtCore.QProcess()
			if self.menuTab.userList.currentItem() is None :
				info = 'Empty Job'
			else :
				info = self.menuTab.userList.currentItem().toolTip()
			""" посчитать объём загрузок, создать файл с данными соответствия путей
				и ключей в self.commonSetOfSharedSource сервера
			"""
			nameMaskFile = randomString(24)
			with open('/dev/shm/LightMight/client/' + nameMaskFile, 'a') as handler :
				downLoadSize = \
					TreeProcessing().getCommonSetOfSharedSource(self.menuTab.treeModel.rootItem, \
																None, \
																checkItem = True, \
																f = handler)[1]
			print self.currentRemoteServerState, self.currentRemoteServerAddr, self.currentRemoteServerPort
			""" запуск клиента """
			pid, start = job.startDetached('/usr/bin/python', \
						 (QtCore.QStringList()	<< './DownLoadClient.py' \
												<< nameMaskFile \
												<< str(downLoadSize) \
												<< str(self.jobCount) \
												<< self.currentRemoteServerState \
												<< self.currentRemoteServerAddr \
												<< str(self.currentRemoteServerPort) \
												<< info), \
						 os.getcwd())
		elif event.type() == 1011 :
			pass

	def showBase(self): pass

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
		showHelp = ListingText( "MSG: LightMight.help", self )
		showHelp.exec_()

	def showClientSettingsShield(self):
		_ClientSettingsShield = ClientSettingsShield(self)
		_ClientSettingsShield.exec_()

	def showServerSettingsShield(self):
		_ServerSettingsShield = ServerSettingsShield(self)
		_ServerSettingsShield.exec_()

	def _close(self):
		#print '/dev/shm/LightMight/server/sharedSource_' + self.serverState, ' close'
		if InitConfigValue(self.Settings, 'SaveLastStructure', 'False') == 'True' :
			#print True
			if os.path.exists('/dev/shm/LightMight/server/sharedSource_' + self.serverState) :
				#print 'Exist'
				shutil.move('/dev/shm/LightMight/server/sharedSource_' + self.serverState, \
							os.path.expanduser('~/.config/LightMight/lastSharedSource'))
			else :
				#print 'not Exist'
				pass
		shutil.rmtree('/dev/shm/LightMight', ignore_errors = True)
		self.close()

	def closeEvent(self, event):
		self._close()
