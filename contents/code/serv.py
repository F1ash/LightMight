# -*- coding: utf-8 -*-

import xmlrpclib, string, tarfile, os, os.path, ssl, socket
#from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from DocXMLRPCServer import DocXMLRPCServer, DocXMLRPCRequestHandler
from SocketServer import ThreadingMixIn
from Functions import *

class ThreadServer(ThreadingMixIn, DocXMLRPCServer):
	#ThreadingMixIn.daemon_threads = True
	def __init__(self, serveraddr, RequestHandlerClass, allow_none = False, TLS = False):
		DocXMLRPCServer.__init__(self, serveraddr, RequestHandlerClass)

		if TLS :
			self.socket = ssl.wrap_socket(\
							socket.socket(socket.AF_INET, socket.SOCK_STREAM), \
							ca_certs = "/etc/ssl/ca_bundle.trust.crt", \
							server_side = True, \
							certfile = os.path.expanduser("~/cert.pem"),
							keyfile = os.path.expanduser("~/cert.pem"),
							ssl_version = ssl.PROTOCOL_TLSv1)
			print '   TLS used on server...'
		else :
			self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		#self.funcs = {}
		self.logRequests = False		## disable logging """
		self.allow_none = allow_none
		self.server_bind()
		self.server_activate()

class ServerDaemon():
	def __init__(self, serveraddr = ('', 34000), commonSetOfSharedSource = None, parent = None, TLS = False):
		self.serverState = randomString(24)
		parent.serverState = self.serverState
		self.commonSetOfSharedSource = commonSetOfSharedSource
		self._srv = ThreadServer(serveraddr, DocXMLRPCRequestHandler, allow_none = True, TLS = TLS)
		#self._srv.set_server_title('PySADAM server')
		#self._srv.set_server_name('Example server') #TODO: need fix it
		#self._srv.set_server_documentation("""Welcome to""")
		#self._srv.register_instance(MainInterface(), allow_dotted_names=True)
		self._srv.register_introspection_functions()
		#self._srv.register_function(self.python_logo, 'python_logo')
		self._srv.register_function(self.python_clean, 'python_clean')
		#self._srv.register_function(self.typePath, 'typePath')
		self._srv.register_function(self.python_file, 'python_file')
		#self._srv.register_function(self.requestCatalogStruct, 'requestCatalogStruct')
		self._srv.register_function(self.requestSharedSourceStruct, 'requestSharedSourceStruct')
		self._srv.register_function(self.sessionID, 'sessionID')

	def sessionID(self):
		fileName = randomString(24)
		_id = randomString(24)
		#print '/dev/shm/LightMight/' + fileName, '  temporary file in sessionId'
		with open('/dev/shm/LightMight/' + fileName, 'wb') as f :
			f.write(fileName + '\n' + _id + '\n' + self.serverState + '\n')
		with open('/dev/shm/LightMight/' + fileName, "rb") as handle :
			return xmlrpclib.Binary(handle.read())

	def typePath(self, name):
		if os.path.isdir(name) :
			return True
		else :
			return False

	def readCatalogStruct(self, name, tarObj, listFile):
		#print name
		tarObj.add(name, None, False)
		for name_ in os.listdir(name):
			name_ = str(name + '/' + name_)
			if os.path.isdir(name_) :
				readCatalogStruct(name_, tarObj, listFile)
			else :
				listFile += [name_]

	def python_clean(self, name):
		if os.path.isfile('/dev/shm/LightMight/' + name) :
			os.remove('/dev/shm/LightMight/' + name)

	def python_logo(self, name):
		#os.chdir('/tmp')
		tar = tarfile.open(str(name + '.tar'), 'w|bz2')
		tar.add(name)
		tar.close()
		with open(str(name + '.tar'), "rb") as handle:
			return xmlrpclib.Binary(handle.read())

	def python_file(self, id_):
		""" добавить обработчик ошибок соединения и существования файлов """
		#print id_, type(id_), str(self.commonSetOfSharedSource[int(id_)]), '  serv'

		if int(id_) in self.commonSetOfSharedSource :
				with open(str(self.commonSetOfSharedSource[int(id_)]), "rb") as handle :
					return xmlrpclib.Binary(handle.read())

	def requestCatalogStruct(self, name, _id):
		listCatalogFiles = []
		fileList = str('/dev/shm/_struct_' + _id)
		f1 = tarfile.open(fileList, 'w|bz2')
		self.readCatalogStruct(name, f1, listCatalogFiles)
		#print listCatalogFiles, ' ===='
		fileName = DataRendering().listToFile(listCatalogFiles, str('_listFiles_' + _id))
		f1.add(fileName)
		f1.close()
		os.remove(fileName)
		with open(fileList, "rb") as handle:
			return xmlrpclib.Binary(handle.read())

	def requestSharedSourceStruct(self, name):
		#print '/dev/shm/LightMight/server/' + name, ' in requestSharedSourceStruct'
		with open('/dev/shm/LightMight/server/' + name, "rb") as handle:
			return xmlrpclib.Binary(handle.read())

	def run(self):
		self._srv.serve_forever()

	def _shutdown(self):
		self._srv.shutdown()
		print ' server terminated'

if __name__ == '__main__':

	try :
		d = ServerDaemon()
		d.run()
	except KeyboardInterrupt :
		d._shutdown()
		print '\nexit'
