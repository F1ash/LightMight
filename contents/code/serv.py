
import xmlrpclib, string, tarfile, os, os.path
from DocXMLRPCServer import DocXMLRPCServer, DocXMLRPCRequestHandler
from SocketServer import ThreadingMixIn, ForkingMixIn

class ThreadServer(ThreadingMixIn, DocXMLRPCServer):pass

def typePath(name):
	if os.path.isdir(name) :
		return True
	else :
		return False

def readCatalogStruct(name, tarObj, listObj):
	tar = tarObj
	listFile = listObj
	print name
	tar.add(name, None, False)
	for name_ in os.listdir(name):
		if os.path.isdir(name_) :
			readCatalogStruct(name_, tar, listFile)
		else :
			listFile += [name_]

def parseFileList(name, tarObj) :
	tar = tarObj
	if os.path.isdir(name) :
		tar.add(name)
		#parseFileList(name, tar)
	elif os.path.isfile(name) :
		tar.add(name)

def python_clean(name):
	os.remove(name)

def python_logo(name):
	#os.chdir('/tmp')
	tar = tarfile.open(str(name + '.tar'), 'w|bz2')
	#parseFileList(name, tar)
	tar.add(name)
	tar.close()
	with open(str(name + '.tar'), "rb") as handle:
		return xmlrpclib.Binary(handle.read())

def python_file(name):
	#os.chdir('/tmp')
	with open(name, "rb") as handle:
		return xmlrpclib.Binary(handle.read())

def requistCatalogStruct(name):
	listCatalogFiles = []
	f1 = tarfile.open('/dev/shm/_struct', 'w|bz2')
	readCatalogStruct(name, f1, listCatalogFiles)
	f2 = open('/dev/shm/_listFiles', 'wb')
	f2.writelines(listCatalogFiles)
	f2.close()
	f1.add('/dev/shm/_listFiles')
	f1.close()
	os.remove('/dev/shm/_listFiles')
	with open('/dev/shm/_struct', "rb") as handle:
		return xmlrpclib.Binary(handle.read())

class Daemon:
	def __init__(self):
		self.serveraddr = ('', 35113)
		self._srv = ThreadServer(self.serveraddr, DocXMLRPCRequestHandler, allow_none=True)
		self._srv.set_server_title('PySADAM server')
		self._srv.set_server_name('Example server') #TODO: need fix it
		self._srv.set_server_documentation("""Welcome to""")
		#self._srv.register_instance(MainInterface(), allow_dotted_names=True)
		self._srv.register_introspection_functions()
		self._srv.register_function(python_logo, 'python_logo')
		self._srv.register_function(python_clean, 'python_clean')
		self._srv.register_function(typePath, 'typePath')
		self._srv.register_function(python_file, 'python_file')
		self._srv.register_function(requistCatalogStruct, 'requistCatalogStruct')

	def run(self):
		self._srv.serve_forever()

	def _shutdown(self):
		self._srv.shutdown()

if __name__ == '__main__':

	try :
		d = Daemon()
		d.run()
	except KeyboardInterrupt :
		d._shutdown()
		print '\nexit'
