# -*- coding: utf-8 -*-

import shutil, os.path, string, sys, os
from PyQt4 import QtGui, QtCore
from Functions import *
from Modules import ModuleExist
from Box import Box
from Wait import SetupTree
from ServerSettingsShield import ServerSettingsShield
from ClientSettingsShield import ClientSettingsShield
from CommonSettingsShield import CommonSettingsShield
#from ColorSettingsShield import ColorSettingsShield
from ListingText import ListingText
from DataCache import DataCache
from StatusBar import StatusBar

if Path.platform == 'win':
	if ModuleExist.AvahiAvailable :
		from BonjourTools import AvahiBrowser, AvahiService
else:
	if ModuleExist.AvahiAvailable :
		from AvahiTools import AvahiBrowser, AvahiService

from serv import ServerDaemon
from ToolsThread import ToolsThread
from TreeProc import TreeModel
from PathToTree import SharedSourceTree2XMLFile
from TreeProcess import TreeProcessing
from mcastSender import _send_mcast as Sender
from UdpClient import UdpClient
from clnt import xr_client
from Policy  import Policy
from ConfirmRequest import ConfirmRequest

class MainWindow(QtGui.QMainWindow):
	# custom signals
	errorString = QtCore.pyqtSignal(str)
	commonSet = QtCore.pyqtSignal(dict)
	startServer = QtCore.pyqtSignal()
	uploadSignal = QtCore.pyqtSignal(QtCore.QString)
	contactMessage = QtCore.pyqtSignal(QtCore.QString, QtCore.QString)
	changeConnectState = QtCore.pyqtSignal()
	cacheDown = QtCore.pyqtSignal()
	serverDown = QtCore.pyqtSignal(str)
	serverDOWN = QtCore.pyqtSignal(str, str)
	initServeR = QtCore.pyqtSignal(TreeModel, str, str, bool)
	reinitServer = QtCore.pyqtSignal()
	setAccess = QtCore.pyqtSignal(str)
	def __init__(self, parent = None):
		QtGui.QMainWindow.__init__(self, parent)

		self.serverState = ''
		self.jobCount = 0
		self.commonSetOfSharedSource = {}
		self.USERS = {}
		self.SEP = os.sep

		#self.resize(450, 350)
		self.setWindowTitle('LightMight')
		self.setWindowIcon(QtGui.QIcon('..' + self.SEP + 'icons' + self.SEP + 'tux_partizan.png'))

		self.Settings = QtCore.QSettings('LightMight','LightMight')
		self.Policy = Policy(self)
		self.avatarPath = InitConfigValue(self.Settings, 'AvatarPath', '')

		self.exit_ = QtGui.QAction(QtGui.QIcon('..' + self.SEP + 'icons' + self.SEP + 'exit.png'), '&Exit', self)
		self.exit_.setShortcut('Ctrl+Q')
		self.exit_.setStatusTip('Exit application')
		self.connect(self.exit_, QtCore.SIGNAL('triggered()'), self._close)

		listHelp = QtGui.QAction(QtGui.QIcon('..' + self.SEP + 'icons' + self.SEP + 'help.png'),'&About LightMight', self)
		listHelp.setStatusTip('Read help')
		self.connect(listHelp,QtCore.SIGNAL('triggered()'), self.showMSG)

		commonSettings = QtGui.QAction(QtGui.QIcon('..' + self.SEP + 'icons' + self.SEP + 'help.png'),'&Common Settings', self)
		commonSettings.setStatusTip('Set avatars, use cache, etc.')
		self.connect(commonSettings, QtCore.SIGNAL('triggered()'), self.showCommonSettingsShield)

		serverSettings = QtGui.QAction(QtGui.QIcon('..' + self.SEP + 'icons' + self.SEP + 'help.png'),'&Server Settings', self)
		serverSettings.setStatusTip('Set shared source, encrypt, etc.')
		self.connect(serverSettings, QtCore.SIGNAL('triggered()'), self.showServerSettingsShield)

		clientSettings = QtGui.QAction(QtGui.QIcon('..' + self.SEP + 'icons' + self.SEP + 'help.png'),'C&lient Settings', self)
		clientSettings.setStatusTip('Set the download path, etc.')
		self.connect(clientSettings, QtCore.SIGNAL('triggered()'), self.showClientSettingsShield)

		#colorSettings = QtGui.QAction(QtGui.QIcon('..' + self.SEP + 'icons' + self.SEP + 'help.png'),'Color&Font and Background', self)
		#colorSettings.setStatusTip('Set font color & background.')
		#self.connect(colorSettings, QtCore.SIGNAL('triggered()'), self.showColorSettingsShield)

		self.statusBar = StatusBar(self)
		self.setStatusBar(self.statusBar)

		menubar = self.menuBar()

		file_ = menubar.addMenu('&File')
		file_.addAction(self.exit_)

		set_ = menubar.addMenu('&Settings')
		set_.addAction(commonSettings)
		set_.addAction(serverSettings)
		set_.addAction(clientSettings)
		#set_.addAction(colorSettings)

		help_ = menubar.addMenu('&Help')
		help_.addAction(listHelp)

		self.menuTab = Box(self)
		self.setCentralWidget(self.menuTab)

		self.trayIconMenu = QtGui.QMenu(self)
		show_hide = self.trayIconMenu.addAction(QtGui.QIcon('..' + self.SEP + 'icons' + self.SEP + 'tux_partizan.png'), 'Hide / Show')
		self.connect(show_hide, QtCore.SIGNAL('triggered()'), self.show_n_hide)
		help_tray = self.trayIconMenu.addAction(QtGui.QIcon('..' + self.SEP + 'icons' + self.SEP + 'help.png'), 'Help')
		self.connect(help_tray, QtCore.SIGNAL('triggered()'), self.showMSG)
		exit_tray = self.trayIconMenu.addAction(QtGui.QIcon('..' + self.SEP + 'icons' + self.SEP + 'exit.png'), '&Exit')
		self.connect(exit_tray, QtCore.SIGNAL('triggered()'), self._close)
		self.trayIconPixmap = QtGui.QPixmap('..' + self.SEP + 'icons' + self.SEP + 'tux_partizan.png') # файл иконки
		self.trayIcon = QtGui.QSystemTrayIcon(self)
		self.trayIcon.setToolTip('LightMight')
		self.trayIcon.setContextMenu(self.trayIconMenu)
		self.trayIcon.setIcon(QtGui.QIcon(self.trayIconPixmap))
		self.connect(self.trayIcon, QtCore.SIGNAL("activated(QSystemTrayIcon::ActivationReason)"), \
																			self.trayIconClicked)
		self.trayIcon.show()

		self.errorString.connect(self.showMSG)
		self.commonSet.connect(self.preProcessingComplete)
		self.startServer.connect(self.initServerComplete)
		self.uploadSignal.connect(self.uploadTask)
		self.contactMessage.connect(self.receiveBroadcastMessage)
		self.changeConnectState.connect(self.initAvahiBrowser)
		self.cacheDown.connect(self.cacheS)
		self.initServeR.connect(self.initServer)
		self.reinitServer.connect(self.initServer)
		self.serverDown.connect(self.menuTab.preStartServer)
		self.setAccess.connect(self.confirmAction)
		self.timer = QtCore.QTimer()
		self.timer.setSingleShot(True)
		self.timer.timeout.connect(self.initServer)
		self.timer.start(1000)

	'''
	data =  0/1/A/R(offline/online/answer/reinit)<separator>
			remoteServerName<separator>
			address<separator>
			port<separator>
			Encoding<separator>
			Status<separator>
			ShareInfo
	'''

	def receiveBroadcastMessage(self, data, addr):
		if data.count('<||>') != 6 : return None	## ignore non-standart packets
		mark, name, addr_in_data, port, encode, state, info = data.split('<||>', QtCore.QString.KeepEmptyParts)
		#print 'New request :', mark, QtCore.QString().fromUtf8(name), addr_in_data, port, encode, state, info
		''' check correct IP for local network '''
		if addr == addr_in_data :
			if   mark == '1' : self.sentAnswer(addr); self.addNewContact(name, addr, port, encode, state, None, False)
			elif mark == '0' : self.delContact(name, addr_in_data, port, encode, state)
			elif mark == 'A' : self.addNewContact(name, addr, port, encode, state, None, False)
			elif mark == 'R' : self.reInitRequest(name, addr, port, encode, state)

	def sentAnswer(self, addr):
		name_ = InitConfigValue(self.Settings, 'ServerName', 'Own Avahi Server')
		if self.TLS :
			encode = 'Yes'
		else :
			encode = 'No'
		data = QtCore.QString('A' + '<||>' + \
							  name_ + '<||>' + \
							  self.server_addr + '<||>' + \
							  str(self.server_port) + '<||>' + \
							  encode + '<||>' + \
							  self.serverState + '<||>' + \
							  '*infoShare*')
		Sender(data, addr)

	def reInitRequest(self, name, addr, port, encode, state):
		 pass

	def delContact(self, name, addr, port, encode, state):
		#print [QtCore.QString().fromUtf8(name), addr, port, encode, state] , 'Must die!'
		if addr != None and port != None :
			key = str(addr + ':' + port)
			if key in self.USERS :
				for i in xrange(self.menuTab.userList.count()) :
					item_ = self.menuTab.userList.item(i)
					if item_ is not None and item_.data(QtCore.Qt.AccessibleTextRole).toList()[0] == key :
						self.menuTab.userList.takeItem(self.menuTab.userList.row(item_))
						if key in self.USERS :
							del self.USERS[key]
							#print key, 'deleted'
						_addr = str(addr)
						if _addr in self.serverThread.Obj.currentSessionID :
							del self.serverThread.Obj.currentSessionID[_addr]
							#print _addr, 'deletedDD'
						break
		else :
			item = self.menuTab.userList.findItems(name, \
					QtCore.Qt.MatchFlags(QtCore.Qt.MatchCaseSensitive))
			domain = str(state)
			#print item, ' find list'
			if len(item) > 0 :
				for item_ in item :
					data = item_.data(QtCore.Qt.AccessibleTextRole).toList()
					if data[1].toBool() :
						# because avahi & broadcast reinit together
						if domain in data[2:] :
							self.menuTab.userList.takeItem(self.menuTab.userList.row(item_))
							key = str(data[0].toString())
							if key in self.USERS :
								del self.USERS[key]
								str_ = key.split(':')
								self.delContact(None, str_[0], str_[1], None, None)
								#print key, 'deleted'
		#print 'DEL down'

	def addNewContact(self, name, addr, port, encode, state, domain, avahi_method = True):
		#print QtCore.QString().fromUtf8(name), addr, port, 'new contact'
		key = str(addr + ':' + port)
		''' check uniqualled contact (uniqual IP:port) '''
		if not avahi_method :
			if key in self.USERS :
				'''
				print 'Not uniqual contact(B):', unicode(self.USERS[iter_][0]), \
												 self.USERS[iter_][1], \
												 self.USERS[iter_][2]
				'''
				return False
		else :
			''' check not uniqual name (avahi u. name > broadcast u. name) '''
			if key in self.USERS :
				'''
				print 'Not uniqual contact(A):', unicode(self.USERS[iter_][0]), \
												 self.USERS[iter_][1], \
												self.USERS[iter_][2]
				'''
				for i in xrange(self.menuTab.userList.count()) :
					item_ = self.menuTab.userList.item(i)
					data = item_.data(QtCore.Qt.AccessibleTextRole).toList()
					if domain not in data[2:] :
						data.append(domain)
						data[1] = avahi_method
						item_.setData(QtCore.Qt.AccessibleTextRole, QtCore.QVariant(data))
					return True
		new_item = QtGui.QListWidgetItem(name)
		new_item.setData(QtCore.Qt.AccessibleTextRole, QtCore.QVariant([key, avahi_method, domain]))
		in_cashe, path_ = InCache(state)
		if in_cashe :
			head, tail = os.path.split(str(path_))
			path_ = os.path.join(head, 'avatars', tail)
		else :
			path_ = Path.tempAvatar(state)

		new_item.setIcon(QtGui.QIcon(path_))
		new_item.setToolTip(toolTipsHTMLWrap(path_, \
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
		self.USERS[key] = (name, addr, port, encode, state, False)
		#print self.USERS
		return True

	def preinitAvahiBrowser(self):
		#if 'avahiBrowser' in dir(self) :	## multiply contact
		#	if '__del__' in dir(self.avahiBrowser) : self.avahiBrowser.__del__(); self.avahiBrowser = None
		# stopping caching
		if 'cachingThread' in dir(self) :
			self.cachingThread._shutdown()
			self.cachingThread.quit()
			del self.cachingThread
		if 'udpClient' in dir(self) :
			self.udpClient.stop()
		else : self.initAvahiBrowser()

	def cacheS(self):
		print 'Cache down signal received'

	def initAvahiBrowser(self, *args):
		if self.Settings.value('AvahiDetect', True).toBool() and 'avahiBrowser' not in dir(self):
			print 'Use Avahi'
			if ModuleExist.AvahiAvailable and 'avahiBrowser' not in dir(self) :
				self.avahiBrowser = AvahiBrowser(self.menuTab)
				self.avahiBrowser.start()
		if InitConfigValue(self.Settings, 'UseCache', 'False') == 'True' :
			print 'Use Cache'
			self.cachingThread = DataCache(self.USERS, self)
			self.cachingThread.start()
		if self.Settings.value('BroadcastDetect', True).toBool() :
			print 'Use Broadcast'
			self.udpClient = UdpClient(self)
			self.udpClient.start()
		else : self.initAvahiService()

	def initAvahiService(self):
		if 'avahiService' in dir(self) :
			if '__del__' in dir(self.avahiService) : self.avahiService.__del__()
			self.avahiService = None
		name_ = InitConfigValue(self.Settings, 'ServerName', 'Own Avahi Server')
		if self.TLS :
			encode = 'Yes'
		else :
			encode = 'No'
		if ModuleExist.AvahiAvailable and self.Settings.value('AvahiDetect', True).toBool() :
			self.avahiService = AvahiService(self.menuTab, \
								name = name_, \
								port = self.server_port, \
								description = 'Encoding=' + encode + '.' + 'State=' + self.serverState)
			self.avahiService.start()
		self.initBroadcast(name_, encode)

	def initBroadcast(self, name_ = None, encode = None):
		if name_ is None or encode is None : return None
		if self.Settings.value('BroadcastDetect', True).toBool() :
			data = QtCore.QString('1' + '<||>' + \
								  name_ + '<||>' + \
								  self.server_addr + '<||>' + \
								  str(self.server_port) + '<||>' + \
								  encode + '<||>' + \
								  self.serverState + '<||>' + \
								  '*infoShare*')
			Sender(data)

	def initServer(self, sharedSourceTree = None, \
						 loadFile = None, previousState = '', \
						 restart = False):
		self.previousState = previousState
		self.menuTab.progressBar.show()
		if 'serverThread' in dir(self) and restart :
			treeModel = sharedSourceTree
			firstRun = False
			del self.serverThread
			self.serverThread = None
		elif 'serverThread' in dir(self) :
			treeModel = sharedSourceTree
			firstRun = False
			del self.serverThread
			self.serverThread = None
		else :
			treeModel = TreeModel('Name', 'Description')
			firstRun = True
		self.statusBar.clearMessage()
		self.statusBar.showMessage('Server offline')
		self.serverReady = 0

		self.server_port = getFreePort(int(InitConfigValue(self.Settings, 'MinPort', '34000')), \
										int(InitConfigValue(self.Settings, 'MaxPort', '34100')))[1]
		self.server_addr = getIP()
		print self.server_addr, self.server_port, 'free'
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
													cert = str(certificatePath), \
													restart = restart), \
										parent = self)

		""" create file of SharedResurces Structure """
		if firstRun :
			lastServerState = str(InitConfigValue(self.Settings, 'LastServerState', ''))
			#print [lastServerState]
			path_ = Path.config('lastSharedSource')
			if lastServerState != '' and os.path.exists(path_) :
				self.serverState = lastServerState
				shutil.move(path_, Path.multiPath(Path.tempStruct, 'server', 'sharedSource_' + self.serverState))
			else :
				S = SharedSourceTree2XMLFile('sharedSource_' + self.serverState, treeModel.rootItem)
				S.__del__(); S = None
		elif loadFile is not None and loadFile != '' :
			if not moveFile(loadFile, Path.multiPath(Path.tempStruct, 'server', 'sharedSource_' + self.serverState), False) :
				S = SharedSourceTree2XMLFile('sharedSource_' + self.serverState, treeModel.rootItem)
				S.__del__(); S = None
		else :
			S = SharedSourceTree2XMLFile('sharedSource_' + self.serverState, treeModel.rootItem)
			S.__del__(); S = None

		""" creating match dictionary {number : fileName} """
		treeModel = TreeModel('Name', 'Description')		## cleaned treeModel.rootItem

		self.serverReinited = not restart
		self.threadSetupTree = SetupTree(TreeProcessing(), \
										[Path.multiPath(Path.tempStruct, 'server', 'sharedSource_' + self.serverState)], \
										treeModel, \
										self, \
										True, \
										self)
		self.threadSetupTree.start()

	def preProcessingComplete(self, commonSet = {}):
		self.commonSetOfSharedSource = commonSet
		#print len(self.commonSetOfSharedSource), ' commonSet.count '
		""" this for server commonSet """
		self.serverThread.Obj.commonSetOfSharedSource = commonSet
		self.serverReady += 1
		if self.serverReady == 2 : self.serverStart()

	def initServerComplete(self):
		self.serverReady += 1
		if self.serverReady == 2 : self.serverStart()

	def serverStart(self):
		if self.serverState != '' : self.serverThread.Obj.serverState = self.serverState
		self.serverThread.start()
		if self.serverReinited : self.preinitAvahiBrowser()
		else :
			name_ = InitConfigValue(self.Settings, 'ServerName', 'Own Avahi Server')
			if self.TLS :
				encode = 'Yes'
			else :
				encode = 'No'
			self.initBroadcast(name_, encode)
		self.statusBar.clearMessage()
		self.statusBar.showMessage('Server online')
		self.menuTab.progressBar.hide()

	def uploadTask(self, info):
			Info = unicode(info)
			job = QtCore.QProcess()
			self.jobCount += 1
			""" посчитать объём загрузок, создать файл с данными соответствия путей
				и ключей в self.commonSetOfSharedSource сервера
			"""
			nameMaskFile = randomString(DIGITS_LENGTH)
			with open(Path.multiPath(Path.tempStruct, 'client', nameMaskFile), 'a') as handler :
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
			if serverAddr not in self.serverThread.Obj.currentSessionID :
				self.showMSG('Session not exist.\nMay be remote server reinit or close.')
				return None
			pid, start = job.startDetached('python', \
						 (QtCore.QStringList()	<< '.' + self.SEP + 'DownLoadClient.py' \
												<< nameMaskFile \
												<< str(downLoadSize) \
												<< str(self.jobCount) \
												<< serverState \
												<< serverAddr \
												<< serverPort \
												<< description \
												<< encode \
												<< self.serverThread.Obj.currentSessionID[serverAddr][0]), \
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
			STR_ = '..' + self.SEP + '..' + self.SEP + 'README'
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
		self.serverDOWN.connect(_ServerSettingsShield.preInitServer)
		_ServerSettingsShield.exec_()
		self.serverDOWN.disconnect(_ServerSettingsShield.preInitServer)

	'''def showColorSettingsShield(self):
		_ColorSettingsShield = ColorSettingsShield(self)
		_ColorSettingsShield.exec_()'''

	def confirmAction(self, address):
		_ConfirmRequest = ConfirmRequest(address, self)
		confirm = _ConfirmRequest.exec_()

	def disconnectSignals(self):
		if 'contactMessage' in dir(self) :
			self.contactMessage.disconnect(self.receiveBroadcastMessage)
		if 'changeConnectState' in dir(self) :
			self.changeConnectState.disconnect(self.initAvahiBrowser)
		if 'initServeR' in dir(self) :
			self.initServeR.disconnect(self.initServer)
		if 'reinitServer' in dir(self) :
			self.reinitServer.disconnect(self.initServer)
		if 'serverDown' in dir(self) :
			self.serverDown.disconnect(self.menuTab.preStartServer)

	def stopServices(self, restart = False, loadFile = '', mode = ''):
		if restart : self.statusBar.showMessage('Restart Services')
		else : self.statusBar.showMessage('Stop Services')
		# send offline packet
		self.menuTab.sentOfflinePost()
		# caching stop
		if not restart and 'cachingThread' in dir(self) :
			self.cachingThread._shutdown()
			self.cachingThread.quit()
			#del self.cachingThread
		# stop services
		if not restart and 'avahiBrowser' in dir(self) :
			if '__del__' in dir(self.avahiBrowser) : self.avahiBrowser.__del__()
			self.avahiBrowser = None
		if not restart and 'avahiService' in dir(self) :
			if '__del__' in dir(self.avahiService) : self.avahiService.__del__()
			self.avahiService = None
		if not restart and 'udpClient' in dir(self) :
			self.udpClient.stop()
		# send 'close session' request
		try :
			for item in self.USERS.iterkeys() :
				_addr, _port = item.split(':') if item in self.USERS else ('', '')
				addr = str(_addr); port = str(_port)
				if self.USERS[item][3] == 'Yes' :
					encode = True
				else :
					encode = False
				if addr in self.serverThread.Obj.currentSessionID and addr != self.server_addr :
					sessionID = self.serverThread.Obj.currentSessionID[addr][0]
					print addr, sessionID, ' send "close session" request'
					clnt = ToolsThread(\
										xr_client(\
												addr, \
												port, \
												self, \
												self, \
												encode), \
										parent = self)
					clnt.run()
					clnt.Obj.sessionClose(sessionID)
					clnt._terminate()
		except RuntimeError, err :
			print '[in stopServices() __init__] RuntimeError :', err
		finally : pass
		if 'serverThread' in dir(self) :
			self.serverThread._terminate(mode if restart and mode != '' else '', loadFile)
		if not restart : self.END = True

	def saveCache(self):
		Once = True
		limitCache = int(InitConfigValue(self.Settings, 'CacheSize', '100')) * 10000
		prefPath = Path.TempCache
		prefPathForAvatar = Path.TempAvatar
		prefPathInStationar = Path.Cache
		prefPathInStationarForAvatar = Path.Avatar
		if os.path.exists(Path.TempCache) :
			currentSize = getFolderSize(prefPathInStationar)
			#print currentSize, ':'
			listingCache = os.listdir(Path.TempCache)
			for name in listingCache :
				path = Path.tempCache(name)
				pathInStationarCache = Path.cache(name)
				if os.path.isfile(path) and not os.path.isfile(pathInStationarCache) :
					if moveFile(path, pathInStationarCache) :
						currentSize += os.path.getsize(pathInStationarCache)
					if moveFile(Path.tempAvatar(name), Path.avatar(name)) :
						currentSize += os.path.getsize(Path.avatar(name))
					#print currentSize
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

	def saveTemporaryData(self):
		if InitConfigValue(self.Settings, 'UseCache', 'True') == 'True' : self.saveCache()
		if InitConfigValue(self.Settings, 'SaveLastStructure', 'True') == 'True' :
			if os.path.exists(Path.multiPath(Path.tempStruct, 'server', 'sharedSource_' + self.serverState)) :
				shutil.move(Path.multiPath(Path.tempStruct, 'server', 'sharedSource_' + self.serverState), \
							Path.config('lastSharedSource'))
				self.Settings.setValue('LastServerState', self.serverState)
			else :
				self.Settings.setValue('LastServerState', '')

	def _close(self):
		if hasattr(self, 'END') and self.END : return None
		self.disconnectSignals()
		self.stopServices()
		#print Path.multiPath(Path.tempStruct, 'server', 'sharedSource_' + self.serverState), ' close'
		self.saveTemporaryData()
		shutil.rmtree(Path.TempStruct, ignore_errors = True)
		self.close()

	def closeEvent(self, event):
		self._close()
