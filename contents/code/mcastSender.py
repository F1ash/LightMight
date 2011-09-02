#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4.QtCore import QByteArray, QString
from PyQt4.QtNetwork import QUdpSocket, QHostAddress

def _send_mcast(txt):
	print "Sending txt..."
	udpSocket = QUdpSocket()
	data = QString("Test message...")
	udpSocket.writeDatagram(data, QHostAddress.Broadcast, 35114)

if __name__ == '__main__':
	_send_mcast("Поехали, мля...")
