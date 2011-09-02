#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4.QtCore import QByteArray, QObject
from PyQt4.QtNetwork import QUdpSocket, QHostAddress

class UdpClient(QObject):
	def __init__(self):
		QObject.__init__(self)
		self.udp = QUdpSocket(self)
		self.udp.stateChanged.connect(self.sc)
		self.udp.bind(QHostAddress.Any, 35114)
		self.udp.readyRead.connect(self.readUdp)
		print "Binding..."
	
	def start(self):
		while ( True ):
			self.udp.waitForReadyRead()

	def readUdp(self):
		print 'yaha!'
		while ( self.udp.hasPendingDatagrams() ):
			data = QByteArray()
			addr = QHostAddress()
			port = 0
			(data, addr, port) = self.udp.readDatagram(1024)
			print "Datagram: [%s] from %s:%i" % (data, addr.toString(), port)
	
	def sc(self, state):
		print "State: %s" % state

if __name__ == '__main__':
	udp = UdpClient()
	udp.start()
