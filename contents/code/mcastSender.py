#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4.QtCore import QByteArray, QString
from PyQt4.QtNetwork import QUdpSocket, QHostAddress

'''
data =  0/1/A/R(offline/online/answer/reinit)<separator>
		remoteServerName<separator>
		address<separator>
		port<separator>
		Encoding<separator>
		Status<separator>
		ShareInfo
'''

def _send_mcast(data, address = QHostAddress.Broadcast):
	print "Sending :", data
	udpSocket = QUdpSocket()
	addr = QHostAddress(address)
	#print addr.toString()
	return udpSocket.writeDatagram(data, addr, 34001)

if __name__ == '__main__':
	_send_mcast("Поехали, мля...")
