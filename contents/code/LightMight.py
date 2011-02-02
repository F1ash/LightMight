# -*- coding: utf-8 -*-

import os, sys, os.path
from PyQt4 import QtGui, QtCore
from xml.dom.minidom import Document, parse

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

		serverSettings = QtGui.QAction(QtGui.QIcon('../icons/help.png'),'&Client Settings', self)
		serverSettings.setStatusTip('Read help')
		self.connect(serverSettings, QtCore.SIGNAL('triggered()'), self.showServerSettingsShild)

		clientSettings = QtGui.QAction(QtGui.QIcon('../icons/help.png'),'&Server Settings', self)
		clientSettings.setStatusTip('Read help')
		self.connect(clientSettings, QtCore.SIGNAL('triggered()'), self.showClientSettingsShild)

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

		self.menuTab = Box()
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

	def showClientSettingsShild(self):
		_ClientSettingsShild = ClientSettingsShild()
		_ClientSettingsShild.exec_()
		pass

	def showServerSettingsShild(self):
		_ServerSettingsShild = ServerSettingsShild()
		_ServerSettingsShild.exec_()
		pass

class ClientSettingsShild(QtGui.QDialog):
	def __init__(self, parent = None):
		QtGui.QWidget.__init__(self, parent)

		self.setWindowTitle('LightMight Server Settings')
		self.setWindowIcon(QtGui.QIcon('../icons/tux_partizan.png'))

	def closeEvent(self, event):
		event.ignore()
		self.done(0)


class ServerSettingsShild(QtGui.QDialog):
	def __init__(self, parent = None):
		QtGui.QWidget.__init__(self, parent)

		self.setWindowTitle('LightMight Client Settings')
		self.setWindowIcon(QtGui.QIcon('../icons/tux_partizan.png'))

	def closeEvent(self, event):
		event.ignore()
		self.done(0)


class ButtonPanel(QtGui.QWidget):
	def __init__(self, Obj_, job_key = None, parent = None):
		QtGui.QWidget.__init__(self, parent)

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
		self.connect(self.upLoadButton, QtCore.SIGNAL('clicked()'), self.addItem)
		self.layout.addWidget(self.upLoadButton)

		self.setLayout(self.layout)

	def addItem(self):
		pass

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

class TreeItem(QtCore.QObject):
	def __init__(self, data = [], parentItem = None, parent = None):
		QtCore.QObject.__init__(self, parent)
		self.parentItem = parentItem
		self.itemData = data
		self.childItems = []
		self.checkState = QtCore.Qt.Unchecked

	def child(self, row):
		if row <= len(self.childItems):
			return self.childItems[row]
		return None

	def childCount(self):
		return len(self.childItems)

	def columnCount(self):
		return len(self.itemData)

	def data(self, column, role = QtCore.Qt.DisplayRole):
		if role == QtCore.Qt.CheckStateRole and column == 0 :
			return self.checkState
		elif role != QtCore.Qt.CheckStateRole and column >= 0 :
			return self.itemData[column]

	def childIndex(self, child_link = None):
		if child_link in self.childItems and child_link is not None:
			return self.childItems.index(child_link)

	def row(self):
		if (self.parentItem is not None):
			return self.parentItem.childIndex(self)
		return None

	def getParentItem(self):
		return self.parentItem

	def appendChild(self, item):
		if item is not None:
			self.childItems.append(item)

