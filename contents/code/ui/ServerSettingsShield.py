# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtCore
import os
from TreeProc import TreeModel
from TreeProcess import TreeProcessing
from PathToTree import PathToTree

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
		self.connect(self, QtCore.SIGNAL('threadError'), self.threadMSG)

	def addPath(self):
		nameDir = QtGui.QFileDialog.getExistingDirectory(self, 'Path_to_', '~', QtGui.QFileDialog.ShowDirsOnly)
		if os.access(nameDir, os.R_OK) and os.access(nameDir, os.X_OK) :    ## and os.access(nameDir, os.W_OK) :
			# print nameDir
			P = PathToTree(nameDir, self.treeModel.rootItem)
			###P.__del__(); P = None #FIXME: This destruct empty object
			self.treeModel.reset()
			###print gc.collect()
			###print gc.get_referrers()
			###del gc.garbage[:]
			#global TSThread
			#TSThread = TreeSettingThread(self, nameDir, self.treeModel.rootItem)
			#TSThread.start()
		else :
			showHelp = ListingText("MSG: uncorrect Path (access denied).", self)
			showHelp.exec_()

	def treeRefresh(self):
		self.treeModel.reset()
		###gc.collect()
		###print gc.get_referrers()
		###del gc.garbage[:]

	def threadMSG(self, str_):
		showHelp = ListingText("MSG: Available files not found in " + str_, self)
		showHelp.exec_()
		###gc.collect()
		###print gc.get_referrers()
		###del gc.garbage[:]

	def delPath(self):
		item = self.sharedTree.selectionModel().currentIndex()
		itemParent = item.internalPointer().parentItem
		delItem = itemParent.childItems
		delItem.remove(item.internalPointer())
		self.sharedTree.reset()
		###print gc.collect()
		###print gc.get_referrers()
		###del gc.garbage[:]

	def ok(self):
		#global FileNameList
		#doc = Document()
		#doc.appendChild(self.treeModel.treeDataToXML(self.treeModel.rootItem))
		#print doc.toprettyxml()
		#del FileNameList
		#doc.unlink()
		#del doc
		###print gc.collect()
		###print gc.get_referrers()
		###del gc.garbage[:]
		pass #FIXME: this method is empty

	def cancel(self):
		###print gc.collect()
		###print gc.get_referrers()
		###del gc.garbage[:]
		self.done(0)

	def closeEvent(self, event):
		event.ignore()
		self.done(0)


