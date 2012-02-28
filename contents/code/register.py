import select
import sys
import pybonjour

key = True
sdRef = None

def register_callback(sdRef, flags, errorCode, name, regtype, domain):
	if errorCode == pybonjour.kDNSServiceErr_NoError:
		print 'Registered service:'
		print '  name	=', name
		print '  regtype =', regtype
		print '  domain  =', domain

def main(_name, _port, _info = {}):
	global sdRef
	global key
	sdRef = pybonjour.DNSServiceRegister(name = _name,
									 regtype = '_LightMight._tcp',
									 port = _port,
									 callBack = register_callback,
									 txtRecord = pybonjour.TXTRecord(_info))
	try :
		while key :
			ready = select.select([sdRef], [], [])
			if sdRef in ready[0]:
				pybonjour.DNSServiceProcessResult(sdRef)
	except Exception : pass
	finally :
		sdRef.close()
		del sdRef
		#print 'service closed'
		return

def __del__():
	global key
	key = False

if __name__ == '__main__' :
	name = sys.argv[1]
	address = sys.argv[2]
	port = sys.argv[3]
	state = sys.argv[4]
	encode = sys.argv[5]
	info = \
		{'Encoding' : encode + ';', \
		 'Address' : address + ';', \
		 'Port' : port + ';', \
		 'Name' : name + ';', \
		 'State' : state + ';'}
	main(name, int(port), info)
