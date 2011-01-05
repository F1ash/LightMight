# -*- coding: utf-8 -*-

import socket
import threading
import SocketServer
import xmlrpclib, string, os, time

def binData(addr):
	try :
		x = ''
		proxy = xmlrpclib.ServerProxy(str(addr))
		print os.getcwd()
		with open(os.getcwd() + '/' + "fetched_python_logo.jpg", "wb") as handle:
			#handle.write(proxy.python_logo().data)
			handle.write(time.strftime("_%Y_%m_%d_%H:%M:%S", time.localtime()))
	except IOError, x:
		print x, ' 0'
	except socket.error, x:
		print x, ' 1'
	except x:
		print x, ' 2'
	finally :
		#proxy.server_shutdown()
		print 'end serv_'

def client(ip, port, message):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((ip, port))
	sock.send(message + '_http://' + str(ip) + ':' + str(port))
	response = sock.recv(1024)
	print "Received: %s " % response
	sock.close()
	data = string.split(response, ' ')
	print data, ' data'
	addr = "http://" + data[1] + ':' + data[2] + '/'
	print addr, ' addr'
	p = threading.Thread(target = binData, args = [addr])
	p.start()

if __name__ == "__main__":
	# Port 0 means to select an arbitrary unused port
	#HOST, PORT = "localhost", 0

	#server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
	#ip, port = server.server_address
	#print ip, port, '__'

	# Start a thread with the server -- that thread will then start one
	# more thread for each request
	#server_thread = threading.Thread(target=server.serve_forever)
	# Exit the server thread when the main thread terminates
	#server_thread.setDaemon(True)
	#server_thread.start()
	#print "Server loop running in thread:", server_thread.getName()

	#client('127.0.0.1', 37905, "Hello World 1")
	#client(ip, port, "Hello World 2")
	#client(ip, port, "Hello World 3")
	for i in xrange(1):
		c = threading.Thread(target = client, args = ['127.0.0.1', 47396, "Hello World " + str(i)])
		c.start()
		#c.join()

