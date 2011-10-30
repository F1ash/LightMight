# -*- coding: utf-8 -*-

import ssl, socket
from xmlrpclib import ServerProxy
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SocketServer import ThreadingMixIn

class ThreadServer(ThreadingMixIn, SimpleXMLRPCServer):
	#ThreadingMixIn.daemon_threads = True
	def __init__(self, serveraddr, allow_none = False, TLS = False, certificatePath = ''):
		SimpleXMLRPCServer.__init__(self, serveraddr)

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

		self.logRequests = False		## disable logging """
		self.allow_none = allow_none
		self.timeout = 15
		self.server_bind()
		self.server_activate()

	def handle_request(self):
		return SocketServer.TCPServer.handle_request(self)

	def handle_error(self, request, client_address):
		return SocketServer.TCPServer.handle_error(self, request, client_address)

	def get_request(self):
		return SimpleXMLRPCServer.get_request(self)

	def verify_request(self, request, client_address):
		self.client_address = client_address
		#print repr(request), client_address
		return SimpleXMLRPCServer.verify_request(self, request, client_address)

	def process_request(self, request, client_address):
		return SimpleXMLRPCServer.process_request(self, request, client_address)

	def server_close(self):
		return SimpleXMLRPCServer.server_close(self)

	def finish_request(self, request, client_address):
		return SimpleXMLRPCServer.finish_request(self, request, client_address)

	def close_request(self, request_address):
		return SimpleXMLRPCServer.close_request(self, request_address)

	def server_bind(self):
		return SimpleXMLRPCServer.server_bind(self)

	def server_activate(self):
		return SimpleXMLRPCServer.server_activate(self)

class SSLServerProxy(ServerProxy):
	def __init__(self, _servaddr, TLS = False):
		if TLS :
			servaddr = 'https://' + _servaddr
		else :
			servaddr = 'http://' + _servaddr
		ServerProxy.__init__(self, servaddr)

		if TLS :
			self.socket = ssl.wrap_socket(\
							socket.socket(socket.AF_INET, socket.SOCK_STREAM), \
							ca_certs = "/etc/ssl/ca_bundle.trust.crt", \
							ssl_version = ssl.PROTOCOL_TLSv1)
			#print '   TLS used on client ...'
		else :
			self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