class TreeModel(QtCore.QAbstractItemModel):
	checkStateChanged = QtCore.pyqtSignal()
	def __init__(self, data = [], parent = None):
		QtCore.QAbstractItemModel.__init__(self, parent)

		self.rootItem = TreeItem(data, None, self)
		self.changeMe = True

	def index(self, row, column, prnt = QtCore.QModelIndex()):
		if (not self.hasIndex(row, column, prnt)) :
			return QtCore.QModelIndex()

		parentItem = self.rootItem;
		if prnt.isValid():
			parentItem = prnt.internalPointer()
			#print "=====> %s\t-\t%s" % (parentItem, parentItem.data(0))

		childItem = parentItem.child(row)
		if ( childItem is not None) :
			return self.createIndex(row, column, childItem)

		return QtCore.QModelIndex()

	def parent(self, child = QtCore.QModelIndex()):
		if ( not child.isValid() ) :
			return QtCore.QModelIndex()

		childItem = child.internalPointer()
		#print "--> %s" % type(childItem)
		if childItem is None:
			return QtCore.QModelIndex()

		parentItem = childItem.getParentItem()
		if ( parentItem is None or parentItem == self.rootItem ) :
			return QtCore.QModelIndex()

		return self.createIndex(parentItem.row(), 0, parentItem)

	def rowCount(self, parent = QtCore.QModelIndex()):
		if ( parent.column() > 0 ):
			return 0

		if ( not parent.isValid() ) :
			item = self.rootItem
		else :
			item = parent.internalPointer()

		return item.childCount()

	def columnCount(self, parent = QtCore.QModelIndex()):
		#if parent.isValid() :
		#	return parent.internalPointer().columnCount()
		#else :
		#	return self.rootItem.columnCount()
		return 2

	def data(self, index_, role):
		if (not index_.isValid()) :
			return QtCore.QVariant()

		item = index_.internalPointer()
		if role == QtCore.Qt.CheckStateRole :
				return item.data(index_.column(), role)
		elif (role != QtCore.Qt.DisplayRole) :
			return QtCore.QVariant()
		return item.data(index_.column(), role)

	def headerData(self, section, orientation = QtCore.Qt.Horizontal, role = QtCore.Qt.DisplayRole):
		if (orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole) :
			return self.rootItem.data(section)
		return QtCore.QVariant()

	def setupItemData(self, pathList):
		for path in pathList :
			datasource = open(path)
			dom2 = parse(datasource)   # parse an open file
			#print dom2

			self.parseFile(dom2.childNodes, self.rootItem)

		#self.debugPrintObj(self.rootItem)

	def parseFile(self, listNodes, parent_obj, tab = '	'):
		for i in xrange(listNodes.length):
			node = listNodes.item(i)
			name_ = node.localName

			#print tab, name_, node.attributes.item(0).value
			_ddata = [node.attributes.item(0).value, name_]
			_newobj = TreeItem(_ddata, parent_obj, parent_obj)
			parent_obj.appendChild(_newobj)
			if name_ == 'dir':
				self.parseFile(node.childNodes, _newobj, tab + '\t')

	def debugPrintObj(self, some_obj, tab = '	'):
		return
		print "obj->%s", tab, some_obj.data(0)
		for child in some_obj.childItems:
			self.debugPrintObj(child, tab + '	')

	def processCheckStateOfChildren(self, b):
		qua = b.childCount()
		checkState = b.checkState
		for i in range(0, qua):
			childItem = b.child(i)
			childItem.checkState = checkState
			self.processCheckStateOfChildren(childItem)

	def processCheckStateOfParents(self, b):
		parentItem = b.getParentItem()
		if parentItem is not None :
			qua = parentItem.childCount()
		else :
			return

		quaOfChecked = 0
		quaOfPartChecked = 0
		for i in range(0, qua) :
			if parentItem.child(i).checkState == QtCore.Qt.Checked :
				quaOfChecked += 1
			elif parentItem.child(i).checkState == QtCore.Qt.PartiallyChecked :
				quaOfPartChecked += 1

			if quaOfChecked == qua :
				checkState = QtCore.Qt.Checked
			elif quaOfChecked == 0 and quaOfPartChecked == 0 :
				checkState = QtCore.Qt.Unchecked
			else :
				checkState = QtCore.Qt.PartiallyChecked

			parentItem.checkState = checkState
			self.processCheckStateOfParents(parentItem)

	def setData(self, index_, value, role = QtCore.Qt.DisplayRole):
		if not index_.isValid() :
			return False

		if role == QtCore.Qt.CheckStateRole :
			item = index_.internalPointer()

			if item.checkState == QtCore.Qt.Unchecked :
				item.checkState = QtCore.Qt.Checked
			else :
				item.checkState = QtCore.Qt.Unchecked

			if self.changeMe and item is not None:
				self.changeMe = False
				self.processCheckStateOfChildren(item)
				self.processCheckStateOfParents(item)
				self.changeMe = True

			self.emit(QtCore.SIGNAL("checkStateChanged()"))
			self.emit(QtCore.SIGNAL("dataChanged(const QModelIndex&, const QModelIndex&)"), \
																	index_.parent(), index_)
			return True

		return False

	def flags(self, index_):
		if not index_.isValid() :
			return QtCore.Qt.ItemIsEnabled

		return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | \
										QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEditable

class Box(QtGui.QWidget):
	def __init__(self, job_key = None, parent = None):
		QtGui.QWidget.__init__(self, parent)

		self.layout = QtGui.QGridLayout()

		self.userList = QtGui.QListWidget()
		self.userList.setMaximumWidth(250)
		#self.userList.setMinimumSize(100, 75)
		self.userList.setToolTip('Users in Web')
		self.layout.addWidget(self.userList, 0, 0)

		pathList = ['result1', 'result2', 'result3']
		treeModel = TreeModel(['Name', 'Description'], parent = self)
		self.sharedTree = QtGui.QTreeView()
		#self.sharedTree.setRootIndex(treeModel.index(0, 0))
		self.sharedTree.setRootIsDecorated(True)
		treeModel.setupItemData(pathList)
		self.sharedTree.setToolTip('Shared Source')
		self.sharedTree.setExpandsOnDoubleClick(True)
		self.sharedTree.setModel(treeModel)
		self.layout.addWidget(self.sharedTree, 0, 1)

		self.buttunPanel = BoxLayout(ButtonPanel)
		self.buttunPanel.setMaximumWidth(100)
		self.layout.addWidget(self.buttunPanel, 0, 2)

		self.setLayout(self.layout)

#os.system('cd $HOME && xauth merge /dev/shm/dsa && rm /dev/shm/dsa')
name_ = os.path.basename(sys.argv[0])
#print sys.argv[0][:-len(name_)]
os.chdir(sys.argv[0][:-len(name_)])
app = QtGui.QApplication(sys.argv)
main = MainWindow()
main.show()
sys.exit(app.exec_())
