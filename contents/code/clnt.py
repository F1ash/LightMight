from xmlrpclib import ServerProxy
from threading import Thread
import os, os.path, tarfile

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
			s.python_clean(name)

		for name in fileList :
			tar = tarfile.open(str(name + '.my.tar'), 'r')
			tar.extractall()
			tar.close()
			os.remove(str(name + '.my.tar'))

if __name__ == '__main__':
	t = xr_client()
	t._run()
