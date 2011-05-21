# -*- coding: utf-8 -*-

import xmlrpclib, string, tarfile, os, os.path
from DocXMLRPCServer import DocXMLRPCServer, DocXMLRPCRequestHandler
from SocketServer import ThreadingMixIn, ForkingMixIn
from Functions import *

def sessionID():
	fileName = str('/dev/shm/' + randomString(24))
	_id = randomString(24)
	f = open(fileName, 'wb')
	f.write(str(fileName + '\n' + _id + '\n'))
	f.close()
	with open(fileName, "rb") as handle:
		return xmlrpclib.Binary(handle.read())

class ThreadServer(ThreadingMixIn, DocXMLRPCServer): pass

def typePath(name):
	if os.path.isdir(name) :
		return True
	else :
		return False

def readCatalogStruct(name, tarObj, listFile):
	#print name
	tarObj.add(name, None, False)
	for name_ in os.listdir(name):
		name_ = str(name + '/' + name_)
		if os.path.isdir(name_) :
			readCatalogStruct(name_, tarObj, listFile)
		else :
			listFile += [name_]

def python_clean(name):
	os.remove(name)

def python_logo(name):
	#os.chdir('/tmp')
	tar = tarfile.open(str(name + '.tar'), 'w|bz2')
	tar.add(name)
	tar.close()
	with open(str(name + '.tar'), "rb") as handle:
		return xmlrpclib.Binary(handle.read())

def python_file(name):
	#os.chdir('/tmp')
	if not os.path.isfile(name) :
		f =  open(name, 'wb')
		f.write(str('File ' + name + ' not found in server.\n'))
		f.close()
	with open(name, "rb") as handle:
		return xmlrpclib.Binary(handle.read())

def requestCatalogStruct(name, _id):
	listCatalogFiles = []
	fileList = str('/dev/shm/_struct_' + _id)
	f1 = tarfile.open(fileList, 'w|bz2')
	readCatalogStruct(name, f1, listCatalogFiles)
	#print listCatalogFiles, ' ===='
	fileName = DataRendering().listToFile(listCatalogFiles, str('_listFiles_' + _id))
	f1.add(fileName)
	f1.close()
	os.remove(fileName)
	with open(fileList, "rb") as handle:
		return xmlrpclib.Binary(handle.read())

class ServerDaemon():
	def __init__(self, serveraddr = ('', 35113)):
		self._srv = ThreadServer(serveraddr, DocXMLRPCRequestHandler, allow_none = True)
		self._srv.set_server_title('PySADAM server')
		self._srv.set_server_name('Example server') #TODO: need fix it
		self._srv.set_server_documentation("""Welcome to""")
		#self._srv.register_instance(MainInterface(), allow_dotted_names=True)
		self._srv.register_introspection_functions()
		self._srv.register_function(python_logo, 'python_logo')
		self._srv.register_function(python_clean, 'python_clean')
		self._srv.register_function(typePath, 'typePath')
		self._srv.register_function(python_file, 'python_file')
		self._srv.register_function(requestCatalogStruct, 'requestCatalogStruct')
		self._srv.register_function(sessionID, 'sessionID')

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
