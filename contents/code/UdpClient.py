#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4.QtCore import QByteArray, QObject, QString
from PyQt4.QtNetwork import QUdpSocket, QHostAddress

class UdpClient(QObject):
	def __init__(self, parent):
		QObject.__init__(self)

		self.prnt = parent
		self.udp = QUdpSocket(self)
		addr = QHostAddress(QHostAddress.Any)
		print addr.toString()
		self.udp.stateChanged.connect(self.sc)
		self.udp.bind(addr, 34001)
		self.udp.readyRead.connect(self.readUdp)
		print "Binding..."
	
	def start(self):
		while True :
			self.udp.waitForReadyRead()

	def stop(self):
		self.udp.close()

	def readUdp(self):
		while ( self.udp.hasPendingDatagrams() ):
			data = QByteArray()
			addr = QHostAddress()
			port = 0
			(data, addr, port) = self.udp.readDatagram(1024)
			print "Datagram: [%s] from %s:%i" % (QString().fromUtf8(data), addr.toString(), port)
			self.prnt.contactMessage.emit(QString().fromUtf8(data), addr.toString())

	def sc(self, state):
		print "State: %s" % state
		self.prnt.changeConnectState.emit(QString(state))

if __name__ == '__main__':
	udp = UdpClient()
	try :
		udp.start()
	except KeyboardInterrupt :
		print 'tread closed manually'
		udp.stop()
