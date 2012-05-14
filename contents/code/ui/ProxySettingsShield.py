# -*- coding: utf-8 -*-

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from ListingText import ListingText
import os, stat, os.path, shutil

def loadSocksModule(Settings, loadModule = None):
	proxyLoad = False
	if ( loadModule is None and Settings.value('UseProxy', 'False')=='True' ) or loadModule :
		## http://sourceforge.net/projects/socksipy/
		## or install the Fedora liked python-SocksiPy package
		try :
			import socks
			proxyLoad = True
		except : pass #proxyLoad = False
		finally : pass
	return proxyLoad

class ProxySettingsShield(QDialog):
	def __init__(self, parent = None):
		QDialog.__init__(self, parent)

		self.Obj = parent
		self.SEP = os.sep

		self.setWindowTitle('LightMight Proxy Settings')
		self.setWindowIcon(QIcon('..' + self.SEP + 'icons' + self.SEP + 'tux_partizan.png'))
		#self.tr = Translator('Proxy')

		self.layout = QGridLayout()
		self.layout.setSpacing(0)

		self.enableProxy = QCheckBox()
		#self.enableProxy.setToolTip(self.tr._translate("Enable\Disable the Proxy"))
		self.Enabled = True if self.Obj.Settings.value('UseProxy', 'False')=='True' else False
		if self.Enabled : self.enableProxy.setCheckState(Qt.Checked)
		else : self.enableProxy.setCheckState(Qt.Unchecked)
		self.enableProxy.stateChanged.connect(self.activateProxy)
		self.layout.addWidget(self.enableProxy, 0, 0, Qt.AlignLeft)

		self.proxyTypeBox = QComboBox()
		self.proxyTypeBox.addItem('HTTP', QVariant('HTTP'))
		self.proxyTypeBox.addItem('SOCKS4', QVariant('SOCKS4'))
		self.proxyTypeBox.addItem('SOCKS5', QVariant('SOCKS5'))
		#self.proxyTypeBox.setToolTip(self.tr._translate("Proxy type"))
		data = self.Obj.Settings.value('ProxyType', 'SOCKS5')
		self.proxyTypeBox.setCurrentIndex(self.proxyTypeBox.findData(data))
		self.layout.addWidget(self.proxyTypeBox, 1, 0)

		self.Hlayout = QHBoxLayout()
		self.addrEditor = QLineEdit()
		self.addrEditor.setText(self.Obj.Settings.value('ProxyAddr', '').toString())
		#self.addrEditor.setToolTip(self.tr._translate("Proxy address"))
		self.Hlayout.addWidget(self.addrEditor, 0)

		self.portBox = QSpinBox()
		self.portBox.setMinimum(0)
		self.portBox.setMaximum(65535)
		value = self.Obj.Settings.value('ProxyPort', '3128' )
		self.portBox.setValue(int(str(value.toString())))
		self.portBox.setSingleStep(1)
		#self.portBox.setToolTip(self.tr._translate('Proxy Port'))
		self.Hlayout.addWidget(self.portBox, 0,  Qt.AlignRight)

		self.layout.addItem(self.Hlayout, 1, 1)

		self.userLabel = QLabel("UserName :")
		self.passwLabel = QLabel("Password :")
		self.layout.addWidget(self.userLabel, 2, 0,  Qt.AlignLeft)
		self.layout.addWidget(self.passwLabel, 3, 0,  Qt.AlignLeft)

		self.userEditor = QLineEdit()
		self.userEditor.setText(self.Obj.Settings.value('ProxyUSER', '').toString())
		self.passwEditor = QLineEdit()
		self.passwEditor.setText(self.Obj.Settings.value('ProxyPASS', '').toString())
		self.layout.addWidget(self.userEditor, 2, 1)
		self.layout.addWidget(self.passwEditor, 3, 1)

		self.okButton = QPushButton('&Ok')
		self.okButton.setMaximumWidth(75)
		self.connect(self.okButton, SIGNAL('clicked()'), self.ok)
		self.layout.addWidget(self.okButton, 14, 2)

		self.cancelButton = QPushButton('&Cancel')
		self.cancelButton.setMaximumWidth(75)
		self.connect(self.cancelButton, SIGNAL('clicked()'), self.cancel)
		self.layout.addWidget(self.cancelButton, 15, 2)

		if loadSocksModule(self.Obj.Settings) : available = "SocksiPy module loaded"
		else : available = "SocksiPy module not loaded"
		self.proxyModuleLabel = QLabel(available)
		self.layout.addWidget(self.proxyModuleLabel, 0, 1,  Qt.AlignRight)

		self.setLayout(self.layout)
		self.activateProxy()

	def saveData(self):
		self.Obj.Settings.setValue('ProxyType', self.proxyTypeBox.currentText())
		self.Obj.Settings.setValue('ProxyAddr', self.addrEditor.text())
		self.Obj.Settings.setValue('ProxyPort', self.portBox.value())
		self.Obj.Settings.setValue('ProxyUSER', self.userEditor.text())
		self.Obj.Settings.setValue('ProxyPASS', self.passwEditor.text())
		if self.enableProxy.isChecked() :
			value = 'True'
		else :
			value = 'False'
		self.Obj.Settings.setValue('UseProxy', value)
		self.Obj.Settings.sync()

	def activateProxy(self):
		state = True if self.enableProxy.checkState()==Qt.Checked else False
		if state : PROXY_Module = loadSocksModule(self.Obj.Settings, True)
		else : PROXY_Module = loadSocksModule(self.Obj.Settings, False)
		if PROXY_Module : available = "SocksiPy module loaded"
		else : available = "SocksiPy module not loaded"
		self.proxyModuleLabel.setText(available)
		if PROXY_Module and state : self.enableWidgets(True)
		else : self.enableWidgets(False)

	def enableWidgets(self, state):
		self.addrEditor.setEnabled(state)
		self.portBox.setEnabled(state)
		self.userLabel.setEnabled(state)
		self.passwLabel.setEnabled(state)
		self.userEditor.setEnabled(state)
		self.passwEditor.setEnabled(state)
		self.proxyTypeBox.setEnabled(state)

	def ok(self):
		self.saveData()
		# [re]init server for web
		self.done(0)

	def cancel(self):
		self.done(0)

	def closeEvent(self, event):
		event.ignore()
		self.done(0)

