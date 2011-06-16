# -*- coding: utf-8 -*-

import os, os.path, string, random, socket, ssl

char_set = string.ascii_letters + string.digits

def randomString( j = 1):
	#return "".join( [random.choice(string.letters) for i in xrange(j)] )
	return ''.join(random.sample(char_set, j))

class DataRendering:
	def __init__(self):
		pass

	def fileToList(self, path_ = ''):
		if os.path.isfile(path_) :
			f = open(path_, 'rb')
			l = f.read()
			f.close()
			s = string.split(l, '\n')
			for i in xrange(s.count('')) :
				s.remove('')
			return s
		else :
			return []

	def listToFile(self, list_ = [], name_ = ''):
		if name_ != '' :
			fileName = str('/dev/shm/' + name_)
			l = string.join(list_, '\n')
			f = open(fileName, 'wb')
			f.write(l)
			f.close()
			return fileName
		else :
			return ''

def InitConfigValue(Settings = None, key = None, default = None):
	if not Settings is None and Settings.contains(key) :
		return Settings.value(key).toString()
	else :
		return default

def getFreePort(minValue, maxValue):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	number_ = -1; 
	for i in xrange(maxValue - minValue) :
		try :
			s.bind(('127.0.0.1', minValue + i))
		except socket.error, x :
			#print x
			continue
		number_ = i
		break
	if number_ != -1 :
		addr, port = s.getsockname()
		s.close()
		return addr, port
	return '', 0

""" ssl socket examples """
def encryptData(data, (addr, port)):
	try :
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.bind((addr, port))
		sock.listen(5)
		print sock.getsockname(), '  own'
		while True :
			newsocket, fromaddr = sock.accept()
			print newsocket, fromaddr, '   end'
			ssl_sock = ssl.wrap_socket(newsocket, \
							server_side = True, \
							certfile = "./cert.pem",
							keyfile = "./cert.pem",
							ssl_version = ssl.PROTOCOL_TLSv1)
			print '    wrapped'
			try:
				#deal_with_client(ssl_sock)
				ssl_sock.write(str(data))
			#except socket.error, err: print err, ' internal errors'
			finally:
				print '--->>'
				ssl_sock.shutdown(socket.SHUT_RDWR)
				ssl_sock.close()
				print 'X'
			#ssl_sock.connect(('127.0.0.1', 56000))
			#ssl_sock.close()
	#except socket.error, err: print err, ' common errors'
	finally :
		#sock.close()
		print 'Exit'
		pass

def decryptData((addr, port), (listenAddr, listenPort)):
	try :
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.bind((addr, port))
		print '  bind'
		ssl_sock = ssl.wrap_socket(sock, \
							ca_certs = "/etc/ssl/ca_bundle.trust.crt", \
							ssl_version = ssl.PROTOCOL_TLSv1)
		print '  wrapped'
		ssl_sock.connect((listenAddr, listenPort))
		print '<--->'
		str_ = ssl_sock.read()
		print str_, ' <----'
		ssl_sock.close()
		print 'X'
	#except socket.error, err: print err
	finally :
		sock.close()
		print 'Exit'
