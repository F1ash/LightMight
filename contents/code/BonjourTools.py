import select
import sys, string, socket, ctypes
import os, signal
import pybonjour, register
from PyQt4 import QtCore
from Functions import randomString, getIP

def pid_exists(pid, sig):
	try:
		os.kill(pid, sig)
		return True
	except OSError, err:
		return False

def reverseStr(s):
	lenStr = len(s)
	str_ = ''
	for i in xrange(lenStr) : str_ += s[lenStr - 1 - i]
	#print str_, 'reverse down'
	return str_

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
		if 'browse_sdRef' in dir(self) : self.browse_sdRef.close()

	def resolve_callback(self, sdRef, flags, interfaceIndex, errorCode, fullname,
						hosttarget, port, txtRecord):
		if errorCode == pybonjour.kDNSServiceErr_NoError :
			'''print 'Resolved service:'
			print '  fullname   =', fullname
			print '  hosttarget =', hosttarget
			print '  port	   =', port
			print '  Record 	= ', txtRecord.split(';')
			print '  InterfaceIndex = ' , interfaceIndex
			self.resolved.append(True)'''

			str_ = txtRecord.replace('\x01', '')

			if not str_.startswith('Name=') and str_.endswith('=gnidocnE') :
				str_raw = str_
				str_ = reverseStr(str_raw)
			__str_addr = ''; __str_port = ''; __str_encode = ''; __str_name = ''; __str_state = ''
			for _str in string.split(str_, ';') :
				if _str.rfind('Address=') > -1 :
					__str_addr = self.getRecord(_str)
				if _str.rfind('Port=') > - 1 :
					__str_port = self.getRecord(_str)
				if _str.rfind('Name=') > -1 :
					__str_name = self.getRecord(_str)
				if _str.rfind('State=') > -1 :
					__str_state = self.getRecord(_str)
				if _str.rfind('Encoding=') > -1 :
					__str_encode = self.getRecord(_str)

			## TODO : send info in pyqtSignal
			'''print [unicode(__str_name, 'utf-8'), __str_addr, __str_port, \
								   __str_encode, __str_state, \
								   fullname.partition('._tcp.')[2].split('.')[0], \
								   True]'''
			self.obj.addNewContact(unicode(__str_name, 'utf-8'), __str_addr, __str_port, \
								   __str_encode, __str_state, \
								   fullname.partition('._tcp.')[2].split('.')[0], \
								   True)

	def getRecord(self, str_):
		_str_ = string.split(str_, '=')
		if len(_str_) > 1 :
			return _str_[1]
		else :
			return _str_[0]

	def browse_callback(self, sdRef, flags, interfaceIndex, errorCode, serviceName,
						regtype, replyDomain):
		if errorCode != pybonjour.kDNSServiceErr_NoError :
			return

		if not (flags & pybonjour.kDNSServiceFlagsAdd):
			#print 'Service removed :'
			#print [flags, interfaceIndex, errorCode, serviceName,
			#			regtype, replyDomain.split('.')[0]]
			## TODO :  send [serviceName, regtype, replyDomain] in pyqtSignal
			## to delete service
			self.obj.delContact(serviceName, None, None, None, replyDomain.split('.')[0])
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
		#self.exit()

class AvahiService(QtCore.QThread):
	def __init__(self, obj = None, name = 'Own Demo Service', \
				description = 'No', port = 34100, parent = None):
		QtCore.QThread.__init__(self, parent)

		self.obj = obj
		self.name = unicode(name)
		self.regtype = '_LightMight._tcp'
		self.address = getIP()[0]
		self.port = str(port)
		self._encode, self._state, p, a, n = description.split(';')
		self.dataList = [0, False]

	def run(self):
		Data = QtCore.QStringList()
		Data.append('./register.py')
		Data.append(self.name)
		Data.append(self.address)
		Data.append(self.port)
		Data.append(self._state.split('=')[1])
		Data.append(self._encode.split('=')[1])
		self.Thread = QtCore.QProcess()
		start, pid = self.Thread.startDetached('python', Data, os.getcwd())
		self.dataList = [int(pid), start]
		#print self.dataList, 'run stopped'

	def __del__(self):
		print ' AvahiService terminated...'
		if self.dataList[1] and pid_exists(self.dataList[0], signal.SIGTERM) :
			#print  self.dataList[0], '  killed'
			pass
		else :
			#print  self.dataList[0], '  not exist'
			pass
		#self.exit()
