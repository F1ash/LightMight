# -*- coding: utf-8 -*-

import ssl, socket	#, socks
from xmlrpclib import ServerProxy
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SocketServer import ThreadingMixIn
from Functions import readSocketReady, writeSocketReady, TIMEOUT

#socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, 'localhost', 9050)
#socket.socket = socks.socksocket

class ThreadServer(ThreadingMixIn, SimpleXMLRPCServer):
	def __init__(self, serveraddr, allow_none = False, TLS = False, certificatePath = ''):
		SimpleXMLRPCServer.__init__(self, serveraddr, bind_and_activate = False)
		if False : #TLS :
			self.socket = ssl.wrap_socket(\
							socket.socket(socket.AF_INET, socket.SOCK_STREAM), \
							#keyfile = certificatePath, \
							certfile = certificatePath, \
							server_side = True, \
							cert_reqs = ssl.CERT_NONE,  #OPTIONAL, \
							ssl_version = ssl.PROTOCOL_TLSv1, \
							#ca_certs = "/etc/ssl/ca_bundle.trust.crt", \
							ciphers = 'HIGH:TLSv1')
			#print '   TLS used on server...'
		else :
			self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.logRequests = False		## disable logging """
		self.allow_none = allow_none
		self.timeout = TIMEOUT
		self.server_bind()
		self.server_activate()
		self.Ready = True

class SSLServerProxy(ServerProxy):
	def __init__(self, _servaddr, TLS = False, certificatePath = ''):
		if TLS :
			servaddr = 'https://' + _servaddr
		else :
			servaddr = 'http://' + _servaddr
		ServerProxy.__init__(self, servaddr)

		count = 0
		self.Ready = True
		_addr = _servaddr.split(':')
		addr = (str(_addr[0]), int(_addr[1]))
		while count < 10 :
			self.socketInit(addr, False, certificatePath)
			if writeSocketReady(self.socket, TIMEOUT) : break
			count += 1
		else :
			self.Ready = False
			return
		self.timeout = TIMEOUT
		self.socket.settimeout(self.timeout)

	def socketInit(self, addr, TLS = False, certificatePath = ''):
		if TLS :
			self.socket = ssl.wrap_socket(\
							socket.socket(socket.AF_INET, socket.SOCK_STREAM), \
							#keyfile = certificatePath, \
							certfile = certificatePath, \
							cert_reqs = ssl.CERT_NONE,  #OPTIONAL, \
							ssl_version = ssl.PROTOCOL_TLSv1, \
							#ca_certs = "/etc/ssl/ca_bundle.trust.crt", \
							ciphers = 'HIGH:TLSv1')
			#print '   TLS used on client ...'
		else :
			self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.setblocking(1)
		self.socket.connect(addr)
		#print ssl.get_server_certificate(addr, ssl_version = ssl.PROTOCOL_TLSv1)
