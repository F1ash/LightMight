# -*- coding: utf-8 -*-

from PyQt4.QtGui import *
from PyQt4.QtCore import *
import os

class ViewPanel(QWidget):
	def __init__(self, viewWidget, parent = None):
		QWidget.__init__(self, parent)
		self.prnt = parent
		self.SEP = os.sep

		self.layout = QHBoxLayout()
		self.layout.setSpacing(0)

		self.upButton = QPushButton(QIcon('..' + self.SEP + 'icons' + self.SEP + 'up.png'), '')
		self.upButton.setFlat(True)
		self.upButton.setToolTip('Back to ..')
		self.upButton.setMaximumWidth(25)
		self.upButton.setMaximumHeight(2000)
		self.upButton.setStyleSheet('QPushButton { background: rgba(192,192,255,64);} ')
		self.upButton.clicked.connect(self.prnt.backToParent)
		self.layout.addWidget(self.upButton, 0)

		self.viewWidget = viewWidget
		self.layout.addWidget(self.viewWidget, 1)

		self.setLayout(self.layout)
