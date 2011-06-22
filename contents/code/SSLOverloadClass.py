# -*- coding: utf-8 -*-

import ssl, socket
from xmlrpclib import ServerProxy
from DocXMLRPCServer import DocXMLRPCServer, DocXMLRPCRequestHandler
from SocketServer import ThreadingMixIn

class ThreadServer(ThreadingMixIn, DocXMLRPCServer):
	#ThreadingMixIn.daemon_threads = True
	def __init__(self, serveraddr, RequestHandlerClass, allow_none = False, TLS = False, certificatePath = ''):
		DocXMLRPCServer.__init__(self, serveraddr, RequestHandlerClass)

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

		#self.funcs = {}
		self.logRequests = False		## disable logging """
		self.allow_none = allow_none
		self.server_bind()
		self.server_activate()

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
