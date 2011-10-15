# -*- coding: utf-8 -*-

import shutil, os.path, string, sys
from PyQt4 import QtGui, QtCore
from Box import Box
from Wait import SetupTree
from ServerSettingsShield import ServerSettingsShield
from ClientSettingsShield import ClientSettingsShield
from CommonSettingsShield import CommonSettingsShield
from ListingText import ListingText
from DataCache import DataCache
from StatusBar import StatusBar

if sys.platform == 'win32':
	from BonjourTools import AvahiBrowser, AvahiService
	print 'Platform : Win'
else:
	if sys.platform == 'darwin':
		print 'Platform : Apple'
	else :
		print 'Platform : Linux'
	from AvahiTools import AvahiBrowser, AvahiService
#from BonjourTools import AvahiBrowser, AvahiService
	
from serv import ServerDaemon
from Functions import *
from ToolsThread import ToolsThread
from TreeProc import TreeModel
from PathToTree import SharedSourceTree2XMLFile
from TreeProcess import TreeProcessing
from mcastSender import _send_mcast as Sender
from UdpClient import UdpClient

class MainWindow(QtGui.QMainWindow):
	# custom signals
	errorString = QtCore.pyqtSignal(str)
	commonSet = QtCore.pyqtSignal(dict)
	uploadSignal = QtCore.pyqtSignal(QtCore.QString)
	contactMessage = QtCore.pyqtSignal(QtCore.QString, QtCore.QString)
	changeConnectState = QtCore.pyqtSignal(QtCore.QString)
	def __init__(self, parent = None):
		QtGui.QMainWindow.__init__(self, parent)

		self.pathPref = pathPrefix()

		self.serverState = ''
		self.currentRemoteServerState = ''
		self.currentRemoteServerAddr = ''
		self.currentRemoteServerPort = ''
		self.jobCount = 0
		self.commonSetOfSharedSource = {}
		self.USERS = {}

		#self.resize(450, 350)
		self.setWindowTitle('LightMight')
		self.setWindowIcon(QtGui.QIcon('../icons/tux_partizan.png'))

		self.Settings = QtCore.QSettings('LightMight','LightMight')
		self.avatarPath = InitConfigValue(self.Settings, 'AvatarPath', '')

		self.exit_ = QtGui.QAction(QtGui.QIcon('../icons/exit.png'), '&Exit', self)
		self.exit_.setShortcut('Ctrl+Q')
		self.exit_.setStatusTip('Exit application')
		self.connect(self.exit_, QtCore.SIGNAL('triggered()'), self._close)

		listHelp = QtGui.QAction(QtGui.QIcon('../icons/help.png'),'&About LightMight', self)
		listHelp.setStatusTip('Read help')
		self.connect(listHelp,QtCore.SIGNAL('triggered()'), self.showMSG)

		commonSettings = QtGui.QAction(QtGui.QIcon('../icons/help.png'),'&Common Settings', self)
		commonSettings.setStatusTip('Set avatars, use cache, etc.')
		self.connect(commonSettings, QtCore.SIGNAL('triggered()'), self.showCommonSettingsShield)

		serverSettings = QtGui.QAction(QtGui.QIcon('../icons/help.png'),'&Server Settings', self)
		serverSettings.setStatusTip('Set shared source, encrypt, etc.')
		self.connect(serverSettings, QtCore.SIGNAL('triggered()'), self.showServerSettingsShield)

		clientSettings = QtGui.QAction(QtGui.QIcon('../icons/help.png'),'&Client Settings', self)
		clientSettings.setStatusTip('Set the download path, etc.')
		self.connect(clientSettings, QtCore.SIGNAL('triggered()'), self.showClientSettingsShield)

		self.statusBar = StatusBar(self)
		self.setStatusBar(self.statusBar)

		menubar = self.menuBar()

		file_ = menubar.addMenu('&File')
		"""file_.addAction(self.base_)
		file_.addAction(self.create_struct)
		"""
		file_.addAction(self.exit_)

		set_ = menubar.addMenu('&Settings')
		set_.addAction(commonSettings)
		set_.addAction(serverSettings)
		set_.addAction(clientSettings)

		help_ = menubar.addMenu('&Help')
		help_.addAction(listHelp)

		self.menuTab = Box(self)
		self.setCentralWidget(self.menuTab)

		self.trayIconMenu = QtGui.QMenu(self)
		show_hide = self.trayIconMenu.addAction(QtGui.QIcon('../icons/tux_partizan.png'), 'Hide / Show')
		self.connect(show_hide, QtCore.SIGNAL('triggered()'), self.show_n_hide)
		help_tray = self.trayIconMenu.addAction(QtGui.QIcon('../icons/help.png'), 'Help')
		self.connect(help_tray, QtCore.SIGNAL('triggered()'), self.showMSG)
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

		self.errorString.connect(self.showMSG)
		self.commonSet.connect(self.preProcessingComplete)
		self.uploadSignal.connect(self.uploadTask)
		self.contactMessage.connect(self.receiveBroadcastMessage)
		#self.changeConnectState.connect()
		self.timer = QtCore.QTimer()
		self.timer.setSingleShot(True)
		self.timer.timeout.connect(self.initServices)
		self.timer.start(1000)

	'''
	data =  0/1/R(offline/online/reinit)<separator>
			remoteServerName<separator>
			address<separator>
			port<separator>
			Encoding<separator>
			Status<separator>
			ShareInfo
	'''

	def receiveBroadcastMessage(self, data, addr):
		mark, name, addr_in_data, port, encode, state, info = data.split('<||>', QtCore.QString.KeepEmptyParts)
		''' check correct IP for local network '''
		if addr == addr_in_data :
			if mark == '1' : self.addNewContact(name, addr, port, encode, state, False)
			elif mark == '0' : self.delContact(name, addr_in_data, port, encode, state)
			elif mark == 'R' : self.reInitRequest(name, addr, port, encode, state)
		else :
			''' check correct IP for internet '''
			pass

	def reInitRequest(self, name, addr, port, encode, state):
		 pass

	def delContact(self, name, addr, port, encode, state):
		print name, addr, port, encode, state , 'Must die!'
		if addr != None and port != None :
			contactExist = False
			for iter_ in self.USERS.iterkeys() :
				try :
					if self.USERS[iter_][1] == addr and self.USERS[iter_][2] == port :
						name = self.USERS[iter_][0]
						print 'Found contact:', name
						contactExist = True
						break
				except RuntimeError, err :
					print err
				finally : pass
			if not contactExist : return None
		else :
			addr = ''; port = ''
		item = self.menuTab.userList.findItems(name, \
				QtCore.Qt.MatchFlags(QtCore.Qt.MatchCaseSensitive))
		#print item, ' find list'
		if len(item) > 0 :
			for item_ in item :
				if item_.data(QtCore.Qt.AccessibleTextRole).toString() == addr + ':' + port :
					self.menuTab.userList.takeItem(self.menuTab.userList.row(item_))
					if str(addr + ':' + port) in self.USERS : del self.USERS[str(addr + ':' + port)]

	def addNewContact(self, name, addr, port, encode, state, avahi_method = True):
		''' check uniqualled contact (uniqual IP:port) '''
		if not avahi_method :
			for iter_ in self.USERS.iterkeys() :
				try :
					if self.USERS[iter_][1] == addr and self.USERS[iter_][2] == port :
						print 'Not uniqual contact(B):', self.USERS[iter_][0], \
														 self.USERS[iter_][1], \
														 self.USERS[iter_][2]
						''' add the check of optional data '''	## FIXME:
						return False
				except RuntimeError, err :
					print err
				finally : pass
			''' check uniqual name '''
			name_ = unicode(name)
			key = True
			while key :
				key = False
				for iter_ in self.USERS.iterkeys() :
					if self.USERS[iter_][0]  == name_ :
						name_ = name_.split('_')[0] + '_' + randomString(3)
						key = True;
						break
			name = name_
		else :
			''' check not uniqual name (avahi u. name > broadcast u. name) '''
			for iter_ in self.USERS.iterkeys() :
				try :
					if self.USERS[iter_][1] == addr and self.USERS[iter_][2] == port :
						print 'Not uniqual contact(A):', self.USERS[iter_][0], \
														 self.USERS[iter_][1], \
														 self.USERS[iter_][2]
						self.delContact(self.USERS[iter_][0], \
										self.USERS[iter_][1], \
										self.USERS[iter_][2], \
										None, None)
						break
				except RuntimeError, err :
					print err
				finally : pass
		new_item = QtGui.QListWidgetItem(name)
		new_item.setData(QtCore.Qt.AccessibleTextRole, QtCore.QVariant(addr + ':' + port))
		in_cashe, path_ = InCache(state)
		if in_cashe :
			head, tail = os.path.split(str(path_))
			new_item.setIcon(QtGui.QIcon(head + '/avatars/' + tail))
			new_item.setToolTip(toolTipsHTMLWrap(head + '/avatars/' + tail, \
								'name : ' + name + '<br>'\
								'\naddress : ' + addr + '<br>'\
								'\nport : ' + port + '<br>'\
								'\nEncoding : ' + encode + '<br>'\
								'\nServerState : ' + state))
		else :
			new_item.setToolTip(toolTipsHTMLWrap('/dev/shm/LightMight/cache/avatars/' + state, \
								'name : ' + name + '<br>'\
								'\naddress : ' + addr + '<br>'\
								'\nport : ' + port + '<br>'\
								'\nEncoding : ' + encode + '<br>'\
								'\nServerState : ' + state))
		self.menuTab.userList.addItem(new_item)
		""" Keys of USERS defined by "addr:port", because it uniqual property,
			but "state" may be not changed. In cache the important\exclusive role
			has the status of remote server.
		"""
		self.USERS[str(addr + ':' + port)] = (name, addr, port, encode, state, False)
		#print self.USERS
		return True

	def initServices(self):
		self.initServer()
		self.initAvahiTools()

	def initAvahiTools(self):
		self.initAvahiBrowser()
		#self.initAvahiService()

	def initAvahiBrowser(self):
		if 'avahiBrowser' in dir(self) :
			self.avahiBrowser.__del__(); self.avahiBrowser = None
			# stopping caching
			if 'cachingthread' in dir(self) :
				self.cachingThread._shutdown()
			self.menuTab.userList.clear()
		if 'udpClient' in dir(self) :
			self.udpClient.stop()
			self.udpClient.exit()
			self.udpClient = None
		if self.Settings.value('AvahiDetect', True).toBool() :
			print 'Use Avahi'
			self.avahiBrowser = AvahiBrowser(self.menuTab)
			self.avahiBrowser.start()
		if self.Settings.value('BroadcastDetect', True).toBool() :
			print 'Use Broadcast'
			self.udpClient = UdpClient(self)
			self.udpClient.start()
		if InitConfigValue(self.Settings, 'UseCache', 'False') == 'True' :
			print 'Use Cache'
			#self.cachingThread = DataCache(self.avahiBrowser.USERS, self)
			self.cachingThread = DataCache(self.USERS, self)
			self.cachingThread.start()

	def initAvahiService(self):
		if 'avahiService' in dir(self) :
			if '__del__' in dir(self.avahiService) : self.avahiService.__del__()
			self.avahiService = None
		name_ = InitConfigValue(self.Settings, 'ServerName', 'Own Avahi Server')
		if self.TLS :
			encode = 'Yes'
		else :
			encode = 'No'
		if self.Settings.value('AvahiDetect', True).toBool() :
			self.avahiService = AvahiService(self.menuTab, \
								name = name_, \
								port = self.server_port, \
								description = 'Encoding=' + encode + '.' + 'State=' + self.serverState)
			self.avahiService.start()
		if self.Settings.value('BroadcastDetect', True).toBool() :
			data = QtCore.QString('1' + '<||>' + \
								  name_ + '<||>' + \
								  getIP() + '<||>' + \
								  str(self.server_port) + '<||>' + \
								  encode + '<||>' + \
								  self.serverState + '<||>' + \
								  '*infoShare*')
			Sender(data)

	def initServer(self, sharedSourceTree = None, loadFile = None, previousState = ''):
		self.previousState = previousState
		self.menuTab.progressBar.show()
		if 'serverThread' in dir(self) :
			treeModel = sharedSourceTree
			firstRun = False
			self.serverThread = None
		else :
			treeModel = TreeModel('Name', 'Description')
			firstRun = True
		self.statusBar.clearMessage()
		self.statusBar.showMessage('Server offline')

		self.server_port = getFreePort(int(InitConfigValue(self.Settings, 'MinPort', '34000')), \
										int(InitConfigValue(self.Settings, 'MaxPort', '34100')))[1]
		#print self.server_port, 'free'
		certificatePath = InitConfigValue(self.Settings, 'PathToCertificate', '')
		#print str(certificatePath)
		if 'True' == InitConfigValue(self.Settings, 'UseTLS', 'False') and certificatePath != '' :
			self.TLS = True
		else :
			self.TLS = False
		#print self.TLS, '  <--- using TLS'
		self.serverThread = ToolsThread(\
										ServerDaemon( ('', self.server_port), \
													self.commonSetOfSharedSource, \
													self, \
													TLS = self.TLS, \
													cert = str(certificatePath)), \
										parent = self)

		""" должен сохранить результат как файл для передачи на запрос клиентов """
		if firstRun :
			if os.path.exists(os.path.expanduser('~/.config/LightMight/lastServerState')) :
				with open(os.path.expanduser('~/.config/LightMight/lastServerState'), 'rb') as f :
					self.serverState = f.read()
					self.serverThread.Obj.serverState = self.serverState
			if os.path.exists(os.path.expanduser('~/.config/LightMight/lastSharedSource')) :
				shutil.move(os.path.expanduser('~/.config/LightMight/lastSharedSource'), \
							self.pathPref + '/dev/shm/LightMight/server/sharedSource_' + self.serverState)
			else :
				S = SharedSourceTree2XMLFile('sharedSource_' + self.serverState, treeModel.rootItem)
				S.__del__(); S = None
		elif loadFile is not None :
			if not moveFile(loadFile, self.pathPref + '/dev/shm/LightMight/server/sharedSource_' + self.serverState, False) :
				S = SharedSourceTree2XMLFile('sharedSource_' + self.serverState, treeModel.rootItem)
				S.__del__(); S = None
		else :
			S = SharedSourceTree2XMLFile('sharedSource_' + self.serverState, treeModel.rootItem)
			S.__del__(); S = None

		""" creating match dictionary {number : fileName} """
		treeModel = TreeModel('Name', 'Description')		## cleaned treeModel.rootItem

		self.threadSetupTree = SetupTree(TreeProcessing(), \
										[self.pathPref + '/dev/shm/LightMight/server/sharedSource_' + self.serverState], \
										treeModel.rootItem, \
										self, \
										True, \
										self)
		self.threadSetupTree.start()

	def preProcessingComplete(self, commonSet = {}):
		self.commonSetOfSharedSource = commonSet
		#print len(self.commonSetOfSharedSource), ' commonSet.count '
		""" this for server commonSet """
		self.serverThread.Obj.commonSetOfSharedSource = commonSet
		self.serverThread.start()
		self.statusBar.clearMessage()
		self.statusBar.showMessage('Server online')
		'''
		if 'avahiService' in dir(self) :
			if '__del__' in dir(self.avahiService) : self.avahiService.__del__()
			self.avahiService = None
		name_ = InitConfigValue(self.Settings, 'ServerName', 'Own Avahi Server')
		if self.TLS :
			encode = 'Yes'
		else :
			encode = 'No'
		if self.Settings.value('AvahiDetect', True).toBool() :
			self.avahiService = AvahiService(self.menuTab, \
								name = name_, \
								port = self.server_port, \
								description = 'Encoding=' + encode + '.' + 'State=' + self.serverState)
			self.avahiService.start()
		if self.Settings.value('BroadcastDetect', True).toBool() :
			data = QtCore.QString('1' + '<||>' + \
								  name_ + '<||>' + \
								  getIP() + '<||>' + \
								  str(self.server_port) + '<||>' + \
								  encode + '<||>' + \
								  self.serverState + '<||>' + \
								  '*infoShare*')
			Sender(data)'''
		self.initAvahiBrowser()
		self.initAvahiService()
		self.menuTab.progressBar.hide()

	def uploadTask(self, info):
			Info = unicode(info)
			job = QtCore.QProcess()
			self.jobCount += 1
			""" посчитать объём загрузок, создать файл с данными соответствия путей
				и ключей в self.commonSetOfSharedSource сервера
			"""
			nameMaskFile = randomString(24)
			with open(self.pathPref + '/dev/shm/LightMight/client/' + nameMaskFile, 'a') as handler :
				downLoadSize = \
					TreeProcessing().getCommonSetOfSharedSource(self.menuTab.treeModel.rootItem, \
																None, \
																checkItem = True, \
																f = handler)[1]
			serverState = Info.partition('ServerState : ')[2].partition('</td>')[0].partition('\n')[0].replace('<br>', '')
			serverAddr = Info.partition('address : ')[2].partition('\n')[0].partition('<br>')[0]
			serverPort = Info.partition('port : ')[2].partition('\n')[0].partition('<br>')[0]
			description = Info.partition('Shared Source :')[0]
			encoding = Info.partition('Encoding : ')[2].partition('\n')[0].partition('<br>')[0]
			if encoding == 'Yes' :
				encode = 'True'
			else :
				encode = 'False'
			"""
			print   '\n\n!!!!', serverState, \
					'\n\n!!!!', serverAddr, \
					'\n\n!!!!', serverPort, \
					'\n\n!!!!', description, \
					'\n\n!!!!', encoding, '  info'
			"""
			""" task run """
			pid, start = job.startDetached('/usr/bin/python', \
						 (QtCore.QStringList()	<< './DownLoadClient.py' \
												<< nameMaskFile \
												<< str(downLoadSize) \
												<< str(self.jobCount) \
												<< serverState \
												<< serverAddr \
												<< serverPort \
												<< description \
												<< encode), \
						 os.getcwd())

	def show_n_hide(self):
		if self.isVisible():
			self.hide()
			self.menuTab.sharedTree.hide()
		else:
			self.show()
			#self.menuTab.sharedTree.show()

	def trayIconClicked(self, reason):
		if reason == QtGui.QSystemTrayIcon.DoubleClick :
			self.show_n_hide()

	def showMSG(self, str_ = "README"):
		if str_ == "README" :
			STR_ = '../../README'
		else :
			STR_ = "MSG: " + str_
		showHelp = ListingText(STR_, self)
		showHelp.exec_()

	def showCommonSettingsShield(self):
		_CommonSettingsShield = CommonSettingsShield(self)
		_CommonSettingsShield.exec_()

	def showClientSettingsShield(self):
		_ClientSettingsShield = ClientSettingsShield(self)
		_ClientSettingsShield.exec_()

	def showServerSettingsShield(self):
		_ServerSettingsShield = ServerSettingsShield(self)
		_ServerSettingsShield.exec_()

	def saveCache(self):
		Once = True
		limitCache = int(InitConfigValue(self.Settings, 'CacheSize', '100')) * 10000
		prefPath = self.pathPref + '/dev/shm/LightMight/cache/'
		prefPathForAvatar = prefPath + 'avatars/'
		prefPathInStationar = self.pathPref + os.path.expanduser('~/.cache/LightMight/')
		prefPathInStationarForAvatar = prefPathInStationar + 'avatars/'
		if os.path.exists(self.pathPref + '/dev/shm/LightMight/cache') :
			currentSize = getFolderSize(prefPathInStationar)
			print currentSize, ':'
			listingCache = os.listdir(self.pathPref + '/dev/shm/LightMight/cache')
			for name in listingCache :
				path = prefPath + name
				pathInStationarCache = prefPathInStationar + name
				if os.path.isfile(path) and not os.path.isfile(pathInStationarCache) :
					if moveFile(path, pathInStationarCache) :
						currentSize += os.path.getsize(pathInStationarCache)
					if moveFile(prefPathForAvatar + name, prefPathInStationarForAvatar + name) :
						currentSize += os.path.getsize(prefPathInStationarForAvatar + name)
					print currentSize
					if currentSize >= limitCache :
						print 'cache`s limit is reached'
						self.showMSG('cache`s limit is reached')
						break
					elif Once and currentSize >= limitCache*4/5 :
						Once = False
						self.showMSG('cache is reached more then 80% :\n' + \
									 str(currentSize) + \
									 ' from ' + \
									 str(limitCache))

	def _close(self):
		#print '/dev/shm/LightMight/server/sharedSource_' + self.serverState, ' close'
		if InitConfigValue(self.Settings, 'UseCache', 'True') == 'True' : self.saveCache()
		if InitConfigValue(self.Settings, 'SaveLastStructure', 'True') == 'True' :
			#print True
			if os.path.exists(self.pathPref + '/dev/shm/LightMight/server/sharedSource_' + self.serverState) :
				#print 'Exist'
				shutil.move(self.pathPref + '/dev/shm/LightMight/server/sharedSource_' + self.serverState, \
							os.path.expanduser('~/.config/LightMight/lastSharedSource'))
				with open(os.path.expanduser('~/.config/LightMight/lastServerState'), 'wb') as f :
					f.write(self.serverState)
			else :
				#print 'not Exist'
				pass
		shutil.rmtree(self.pathPref + '/dev/shm/LightMight', ignore_errors = True)
		self.close()

	def closeEvent(self, event):
		self._close()
