#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4.QtCore import QByteArray, QObject, QString, QThread, QMutex
from PyQt4.QtNetwork import QUdpSocket, QHostAddress, QAbstractSocket
import time

class UdpClient(QThread):
	def __init__(self, parent):
		QThread.__init__(self, parent)

		self.prnt = parent
		self.udp = QUdpSocket(self)
		addr = QHostAddress(QHostAddress.Any)
		#print addr.toString()
		self.udp.bind(addr, 34001)
		self.udp.readyRead.connect(self.readUdp)
		print "Binding..."
		self.STOP = False
		self.locker = QMutex()
		self.udp.stateChanged.connect(self.sc)

	def run(self):
		self.prnt.initAvahiService()
		while True :
			if self.udp.state() == QAbstractSocket.ConnectedState :
				self.udp.waitForReadyRead()
			else : time.sleep(0.1)
			if self.STOP : self.udp.close(); break
		print 'UDPClient closed...'
		self.prnt.changeConnectState.emit()

	def stop(self):
		self.locker.lock()
		self.STOP = True
		self.locker.unlock()

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

if __name__ == '__main__':
	udp = UdpClient()
	try :
		udp.start()
	except KeyboardInterrupt :
		print 'tread closed manually'
		udp.stop()
