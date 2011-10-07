#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4.QtCore import QByteArray, QString
from PyQt4.QtNetwork import QUdpSocket, QHostAddress

'''
data =  0/1(offline/online)<separator>
		remoteServerName<separator>
		address:port<separator>
		Status<separator>
		Encoding<separator>
		ShareInfo
'''

def _send_mcast(txt):
	print "Sending txt..."
	udpSocket = QUdpSocket()
	addr = QHostAddress(QHostAddress.Broadcast)
	print addr.toString()
	data = "Test message: " + txt
	return udpSocket.writeDatagram(data, addr, 34001)

if __name__ == '__main__':
	_send_mcast("Поехали, мля...")
