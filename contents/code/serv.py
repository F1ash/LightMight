# -*- coding: utf-8 -*-

import socket
import threading
import SocketServer, time
from SimpleXMLRPCServer import SimpleXMLRPCServer
import xmlrpclib, os

def binData(ip, port):
	def python_logo():
		with open("python_logo.jpg", "rb") as handle:
			return xmlrpclib.Binary(handle.read())

	def server_shutdown(self):
		self.shutdown()
		self.close()

	try :
		x = ''
		server = SimpleXMLRPCServer((ip, port))
		print "Listening on port :", port, " Address :", ip
		print os.getcwd()
		server.register_function(python_logo, 'python_logo')
		server.register_function(server_shutdown(server), 'server_shutdown')
		print '=__='
		server.serve_forever()
		print '__==__'
	except IOError, x:
		print x, ' 0'
	except socket.error, x:
		print x, ' 1'
	except x:
		print x, ' 2'
	finally :
		print 'end serv_'

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

	def handle(self):

		data = self.request.recv(1024)
		print data, ' data'
		cur_thread = threading.currentThread()
		s = socket.socket()
		s.bind(('', 0))
		data = s.getsockname()
		#s.connect(('', data[1]))
		#s.shutdown(socket.SHUT_RDWR)
		s.close()

		p = threading.Thread(target = binData, args = [ip, data[1]])
		p.start()

		response = "%s %s %s" % (cur_thread.getName(), ip, data[1] )
		self.request.send(response)

class ThreadedTCPServer(SocketServer.ForkingMixIn, SocketServer.TCPServer):
	pass

def client(ip, port, message):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((ip, port))
	sock.send(message + '_http://' + str(ip) + ':' + str(port))
	response = sock.recv(1024)
	print "Received: %s" % response
	sock.close()

if __name__ == "__main__":
	# Port 0 means to select an arbitrary unused port
	HOST, PORT = "localhost", 0

	server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
	ip, port = server.server_address
	print ip, port, '__'

	# Start a thread with the server -- that thread will then start one
	# more thread for each request
	server_thread = threading.Thread(target=server.serve_forever)
	# Exit the server thread when the main thread terminates
	server_thread.setDaemon(True)
	server_thread.start()
	print "Server loop running in thread:", server_thread.getName()

	#client(ip, port, "Hello World 1")
	#client(ip, port, "Hello World 2")
	#client(ip, port, "Hello World 3")
	#for i in xrange(12):
	#	c = threading.Thread(target = client, args = [ip, port, "Hello World " + str(i)])
	#	c.start()
	#	c.join()

	try :
		while 1:
			time.sleep(10)
	except KeyboardInterrupt :
		server.shutdown()
		print '\nexit'
