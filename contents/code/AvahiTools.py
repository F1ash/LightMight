# -*- coding: utf-8 -*-

import dbus, gobject, avahi, time, string, os.path
from dbus import DBusException
from dbus.mainloop.glib import DBusGMainLoop
from PyQt4 import QtCore, QtGui
from Functions import randomString  #, toolTipsHTMLWrap, InCache

class AvahiBrowser():
	def __init__(self, obj = None, parent = None):

		TYPE = '_LightMight._tcp'

		loop = DBusGMainLoop()
		bus = dbus.SystemBus(mainloop=loop)

		self.server = dbus.Interface( bus.get_object(avahi.DBUS_NAME, '/'),
									'org.freedesktop.Avahi.Server')

		sbrowser = dbus.Interface(bus.get_object(avahi.DBUS_NAME,
				self.server.ServiceBrowserNew(avahi.IF_UNSPEC,
					avahi.PROTO_UNSPEC, TYPE, 'local', dbus.UInt32(0))),
				avahi.DBUS_INTERFACE_SERVICE_BROWSER)

		sbrowser.connect_to_signal("ItemNew", self.myhandler)
		sbrowser.connect_to_signal("ItemRemove", self.myhandlerRemove)

		#gobject.MainLoop().run()
		self.obj = obj
		self.USERS = self.obj.USERS

	def extractValue(self, __str):
		_str_ = string.split(__str, '=')
		if len(_str_) > 1 :
			str__ = _str_[1]
		else :
			str__ = _str_[0]
		return str__

	def service_resolved(self, *args):
		str_ = string.join( avahi.txt_array_to_string_array(args[9]), '' )
		"""print 'name:', unicode(args[2])
		print 'address:', args[7]
		print 'port:', args[8]
		print str_
		print 'service resolved.'
		"""
		__str_state = ''; __str_encode = ''
		for _str in string.split(str_, '.') :
			if _str.startswith('Encoding=') :
				__str_encode = self.extractValue(_str)
				#break
			#else : __str_encode = _str
			if _str.startswith('State=') :
				__str_state = self.extractValue(_str)
		self.obj.addNewContact(unicode(args[2]), str(args[7]), str(args[8]), __str_encode, __str_state)
		'''new_item = QtGui.QListWidgetItem(unicode(args[2]))
		res_, path_ = InCache(__str_state)
		if res_ :
			head, tail = os.path.split(path_)
			new_item.setIcon(QtGui.QIcon(head + '/avatars/' + tail))
			new_item.setToolTip(toolTipsHTMLWrap(head + '/avatars/' + tail, \
								'name : ' + unicode(args[2]) + '<br>'\
								'\naddress : ' + str(args[7]) + '<br>'\
								'\nport : ' + str(args[8]) + '<br>'\
								'\nEncoding : ' + __str_encode + '<br>'\
								'\nServerState : ' + __str_state))
		else :
			new_item.setToolTip(toolTipsHTMLWrap('/dev/shm/LightMight/cache/avatars/' + __str_state, \
								'name : ' + unicode(args[2]) + '<br>'\
								'\naddress : ' + str(args[7]) + '<br>'\
								'\nport : ' + str(args[8]) + '<br>'\
								'\nEncoding : ' + __str_encode + '<br>'\
								'\nServerState : ' + __str_state))
		self.obj.userList.addItem(new_item)
		#self.USERS[args[2] + count] = (args[2], args[7], args[8])
		""" Keys of USERS defined by "name", because name may be changed in restart,
			but "state" may be not changed. In cache the important\exclusive role
			has the status of remote server.
		"""
		self.USERS[unicode(args[2])] = (unicode(args[2]), args[7], args[8], __str_encode, __str_state, False)
		#print self.USERS'''

	def print_error(self, *args):
		print 'error_handler'
		print args[0]

	def myhandlerRemove(self, interface, protocol, name, stype, domain, flags):

		item = self.obj.userList.findItems(name, \
				QtCore.Qt.MatchFlags(QtCore.Qt.MatchCaseSensitive))
		self.obj.userList.takeItem(self.obj.userList.row(item[0]))
		if unicode(name) in self.USERS : del self.USERS[unicode(name)]
		#print "Removed service: '%s'" % unicode(name)
		#print self.USERS

	def myhandler(self, interface, protocol, name, stype, domain, flags):
		#print "Found service '%s' type '%s' domain '%s' " % (unicode(name), stype, domain)

		if flags & avahi.LOOKUP_RESULT_LOCAL :
				# local service, skip
				pass

		self.server.ResolveService(interface, protocol, unicode(name), stype,
			domain, avahi.PROTO_UNSPEC, dbus.UInt32(0),
			reply_handler = self.service_resolved, error_handler = self.print_error)

	def __del__(self):
		#gobject.MainLoop().close()
		self.USERS.clear()
		pass

	def start(self): pass

