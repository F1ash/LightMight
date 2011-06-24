import select
import sys, string
import pybonjour
from PyQt4 import QtCore, QtGui
from Functions import randomString

class AvahiBrowser(QtCore.QThread):
	def __init__(self, obj = None, parent = None):
		QtCore.QThread.__init__(self, parent)

		self.obj = obj
		self.RUN = True
		self.USERS = {}

		self.regtype = '_LightMight._tcp'
		self.timeout = 5
		self.resolved = []

		self.browse_sdRef = pybonjour.DNSServiceBrowse(regtype = self.regtype,
												callBack = self.browse_callback)
		self.start()

	def run(self):
		while self.RUN :
			ready = select.select([self.browse_sdRef], [], [])
			if self.browse_sdRef in ready[0] :
				pybonjour.DNSServiceProcessResult(self.browse_sdRef)

	def resolve_callback(self, sdRef, flags, interfaceIndex, errorCode, fullname,
						hosttarget, port, txtRecord, serviceName):
		if errorCode == pybonjour.kDNSServiceErr_NoError :
			print 'Resolved service:'
			print '  fullname   =', fullname
			print '  hosttarget =', hosttarget
			print '  port	   =', port
			print '  Record 	= ', str(txtRecord)
			print '  InterfaceIndex = ' , interfaceIndex
			print '  Service Name = ', unicode(serviceName)
			self.resolved.append(True)

			str_ = unicode(txtRecord)
			"""for i in xrange(len(txtRecord)) :
				str_ += txtRecord[len(txtRecord) - 1 - i]"""
			for _str in string.split(str_, '.') :
				if _str.startswith('Encoding=') :
					__str = _str
					break
				else : __str = _str
			_str_ = string.split(__str, '=')
			if len(_str_) > 1 :
				str__ = _str_[1]
			else :
				str__ = _str_[0]

			new_item = QtGui.QListWidgetItem(unicode(serviceName))
			new_item.setToolTip('name : ' + unicode(serviceName) + \
								'\naddress : ' + hosttarget + \
								'\nport : ' + str(port) + \
								'\nEncoding : ' + str__)
			self.obj.userList.addItem(new_item)
			self.USERS[unicode(serviceName)] = (unicode(serviceName), hosttarget, port, str__)
			#print self.USERS

	def browse_callback(self, sdRef, flags, interfaceIndex, errorCode, serviceName,
						regtype, replyDomain):
		if errorCode != pybonjour.kDNSServiceErr_NoError :
			return

		if not (flags & pybonjour.kDNSServiceFlagsAdd) :

			item = self.obj.userList.findItems(serviceName, \
					QtCore.Qt.MatchFlags(QtCore.Qt.MatchCaseSensitive))
			print item, ' find list'
			if len(item) > 0 :
				self.obj.userList.takeItem(self.obj.userList.row(item[0]))
				if unicode(serviceName) in self.USERS : del self.USERS[unicode(serviceName)]
				print 'Service removed :'
				print '  fullname   =', serviceName
				print '  replyDomain 	= ', replyDomain
				print '  InterfaceIndex = ' , interfaceIndex
			else :
				print '  item not found'
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
				ready = select.select([self.resolve_sdRef], [], [], self.timeout)
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
		self.USER.clear()
		if 'browse_sdRef' in dir(self) : self.browse_sdRef.close()
		self.exit()

class AvahiService(QtCore.QThread):
	def __init__(self, obj = None, name = 'Own Demo Service', \
				description = 'No', port = 34100, parent = None):
		QtCore.QThread.__init__(self, parent)

		self.obj = obj
		self.RUN = True
		self.name = unicode(name)
		self.regtype = '_LightMight._tcp'
		self.port = port
		unicalName = False

		""" instance 'txtRecord' must finished by '\n' always """
		while not unicalName :
			try :
				self.sdRef = pybonjour.DNSServiceRegister(name = self.name,
									 regtype = self.regtype,
									 port = self.port,
									 txtRecord = pybonjour.TXTRecord(
														{'Encoding' : description + '\n'}
																	),
									 callBack = self.register_callback)
			except pybonjour.BonjourError, err :
				print 'PyBonjourError : ', err
				self.name += '_' + randomString(3)
			finally :
				if 'sdRef' in dir(self) : unicalName = True
		self.start()

	def run(self):
		while self.RUN :
			ready = select.select([self.sdRef], [], [])
			if self.sdRef in ready[0] :
				pybonjour.DNSServiceProcessResult(self.sdRef)

	def register_callback(self, sdRef, flags, errorCode, name, regtype, domain, host, port):
		if errorCode == pybonjour.kDNSServiceErr_NoError :
			print 'Registered service:'
			print '  name	=', name
			print '  regtype =', regtype
			print '  domain  =', domain
			print '  host = ', host
			print '  port	= ', port

	def __del__(self):
		self.RUN = False
		if 'sdRef' in dir(self) : self.sdRef.close()
		print ' AvaviService terminated...'
		self.exit()
