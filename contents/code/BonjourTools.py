import select
import sys, string, socket, ctypes
import pybonjour
from PyQt4 import QtCore
from Functions import randomString, getIP

class AvahiBrowser(QtCore.QThread):
	def __init__(self, obj = None, parent = None):
		QtCore.QThread.__init__(self, parent)

		self.obj = obj.Obj
		self.RUN = True
		self.USERS = self.obj.USERS

		self.regtype = '_LightMight._tcp'
		self.timeout = 5
		self.resolved = []

		self.browse_sdRef = pybonjour.DNSServiceBrowse(regtype = self.regtype,
												callBack = self.browse_callback)
		#self.start()

	def run(self):
		while self.RUN :
			ready = select.select([self.browse_sdRef], [], [])
			if self.browse_sdRef in ready[0] :
				pybonjour.DNSServiceProcessResult(self.browse_sdRef)

	def resolve_callback(self, sdRef, flags, interfaceIndex, errorCode, fullname,
						hosttarget, port, txtRecord):
		if errorCode == pybonjour.kDNSServiceErr_NoError :
			"""print 'Resolved service:'
			print '  fullname   =', fullname
			print '  hosttarget =', hosttarget
			print '  port	   =', port
			print '  Record 	= ', str(txtRecord)
			print '  InterfaceIndex = ' , interfaceIndex"""
			self.resolved.append(True)

			str_ = txtRecord
			__str_addr = ''; __str_port = ''; __str_encode = ''; __str_name = ''; __str_state = ''
			for _str in string.split(str_, ';') :
				if _str.rfind('Address=') > -1 :
					__str_addr = self.getRecord(_str)
				if _str.rfind('Port=') > - 1 :
					__str_port = self.getRecord(_str)
				if _str.rfind('Encoding=') > -1 :
					__str_encode = self.getRecord(_str)
				if _str.rfind('Name=') > -1 :
					__str_name = self.getRecord(_str)
				if _str.rfind('State=') > -1 :
					__str_state = self.getRecord(_str)

			self.obj.addNewContact(unicode(__str_name, 'utf-8'), __str_addr, __str_port, \
								   __str_encode, __str_state, \
								   fullname.partition('._')[1].partition('.')[1])

	def getRecord(self, str_):
		_str_ = string.split(str_, '=')
		if len(_str_) > 1 :
			return _str_[1]
		else :
			return _str_[0]

	def browse_callback(self, sdRef, flags, interfaceIndex, errorCode, serviceName,
						regtype, replyDomain):
		print errorCode, '   errCode'
		if errorCode != pybonjour.kDNSServiceErr_NoError :
			return

		if not (flags & pybonjour.kDNSServiceFlagsAdd) :
			self.obj.delContact(serviceName, None, None, None, replyDomain)
			return

		print 'Service added; resolving'

		self.resolve_sdRef = pybonjour.DNSServiceResolve(0,
														interfaceIndex,
														serviceName,
														regtype,
														replyDomain,
														self.resolve_callback)

		try :
			while not self.resolved :
				try :
					ready = select.select([self.resolve_sdRef], [], [], self.timeout)
				except ctypes.ArgumentError, err :
					print 'CTypesArgumentError : ', err
				#finally : pass
				if self.resolve_sdRef not in ready[0] :
					print 'Resolve timed out'
					break
				pybonjour.DNSServiceProcessResult(self.resolve_sdRef)
			else :
				self.resolved.pop()
		finally :
			self.resolve_sdRef.close()

	def __del__(self):
		self.RUN = False
		self.USERS.clear()
		if 'browse_sdRef' in dir(self) : self.browse_sdRef.close()
		#self.exit()

class AvahiService(QtCore.QThread):
	def __init__(self, obj = None, name = 'Own Demo Service', \
				description = 'No', port = 34100, parent = None):
		QtCore.QThread.__init__(self, parent)

		self.obj = obj
		self.RUN = True
		self.name = unicode(name)
		self.regtype = '_LightMight._tcp'
		self.address = getIP()[0]
		self.port = port
		unicalName = False
		_encode, _state = description.split('.')

		while not unicalName :
			try :
				self.sdRef = pybonjour.DNSServiceRegister(name = self.name,
									 regtype = self.regtype,
									 port = self.port,
									 txtRecord = pybonjour.TXTRecord(
														{'Encoding' : _encode.split('=')[1] + ';',
														 'Address' : self.address + ';',
														 'Port' : str(self.port) + ';',
														 'Name' : self.name + ';',
														 'State' : _state.split('=')[1] + ';'}
																	),
									 callBack = self.register_callback)
			except pybonjour.BonjourError, err :
				print 'PyBonjourError : ', err
				self.name += '_' + randomString(3)
			finally :
				if 'sdRef' in dir(self) : unicalName = True
		#self.start()

	def run(self):
		while True :
			try :
				ready = select.select([self.sdRef], [], [])
			except ctypes.ArgumentError, err :
				print 'CTypesArgumentError : ', err
				#ready = [([pybonjour.DNSServiceRef()], '')]
			if self.sdRef in ready[0] :
				pybonjour.DNSServiceProcessResult(self.sdRef)
			if not self.RUN :
				if 'sdRef' in dir(self) :
					self.sdRef.close()
					break

	def register_callback(self, sdRef, flags, errorCode, name, regtype, domain):
		if errorCode == pybonjour.kDNSServiceErr_NoError :
			print 'Registered service:'
			print '  name	=', name
			print '  regtype =', regtype
			print '  domain  =', domain
		else :
			print ' Registration Error : ', errorCode

	def __del__(self):
		self.RUN = False
		print ' AvahiService terminated...'
		#self.exit()