class AvahiService():
	def __init__(self, obj = None, name = 'Own Demo Service', \
				description = 'No', port = 34100, parent = None):

		self.serviceName = unicode(name)
		self.serviceType = "_LightMight._tcp" # See http://www.dns-sd.org/ServiceTypes.html
		self.servicePort = port
		self.serviceTXT = description #TXT record for the service

		self.domain = "" # Domain to publish on, default to .local
		self.host = ""	##"flashcar.dyndns.org" # Host to publish records for, default to localhost

		self.group = None #our entry group
		self.rename_count = 12 # Counter so we only rename after collisions a sensible number of times

		DBusGMainLoop( set_as_default = True )

		self.main_loop = gobject.MainLoop()
		self.bus = dbus.SystemBus()

		self.server = dbus.Interface(
				self.bus.get_object( avahi.DBUS_NAME, avahi.DBUS_PATH_SERVER ),
				avahi.DBUS_INTERFACE_SERVER )

		self.server.connect_to_signal( "StateChanged", self.server_state_changed )
		self.server_state_changed( self.server.GetState() )

		"""try :
			main_loop.run()
		except KeyboardInterrupt :
			pass

		if not self.group is None :
			self.group.Free()"""

	def add_service(self):
		if self.group is None :
			self.group = dbus.Interface(
					self.bus.get_object( avahi.DBUS_NAME, self.server.EntryGroupNew()),
					avahi.DBUS_INTERFACE_ENTRY_GROUP)
			self.group.connect_to_signal('StateChanged', self.entry_group_state_changed)

		print "Adding service '%s' of type '%s' ..." % (QtCore.QString(self.serviceName).toUtf8(), self.serviceType)

		try :
			str_ = ''
			for i in xrange(len(self.serviceTXT)) :
				str_ += self.serviceTXT[len(self.serviceTXT) - 1 - i]
			self.group.AddService(
				avahi.IF_UNSPEC,	#interface
				avahi.PROTO_UNSPEC, #protocol
				dbus.UInt32(0),				  #flags
				self.serviceName, self.serviceType,
				self.domain, self.host,
				dbus.UInt16(self.servicePort),
				avahi.string_array_to_txt_array(str_))
			self.group.Commit()
		except dbus.exceptions.DBusException, err :
			""" DBusError :  org.freedesktop.Avahi.CollisionError: Local name collision """
			#print 'DBusError : ', err
			self.serviceName += '_' + randomString(3)
			self.add_service()
		finally :
			pass

	def remove_service(self):
		if not self.group is None :
			self.group.Reset()

	def server_state_changed(self, state):
		if state == avahi.SERVER_COLLISION :
			print "WARNING: Server name collision"
			self.remove_service()
		elif state == avahi.SERVER_RUNNING :
			self.add_service()

	def entry_group_state_changed(self, state, error):
		print "state change: %i" % state

		if state == avahi.ENTRY_GROUP_ESTABLISHED :
			print "Service established."
		elif state == avahi.ENTRY_GROUP_COLLISION :

			self.rename_count = self.rename_count - 1
			if self.rename_count > 0 :
				self.serviceName = self.server.GetAlternativeServiceName(self.serviceName)
				print "WARNING: Service name collision, changing name to '%s' ..." % QtCore.QString(self.serviceName).toUtf8()
				self.remove_service()
				self.add_service()

			else :
				print "ERROR: No suitable service name found after %i retries, exiting." % QtCore.QString(self.serviceName).toUtf8()
				self.main_loop.quit()
		elif state == avahi.ENTRY_GROUP_FAILURE :
			print "Error in group state changed", error
			self.main_loop.quit()
			return

	def __del__(self):
		self.remove_service()
		#self.main_loop.quit()
		time.sleep(3)			## FIXME: replace on dbus event

	def start(self): pass
