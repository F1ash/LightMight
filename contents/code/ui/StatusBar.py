# -*- coding: utf-8 -*-

from PyQt4.QtGui import QStatusBar, QLabel

class StatusBar(QStatusBar):
	def __init__(self, parent = None):
		QStatusBar.__init__(self, parent)
		self.prnt = parent

		self.clearMessage()
		self.reformat()
		self.status = QLabel()
		self.addPermanentWidget(self.status)

	def showMessage(self, text):
		self.status.setText(text)
