from xmlrpclib import ServerProxy
from threading import Thread
import os, os.path, tarfile

class dataRendering:
	def __init__(self, destinationFile = None, destinationList = None, turn = True):
		pass

class xr_client:
	def __init__(self):
		pass

	def _run(self):
		servaddr = 'http://localhost:35113'
		s = ServerProxy(servaddr)

		methods = s.system.listMethods()
		for m in methods:
			print(m), s.system.methodSignature(m)
		fileList = ["python_logo.jpg", 'clnt.py', 'iy']
		os.chdir('/tmp')
		for name in fileList :
			with open(str(name + '.my.tar'), "wb") as handle:
				handle.write(s.python_logo(name).data)
			s.python_clean(str(name + '.tar'))

		for name in fileList :
			tar = tarfile.open(str(name + '.my.tar'), 'r')
			tar.extractall()
			tar.close()
			os.remove(str(name + '.my.tar'))

	def run_(self):
		servaddr = 'http://localhost:35113'
		s = ServerProxy(servaddr)

		methods = s.system.listMethods()
		os.chdir('/tmp')
		fileList = ["python_logo.jpg", 'clnt.py', 'iy']
		for name in fileList :
			if s.typePath(name) :
				print True
				with open('/dev/shm/struct_', "wb") as handle:
					handle.write(s.requistCatalogStruct(name).data)
				tar = tarfile.open('/dev/shm/_struct', 'r')
				tar.extractall()
				tar.close()
				s.python_clean('/dev/shm/_struct')
				f = open(str(os.getcwd() + '/dev/shm/_listFiles'), 'rb')
				catalogFileList = f.readlines()
				f.close()
				os.remove(str(os.getcwd() + '/dev/shm/_listFiles'))
				os.remove(str('/dev/shm/struct_'))
				for name in catalogFileList :
					with open(name, "wb") as handle:
						handle.write(s.python_file(name).data)
			else :
				print False
				with open(name, "wb") as handle:
					handle.write(s.python_file(name).data)

if __name__ == '__main__':
	t = xr_client()
	t.run_()
