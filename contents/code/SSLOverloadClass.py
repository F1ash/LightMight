# -*- coding: utf-8 -*-

import ssl, socket, socks
from xmlrpclib import ServerProxy
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SocketServer import ThreadingMixIn
from Functions import readSocketReady, writeSocketReady, TIMEOUT

#socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, 'localhost', 9050)
#socket.socket = socks.socksocket

class ThreadServer(ThreadingMixIn, SimpleXMLRPCServer):
	#ThreadingMixIn.daemon_threads = True
	def __init__(self, serveraddr, allow_none = False, TLS = False, certificatePath = ''):
		SimpleXMLRPCServer.__init__(self, serveraddr, bind_and_activate = False)

		count = 0
		self.Ready = True
		while count < 10 :
			self.socketInit(TLS, certificatePath = certificatePath)
			if readSocketReady(self.socket, TIMEOUT) and writeSocketReady(self.socket, TIMEOUT) : break
			count += 1
		else :
			self.Ready = False
			return
		self.logRequests = False		## disable logging """
		self.allow_none = allow_none
		self.timeout = TIMEOUT
		self.socket.settimeout(self.timeout)
		self.server_bind()
		self.server_activate()

	def socketInit(self, TLS = False, certificatePath = ''):
		if TLS :
			self.socket = ssl.wrap_socket(\
							socket.socket(socket.AF_INET, socket.SOCK_STREAM), \
							ca_certs = "/etc/ssl/ca_bundle.trust.crt", \
							server_side = True, \
							certfile = certificatePath,
							keyfile = certificatePath,
							ssl_version = ssl.PROTOCOL_TLSv1, \
							ciphers = 'HIGH:TLSv1')
			#print '   TLS used on server...'
		else :
			self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	def verify_request(self, request, client_address):
		if readSocketReady(request, self.timeout) and writeSocketReady(request, self.timeout) :
			self.client_address = client_address
			return True
		else : False

	'''def single_request(self, request, client_address):
		if readSocketReady(self.socket, self.timeout) :
			return SimpleXMLRPCServer.single_request(self, request, client_address)

	def handle_one_request(self):
		if readSocketReady(self.socket, self.timeout) :
			return SimpleXMLRPCServer.handle_one_request(self)

	def handle_request(self):
		if readSocketReady(self.socket, self.timeout) :
			return SimpleXMLRPCServer.handle_request(self)

	def get_request(self):
		if readSocketReady(self.socket, self.timeout) :
			return SimpleXMLRPCServer.get_request(self)

	def finish_request(self, request, client_address):
		if readSocketReady(self.socket, self.timeout) :
			return SimpleXMLRPCServer.finish_request(self, request, client_address)

	def process_request(self, request, client_address):
		if readSocketReady(self.socket, self.timeout) :
			return SimpleXMLRPCServer.process_request(self, request, client_address)

	def handle_error(self, request, client_address):
		return SimpleXMLRPCServer.handle_error(self, request, client_address)

	def handle_timeout(self):
		return SimpleXMLRPCServer.handle_timeout(self)

	def server_close(self):
		return SimpleXMLRPCServer.server_close(self)

	def close_request(self, request_address):
		return SimpleXMLRPCServer.close_request(self, request_address)

	def server_bind(self):
		return SimpleXMLRPCServer.server_bind(self)

	def server_activate(self):
		return SimpleXMLRPCServer.server_activate(self)'''

class SSLServerProxy(ServerProxy):
	def __init__(self, _servaddr, TLS = False):
		if TLS :
			servaddr = 'https://' + _servaddr
		else :
			servaddr = 'http://' + _servaddr
		ServerProxy.__init__(self, servaddr)

		count = 0
		self.Ready = True
		while count < 10 :
			self.socketInit(TLS)
			if readSocketReady(self.socket, TIMEOUT) and writeSocketReady(self.socket, TIMEOUT) : break
			count += 1
		else :
			self.Ready = False
			return
		self.timeout = TIMEOUT
		self.socket.settimeout(self.timeout)

	def socketInit(self, TLS = False):
		if TLS :
			self.socket = ssl.wrap_socket(\
							socket.socket(socket.AF_INET, socket.SOCK_STREAM), \
							ca_certs = "/etc/ssl/ca_bundle.trust.crt", \
							ssl_version = ssl.PROTOCOL_TLSv1)
			#print '   TLS used on client ...'
		else :
			self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
