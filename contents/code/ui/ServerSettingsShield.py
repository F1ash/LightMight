# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
import os, stat
from TreeProc import TreeModel
from TreeProcess import TreeProcessing
from PathToTree import PathToTree, SharedSourceTree2XMLFile
from ListingText import ListingText
from Functions import InitConfigValue

class ServerSettingsShield(QtGui.QDialog):
	def __init__(self, obj = None, parent = None):
		QtGui.QDialog.__init__(self, parent)

		self.Obj = obj

		self.setWindowTitle('LightMight Server Settings')
		self.setWindowIcon(QtGui.QIcon('../icons/tux_partizan.png'))

		form = QtGui.QGridLayout()

		self.serverNameLabel = QtGui.QLabel('Server Name :')
		form.addWidget(self.serverNameLabel, 0, 0)

		self.defaultName  = InitConfigValue(self.Obj.Settings, 'ServerName', \
											os.getlogin() + ' LightMight Server')
		self.serverNameString = QtGui.QLineEdit(self.defaultName)
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
		value = InitConfigValue(self.Obj.Settings, 'Pool', '100' )
		self.checkPoolBox.setValue(int(value))
		self.checkPoolBox.setSingleStep(1)
		form.addWidget(self.checkPoolBox, 3, 2)

		self.useAvahi = QtGui.QLabel('Use Avahi Service (Zeroconf) :')
		form.addWidget(self.useAvahi, 4, 1)

		self.checkUseAvahi = QtGui.QCheckBox()
		self.checkUseAvahi.setCheckState(QtCore.Qt.Unchecked)
		form.addWidget(self.checkUseAvahi, 4, 2)

		self.saveLastStructureLabel = QtGui.QLabel('Save last Share Structure :')
		form.addWidget(self.saveLastStructureLabel, 5, 1)

		self.saveLastStructureCheck = QtGui.QCheckBox()
		if InitConfigValue(self.Obj.Settings, 'SaveLastStructure', 'False') == 'True' :
			value = QtCore.Qt.Checked
		else:
			value = QtCore.Qt.Unchecked
		self.saveLastStructureCheck.setCheckState(value)
		form.addWidget(self.saveLastStructureCheck, 5, 2)

		self.sharedSourceLabel = QtGui.QLabel('Shared Sources :')
		form.addWidget(self.sharedSourceLabel, 6, 0)

		pathList = []   ##['resultXML']    ## ['result1', 'result2', 'result3']
		self.treeModel = TreeModel('Name', 'Description', parent = self)
		self.sharedTree = QtGui.QTreeView()
		self.sharedTree.setRootIsDecorated(True)
		TreeProcessing().setupItemData(pathList, self.treeModel.rootItem)
		self.sharedTree.setToolTip("<font color=red><b>Select path<br>for share it !</b></font>")
		self.sharedTree.setExpandsOnDoubleClick(True)
		self.sharedTree.setModel(self.treeModel)
		form.addWidget(self.sharedTree, 7, 0, 8, 2)

		self.addDirPathButton = QtGui.QPushButton('&Dir')
		self.addDirPathButton.setMaximumWidth(75)
		self.connect(self.addDirPathButton, QtCore.SIGNAL('clicked()'), self.addDirPath)
		form.addWidget(self.addDirPathButton, 7, 2)

		""" добавить возможность сохранения расшаренных структур
			и загрузки по выбору
		"""

		self.addFilePathButton = QtGui.QPushButton('&File')
		self.addFilePathButton.setMaximumWidth(75)
		self.connect(self.addFilePathButton, QtCore.SIGNAL('clicked()'), self.addFilePaths)
		form.addWidget(self.addFilePathButton, 8, 2)

		self.delPathButton = QtGui.QPushButton('&Del')
		self.delPathButton.setMaximumWidth(75)
		self.connect(self.delPathButton, QtCore.SIGNAL('clicked()'), self.delPath)
		form.addWidget(self.delPathButton, 9, 2)

		self.okButton = QtGui.QPushButton('&Ok')
		self.okButton.setMaximumWidth(75)
		self.connect(self.okButton, QtCore.SIGNAL('clicked()'), self.ok)
		form.addWidget(self.okButton, 10, 2)

		self.cancelButton = QtGui.QPushButton('&Cancel')
		self.cancelButton.setMaximumWidth(75)
		self.connect(self.cancelButton, QtCore.SIGNAL('clicked()'), self.cancel)
		form.addWidget(self.cancelButton, 11, 2)

		self.setLayout(form)
		self.connect(self, QtCore.SIGNAL('refresh'), self.treeRefresh)
		self.connect(self, QtCore.SIGNAL('threadError'), self.threadMSG)

	def addDirPath(self):
		nameDir = QtGui.QFileDialog.getExistingDirectory(self, 'Path_to_', '~', QtGui.QFileDialog.ShowDirsOnly)
		if os.access(nameDir, os.R_OK) and os.access(nameDir, os.X_OK) :    ## and os.access(nameDir, os.W_OK) :
			# print nameDir
			P = PathToTree(nameDir, self.treeModel.rootItem, 'dir')
			###P.__del__(); P = None #FIXME: This destruct empty object
			self.treeModel.reset()
		else :
			showHelp = ListingText("MSG: uncorrect Path (access denied).", self)
			showHelp.exec_()

	def addFilePaths(self):
		fileNames = QtGui.QFileDialog.getOpenFileNames(self, 'Path_to_', '~')
		for name_ in fileNames :
			if not stat.S_ISLNK(os.lstat(name_).st_mode) and os.access(name_, os.R_OK) :
				P = PathToTree(name_, self.treeModel.rootItem, 'file')
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
			delItem = itemParent.childItems
			delItem.remove(item.internalPointer())
			self.sharedTree.reset()
		else :
			print 'Not select Item'

	def ok(self):
		if 'serverThread' in dir(self.Obj) :
			self.Obj.serverThread.terminate()
			self.Obj.serverThread.exit()
		self.saveData()
		self.Obj.initServer()
		""" должен сохранить результат как файл в кеш для передачи на запрос клиентов"""
		S = SharedSourceTree2XMLFile('sharedSource_' + self.Obj.serverState, self.treeModel.rootItem)
		S.__del__(); S = None
		self.done(0)

	def saveData(self):
		self.Obj.Settings.setValue('ServerName', self.serverNameString.text())
		self.Obj.Settings.setValue('Pool', self.checkPoolBox.value())
		if self.saveLastStructureCheck.isChecked() :
			value = 'True'
		else :
			value = 'False'
		self.Obj.Settings.setValue('SaveLastStructure', value)
		self.Obj.Settings.sync()

	def cancel(self):
		self.done(0)

	def closeEvent(self, event):
		event.ignore()
		self.done(0)

