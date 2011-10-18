#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4.QtCore import QByteArray, QObject, QString, QThread, QMutex

class UdpClientThread(QThread):
	def __init__(self, obj_ = None, parent = None):
		QThread.__init__(self, parent)

		self.prnt = parent
		self.Obj = obj_(self)

	def run(self):
		self.Obj.run()

	def stop(self):
		self.Obj.stop()
