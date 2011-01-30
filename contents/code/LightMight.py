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
		self.menuTab.setMaximumSize(800, 650)
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
		showHelp = ListingText("MSG: LightMight.help", self)
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

class ListingText(QtGui.QDialog):
	def __init__(self, path_, parent = None):
		QtGui.QDialog.__init__(self, parent)

		self.setWindowTitle('LightMight Text')
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

class TreeItem(object):
	def __init__(self, data = [], parent = None):

		self.parentItem = parent
		self.itemData = data
		self.childItems = self.parentItem.children()

	def child(self, row):
		#return self.childItems.value(row)
		return self.childItems[row]

	def childCount(self):
		return len(self.childItems)

	def columnCount(self):
		return len(self.itemData)

	def data(self, column):
		# return self.itemData.value(colunm)
		return self.itemData[column]

	def row(self):
		if (self.parentItem is not None):
			return self.parentItem.childItems.index(self)
		return 0

	def parent(self):
		return self.parentItem

	def appendChild(self, item):
		if item:
			self.childItems.append(item);

class TreeModel(QtCore.QAbstractItemModel):
	def __init__(self, data = [], parent = None):
		QtCore.QAbstractItemModel.__init__(self, parent)

		self.rootItem = TreeItem(data, parent = self)

	def index(self, row, column, parent = QtCore.QModelIndex()):
		if (not self.hasIndex(row, column, parent)) :
			return QtCore.QModelIndex()

		if (not parent.isValid()) :
			parentItem = rootItem
		else :
			parentItem = parent.internalPointer()

		childItem = parentItem.child(row)
		if ( childItem is not None) :
			return self.createIndex(row, column, childItem)

		return QtCore.QModelIndex()

	def parent(self, child):
		if ( not child.isValid() ) :
			return QModelIndex()

		childItem = child.internalPointer()
		parentItem = childItem.parent()
		if ( parentItem is not None or parentItem == self.rootItem ) :
			return QtCore.QModelIndex()

		return self.createIndex(parentItem.row(), 0, parentItem)

	def rowCount(self, parent):
		if ( parent.column() > 0 ):
			return 0

		if ( not parent.isValid() ) :
			item = self.rootItem;
		else :
			item = parent.internalPointer()

		return item.childCount()

	def columnCount(self, parent):
		if (parent.isValid()) :
			return (parent.internalPointer()).columnCount()
		else :
			return self.rootItem.columnCount()

	def data(self, index, role):
		return QtCore.QVariant()

	def headerData(self, section, orientation = QtCore.Qt.Horizontal, role = QtCore.Qt.DisplayRole):
		if (orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole) :
			return self.rootItem.data(section)
		return QtCore.QVariant()

class Box(QtGui.QWidget):
	def __init__(self, job_key = None, parent = None):
		QtGui.QWidget.__init__(self, parent)

		self.layout = QtGui.QGridLayout()

		self.userList = QtGui.QListWidget()
		self.userList.setMinimumSize(100, 75)
		self.userList.setToolTip('Users in Web')
		self.layout.addWidget(self.userList, 0, 0)

		treeModel = TreeModel(['Name', 'Description'], parent = self)
		self.sharedTree = QtGui.QTreeView()
		self.sharedTree.setModel(treeModel)
		self.sharedTree.setRootIndex(treeModel.index(0, 0))
		self.sharedTree.setRootIsDecorated(True)
		self.sharedTree.setToolTip('Shared Source')
		self.sharedTree.setExpandsOnDoubleClick(True)
		self.layout.addWidget(self.sharedTree, 0, 1)

		self.setLayout(self.layout)

#os.system('cd $HOME && xauth merge /dev/shm/dsa && rm /dev/shm/dsa')
name_ = os.path.basename(sys.argv[0])
os.chdir(sys.argv[0][:-len(name_)])
app = QtGui.QApplication(sys.argv)
main = MainWindow()
main.show()
sys.exit(app.exec_())
