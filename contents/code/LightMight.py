# -*- coding: utf-8 -*-

import os, sys, os.path
from PyQt4 import QtGui, QtCore, Qt

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

		setPath = QtGui.QAction(QtGui.QIcon('../icons/help.png'),'&set Path', self)
		setPath.setStatusTip('Read help')
		self.connect(setPath, QtCore.SIGNAL('triggered()'), self.showHelp_)

		setAddr = QtGui.QAction(QtGui.QIcon('../icons/help.png'),'&set Address', self)
		setAddr.setStatusTip('Read help')
		self.connect(setAddr, QtCore.SIGNAL('triggered()'), self.showHelp_)

		self.statusBar()

		menubar = self.menuBar()

		file_ = menubar.addMenu('&File')
		file_.addAction(self.base_)
		file_.addAction(self.create_struct)
		file_.addAction(self.exit_)

		set_ = menubar.addMenu('&Settings')
		set_.addAction(setPath)
		set_.addAction(setAddr)

		help_ = menubar.addMenu('&Help')
		help_.addAction(listHelp)

		self.menuTab = BoxLayout(Box)
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
		self.connect(self.trayIcon, QtCore.SIGNAL("activated(QSystemTrayIcon::ActivationReason)"), self.trayIconClicked)
		self.trayIcon.show()

		# toolbar = self.addToolBar('Exit')
		# toolbar.addAction(exit_)

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
		showHelp = ListingText("backupper.help", self)
		showHelp.exec_()

class BoxLayout(QtGui.QWidget):
	def __init__(self, Obj_, job_key = None, parent = None):
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

class MyElem(QtCore.QModelIndex()):
	def __init__(self, parent = None):
		QtCore.QModelIndex.__init__(self, parent)

		pass

class MyTree(QtCore.QAbstractItemModel):
	def __init__(self, listObj = [], parent = None):
		QtCore.QAbstractItemModel.__init__(self, parent)

		self.createIndex(0, 0, QtCore.QString('lkhwvglerht;'))
		pass

class Box(QtGui.QWidget):
	def __init__(self, job_key = None, parent = None):
		QtGui.QWidget.__init__(self, parent)

		self.layout = QtGui.QGridLayout()

		self.userList = QtGui.QListWidget()
		self.userList.setToolTip('Users in Web')
		self.layout.addWidget(self.userList, 0, 0)

		self.sharedTree = QtGui.QTreeView()
		self.sharedTree.setModel(MyTree())
		#self.sharedTree.setRootIndex(QtCore.QModelIndex())
		self.sharedTree.setRootIsDecorated(True)
		self.sharedTree.setToolTip('Shared Source')
		self.layout.addWidget(self.sharedTree, 0, 1)

		self.setLayout(self.layout)

#os.system('cd $HOME && xauth merge /dev/shm/dsa && rm /dev/shm/dsa')
name_ = os.path.basename(sys.argv[0])
os.chdir(sys.argv[0][:-len(name_)])
app = QtGui.QApplication(sys.argv)
main = MainWindow()
main.show()
sys.exit(app.exec_())
