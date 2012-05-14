# -*- coding: utf-8 -*-

import ssl, socket, socks
from xmlrpclib import ServerProxy
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SocketServer import ThreadingMixIn
from Functions import readSocketReady, writeSocketReady, TIMEOUT, differentIP

def readProxySettings(socks, Settings):
	def take_value(arg):
		return None if arg == 'None' or arg.isEmpty() else arg.toLocal8Bit()
	_type = Settings.value('ProxyType', 'None').toString()
	if   _type is None : proxytype = None
	elif _type == 'HTTP' : proxytype = socks.PROXY_TYPE_HTTP
	elif _type == 'SOCKS4' : proxytype = socks.PROXY_TYPE_SOCKS4
	elif _type == 'SOCKS5' : proxytype = socks.PROXY_TYPE_SOCKS5
	else : proxytype = None
	_addr = Settings.value('ProxyAddr', 'None').toString()
	addr = take_value(_addr)
	_port = take_value(Settings.value('ProxyPort', 'None').toString())
	port = int(_port) if _port else None
	rdns = True if Settings.value('ProxyRDNS', 'True').toString()=='True' else False
	_name = Settings.value('ProxyUSER', 'None').toString()
	username = take_value(_name)
	_pass = Settings.value('ProxyPASS', 'None').toString()
	password = take_value(_pass)
	return proxytype, addr, port, rdns, username, password

def loadSocksModule(Settings, loadModule = None):
	proxyLoad = False
	reload(socket)
	if ( loadModule is None and Settings.value('UseProxy', 'False')=='True' ) or loadModule :
		## http://sourceforge.net/projects/socksipy/
		## or install the Fedora liked python-SocksiPy package
		try :
			import socks
			proxyLoad = True
		except : pass #proxyLoad = False
		finally :
			if proxyLoad :
				"""setdefaultproxy(proxytype, addr[, port[, rdns[, username[, password]]]])"""
				proxytype, addr, port, rdns, username, password = readProxySettings(socks, Settings)
				#print proxytype, addr, port, rdns, username, password
				socks.setdefaultproxy(proxytype, addr, port, rdns, username, password)
				socket.socket = socks.socksocket
	return proxyLoad

def enable_proxy(addr, Settings):
	res = False
	if differentIP(addr) not in ('', 'local') :
		if loadSocksModule(Settings, None) : res = True
	return res

class ThreadServer(ThreadingMixIn, SimpleXMLRPCServer):
	def __init__(self, serveraddr, allow_none = False, TLS = False, certificatePath = '', S = None):
		SimpleXMLRPCServer.__init__(self, serveraddr, bind_and_activate = False)
		enable_proxy(serveraddr[0], S)
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
	def __init__(self, _servaddr, TLS = False, certificatePath = '', S = None):
		_addr = _servaddr.split(':')
		enable_proxy(str(_addr[0]), S)
		if TLS :
			servaddr = 'https://' + _servaddr
		else :
			servaddr = 'http://' + _servaddr
		ServerProxy.__init__(self, servaddr)

		self.Ready = False
		addr = (str(_addr[0]), int(_addr[1]))
		self.socketInit(addr, TLS, certificatePath)
		if writeSocketReady(self.socket, TIMEOUT) :
			self.Ready = True

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
		#self.socket.setblocking(1)
		self.socket.connect(addr)
		self.timeout = TIMEOUT
		self.socket.settimeout(self.timeout)
		#print ssl.get_server_certificate(addr, ssl_version = ssl.PROTOCOL_TLSv1)
