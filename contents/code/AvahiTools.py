# -*- coding: utf-8 -*-

import dbus, gobject, avahi, time
from dbus import DBusException
from dbus.mainloop.glib import DBusGMainLoop
from PyQt4 import QtCore, QtGui

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
		self.USERS = {}

	def service_resolved(self, *args):
		print 'name:', args[2]
		print 'address:', args[7]
		print 'port:', args[8]
		print 'service resolved.'

		""" для различения одинаковых имён служб (но Avahi не регистрирует одинаковые имена)
		item = self.obj.userList.findItems(args[2], \
				QtCore.Qt.MatchFlags(QtCore.Qt.MatchStartsWith | QtCore.Qt.MatchCaseSensitive))
		count = ''
		if len(item) > 0 :
			count = "(" + str(len(item)) + ")"
		new_item = QtGui.QListWidgetItem(args[2] + count)
		"""
		new_item = QtGui.QListWidgetItem(args[2])
		new_item.setToolTip('name : ' + str(args[2]) + '\naddress : ' + str(args[7]) + '\nport : ' + str(args[8]))
		self.obj.userList.addItem(new_item)
		#self.USERS[args[2] + count] = (args[2], args[7], args[8])
		self.USERS[args[2]] = (args[2], args[7], args[8])
		#print self.USERS

	def print_error(self, *args):
		print 'error_handler'
		print args[0]

	def myhandlerRemove(self, interface, protocol, name, stype, domain, flags):

		item = self.obj.userList.findItems(name, \
				QtCore.Qt.MatchFlags(QtCore.Qt.MatchStartsWith | QtCore.Qt.MatchCaseSensitive))
		self.obj.userList.takeItem(self.obj.userList.row(item[0]))
		del self.USERS[name]
		print "Removed service: '%s'" % name
		#print self.USERS

	def myhandler(self, interface, protocol, name, stype, domain, flags):
		print "Found service '%s' type '%s' domain '%s' " % (name, stype, domain)

		if flags & avahi.LOOKUP_RESULT_LOCAL :
				# local service, skip
				pass

		self.server.ResolveService(interface, protocol, name, stype,
			domain, avahi.PROTO_UNSPEC, dbus.UInt32(0),
			reply_handler = self.service_resolved, error_handler = self.print_error)

	def __del__(self):
		#gobject.MainLoop().close()
		del self.USERS
		pass

class AvahiService():
	def __init__(self, obj = None, name = 'Own Demo Service', \
				description = '', port = 34100, parent = None):

		self.serviceName = name
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

		print "Adding service '%s' of type '%s' ..." % (self.serviceName, self.serviceType)

		self.group.AddService(
				avahi.IF_UNSPEC,	#interface
				avahi.PROTO_UNSPEC, #protocol
				dbus.UInt32(0),				  #flags
				self.serviceName, self.serviceType,
				self.domain, self.host,
				dbus.UInt16(self.servicePort),
				avahi.string_array_to_txt_array(self.serviceTXT))
		self.group.Commit()

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
				print "WARNING: Service name collision, changing name to '%s' ..." % self.serviceName
				self.remove_service()
				self.add_service()

			else :
				print "ERROR: No suitable service name found after %i retries, exiting." % self.serviceName
				self.main_loop.quit()
		elif state == avahi.ENTRY_GROUP_FAILURE :
			print "Error in group state changed", error
			self.main_loop.quit()
			return

	def __del__(self):
		self.remove_service()
		#self.main_loop.quit()
		time.sleep(3)			## Fix me: replace on d-bus event
