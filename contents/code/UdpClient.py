#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4.QtCore import QByteArray, QString, QThread, QMutex, pyqtSignal, pyqtSlot
from PyQt4.QtNetwork import QUdpSocket, QHostAddress, QAbstractSocket

SocketErrors = {
	0 : 'ConnectionRefusedError\nThe connection was refused by the peer (or timed out).', \
	1 : 'RemoteHostClosedError\nThe remote host closed the connection. Note that the client socket (i.e., this socket) will be closed after the remote close notification has been sent.', \
	2 : 'HostNotFoundError\nThe host address was not found.', \
	3 : 'SocketAccessError\nThe socket operation failed because the application lacked the required privileges.', \
	4 : 'SocketResourceError\nThe local system ran out of resources (e.g., too many sockets).', \
	5 : 'SocketTimeoutError\nThe socket operation timed out.', \
	6 : 'DatagramTooLargeError\nThe datagram was larger than the operating system`s limit (which can be as low as 8192 bytes).', \
	7 : 'NetworkError\nAn error occurred with the network (e.g., the network cable was accidentally plugged out).', \
	8 : 'AddressInUseError\nThe address specified to QUdpSocket.bind() is already in use and was set to be exclusive.', \
	9 : 'SocketAddressNotAvailableError\nThe address specified to QUdpSocket.bind() does not belong to the host.', \
	10 : 'UnsupportedSocketOperationError\nThe requested socket operation is not supported by the local operating system (e.g., lack of IPv6 support).', \
	12 : 'ProxyAuthenticationRequiredError\nThe socket is using a proxy, and the proxy requires authentication.', \
	13 : 'SslHandshakeFailedError\nThe SSL/TLS handshake failed, so the connection was closed (only used in QSslSocket)', \
	11 : 'UnfinishedSocketOperationError\nUsed by QAbstractSocketEngine only, The last operation attempted has not finished yet (still in progress in the background).', \
	14 : 'ProxyConnectionRefusedError\nCould not contact the proxy server because the connection to that server was denied', \
	15 : 'ProxyConnectionClosedError\nThe connection to the proxy server was closed unexpectedly (before the connection to the final peer was established)', \
	16 : 'ProxyConnectionTimeoutError\nThe connection to the proxy server timed out or the proxy server stopped responding in the authentication phase.', \
	17 : 'ProxyNotFoundError\nThe proxy address set with setProxy() (or the application proxy) was not found.', \
	18 : 'ProxyProtocolError\nThe connection negotiation with the proxy server because the response from the proxy server could not be understood.', \
	-1 : 'UnknownSocketError\nAn unidentified error occurred.'
}

class UdpClient(QThread):
	def __init__(self, parent):
		QThread.__init__(self, parent)

		self.prnt = parent
		self.udp = QUdpSocket()
		addr = QHostAddress(QHostAddress.Any)
		print 'bind to:', addr.toString()
		self.udp.bind(addr, 34001)
		self.udp.error.connect(self.errorAnalyser)
		self.udp.readyRead.connect(self.readUdp)
		print "Binding..."
		self.STOP = False
		self.locker = QMutex()

	def run(self):
		self.prnt.initAvahiService()
		while True :
			if self.udp is not None and self.udp.state() == QAbstractSocket.ConnectedState :
				self.udp.waitForReadyRead()
			else : self.msleep(100)
			if self.STOP and self.udp is not None: self.udp.close(); break
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
			try :
				datagramSize = self.udp.pendingDatagramSize()
				if datagramSize > 0 :
					(data, addr, port) = self.udp.readDatagram(datagramSize)
					#print "Datagram: [%s] from %s:%i" % (QString().fromUtf8(data), addr.toString(), port)
					self.prnt.contactMessage.emit(QString().fromUtf8(data), addr.toString())
			except socket.error, err :
				print '[in readUdp() UdpClient] SocketError1 : ', err
			except socket.timeout, err :
				print '[in readUdp() UdpClient] SocketError2 : ', err
			except :
				print '[in readUdp() UdpClient] UnknownError'
			finally : pass

	def errorAnalyser(self, error):
		print '[UdpClient] SocketError : ', SocketErrors[error]

if __name__ == '__main__':
	udp = UdpClient()
	try :
		udp.start()
	except KeyboardInterrupt :
		print 'tread closed manually'
		udp.stop()
