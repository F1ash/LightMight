# -*- coding: utf-8 -*-

import os, os.path, string, random, socket, ssl, time, re, urllib2, select
import hashlib
import cStringIO as S
import M2Crypto as MC
from Path import Path

SESSION_MISMATCH = -12
SERVER_STATE_MISMATCH = -13

def mix(): return random.randint(0, 1)

def cB (*args, **kwrds):
	return '\n'

def createCertificate():
	rsaKey = MC.RSA.gen_key(2048, 65537)
	rsaKey.save_key(Path.config('prvKey.pem'), cipher = None, callback = cB )
	rsaKey.save_pub_key(Path.config('pubKey.pem'))

def pubKeyEncrypted(str_, key_):
	s = S.StringIO(key_)
	bio = MC.BIO.MemoryBuffer(s.read())
	rsa = MC.RSA.load_pub_key_bio(bio)
	encrypted = ''
	try :
		encrypted = rsa.public_encrypt(str_, MC.RSA.pkcs1_oaep_padding)
	except MC.RSA.RSAError, err :
		print 'M2Crypto.RSA.RSAError', err
	finally : pass
	s.close()
	return encrypted

def prvKeyDecrypted(str_, key_):
	s = S.StringIO(key_)
	rsa = MC.RSA.load_key_string(s.read())
	decrypted = ''
	try :
		decrypted = rsa.private_decrypt(str_, MC.RSA.pkcs1_oaep_padding)
	except MC.RSA.RSAError, err :
		print 'M2Crypto.RSA.RSAError', err
	finally : pass
	s.close()
	return decrypted

def hashKey(str_):
	m = hashlib.sha256()
	m.update(str_)
	return m.hexdigest()

def readCashPolicy(str_, policy):
	fileName = hashKey(str_)
	path_ = Path.certificates(fileName)
	if os.path.isfile(path_) :
		with open(path_, 'rb') as f :
			data = f.read()
		chunks = data.split()
		policy = int(chunks[len(chunks) - 1])
	return policy

def addToCertCache(str_, policy):
	fileName = hashKey(str_)
	path_ = Path.certificates(fileName)
	if not os.path.isfile(path_) :
		with open(path_, 'wb') as f :
			f.write(''.join((str_.encode('utf-8'), str(policy))))
	else :
		with open(path_, 'rb') as f :
			data = f.read()
		chunks = data.split()
		policy = int(chunks[len(chunks) - 1])
	return policy

def saveContactPolicy(idx, fileName):
	path = Path.certificates(fileName)
	if not os.path.isfile(path) : return ''
	with open(path, 'rb') as f :
		str_ = f.read()
	(head, sep, tail) = str_.partition('\n-----END PUBLIC KEY-----\n')
	with open(path, 'wb') as f :
		str_ = ''.join((head, sep, str(idx)))
		f.write(str_)

def readPubKeyFromCache(_keyHash):
	path = Path.certificates(_keyHash)
	if not os.path.isfile(path) : return ''
	with open(path, 'rb') as f :
		str_ = f.read()
	(head, sep, tail) = str_.partition('\n-----END PUBLIC KEY-----')
	return ''.join((head, sep)).encode('utf-8')

def createEncryptedSessionID(sessionID_, pubKeyHash):
	pubKey = readPubKeyFromCache(pubKeyHash)
	if mix() :
		mixtureString = ''.join((sessionID_, randomString(DIGITS_LENGTH)))
	else :
		mixtureString = ''.join((randomString(DIGITS_LENGTH), sessionID_))
	#print [sessionID_, pubKey, mixtureString]
	sessionID = '' if pubKey == '' else pubKeyEncrypted(mixtureString, pubKey).encode('base64')
	return sessionID

char_set = string.ascii_letters + string.digits
DIGITS_LENGTH = 24
TIMEOUT = 30.0

pattern = "[1-9]+[0-9]?[0-9]?\.[0-9]+[0-9]?[0-9]?\.[0-9]+[0-9]?[0-9]?\.[0-9]+[0-9]?[0-9]?"
ip_re = re.compile(pattern)
CHECK_SERVICES = ('http://www.viewmyipaddress.com/', 'http://api.wipmania.com/', 'http://checkip.dyndns.org')

def correct_ip(ip = ''):
	findIP = ip_re.findall(ip)

	if findIP == [] :
		return False
	else :
		segment = findIP[0].split('.')
	for i in segment :
		dig = string.atoi(i)
		if dig > 255 :
			return False
	return True

def differentIP(ip = ''):
	if not correct_ip(ip) : return ''
	segment = ip.split('.')
	if segment[0] in ('10', '127') : return 'local'
	dig = string.atoi(segment[1])
	if segment[0] == '172' and dig < 32 and dig > 15 : return 'local'
	elif segment[0] == '192' and dig == 168 : return 'local'
	elif segment[0] == '169' and dig == 254 : return 'local'
	return ip

def getExternalIP():
	ip = ''
	for addr in CHECK_SERVICES :
		try :
			f = urllib2.urlopen(urllib2.Request(addr))
			response = f.read()
			f.close()
			ip_ = ip_re.findall(response)
			if ip_ == [] : continue
			ip = ip_[0]
			break
		except urllib2.URLError, err:
			print err
		finally : pass
	return ip

def readSocketReady(sock, timeout = TIMEOUT):
	ready_to_read, ready_to_write, in_error = select.select([sock], [], [], timeout)
	if sock in ready_to_read : return True
	else :
		sock.shutdown(socket.SHUT_RD)
		sock.close()
		return False

def writeSocketReady(sock, timeout = TIMEOUT):
	ready_to_read, ready_to_write, in_error = select.select([], [sock], [], timeout)
	if sock in ready_to_write : return True
	else :
		sock.shutdown(socket.SHUT_WR)
		sock.close()
		return False

def createStructure():
	for nameDir in [Path.TempAvatar, \
					Path.tempStruct('structure'), \
					Path.tempStruct('client'), \
					Path.tempStruct('server'), \
					Path.config('treeBackup'), \
					Path.Avatar, \
					Path.Certificates] :
		if not os.path.isdir(nameDir):
			os.makedirs(nameDir)
	cwd = os.getcwd()
	while os.path.basename(cwd) not in (os.sep, '', 'LightMight') :
		head, tail = os.path.split(cwd)
		cwd = head
	if os.path.basename(cwd) == 'LightMight' :
		moveFile(os.path.join(cwd, 'contents', 'icons', 'error.png'), \
							  os.path.join(Path.TempAvatar, 'error'), \
							  False)

def randomString( j = 1):
	return ''.join(random.sample(char_set, j))

class DataRendering:
	def __init__(self):
		pass

	def fileToList(self, path_ = ''):
		s = []
		if os.path.isfile(path_) :
			with open(path_, 'rb') as f :
				while True :
					s.append(f.readline(DIGITS_LENGTH))
					if s[len(s) - 1] == '' : break
		return s

	def listToFile(self, list_ = [], name_ = ''):
		fileName = ''
		if name_ != '' :
			fileName = Path.tempStruct(name_)
			with open(fileName, 'wb') as f :
				f.writelines(list_)
		return fileName

def InitConfigValue(Settings = None, key = None, default = None):
	return Settings.value(key, default).toString()

def getIP():
	msg = ''
	j = 0
	Addr = '127.0.0.1'
	addressList = (("gmail.com", 80), ('0.0.0.0', 34001))
	for address in addressList :
		j += 1
		for i in xrange(5) :
			try :
				error = False
				s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				s.connect(address)
				addr = s.getsockname()[0]
			except socket.gaierror, err:
				#print '[in getIP()]:', err
				error = True
			except Exception, err:
				#print '[in getIP()]:', err
				error = True
			finally :
				s.close()
			if not error :
				Addr = addr
				break
		if Addr not in ('', '0.0.0.0', '127.0.0.1') :
			j = 0
			break
		elif j == 1 :
			msg += 'Internet not available\n'
		elif j == 2 :
			msg += 'Local network not available'
	#print msg, j
	return Addr, msg, j

def getFreePort(minValue, maxValue, addr = '127.0.0.1'):
	number_ = -1
	for i in xrange(maxValue - minValue) :
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try :
			s.bind((addr, minValue + i))
		except socket.error, x :
			s.close()
			#print x
			continue
		number_ = i
		break
	if number_ != -1 :
		addr, port = s.getsockname()
		s.close()
		return addr, port
	s.close()
	return '', 0

def dateStamp():
	return time.strftime("%Y.%m.%d_%H:%M:%S", time.localtime())

def moveFile(src, dst, delete = True):
	if os.path.isfile(src) :
		dst_dir = os.path.dirname(dst)
		if not os.path.isdir(dst_dir) :
			try :
				os.makedirs(dst_dir)
			except OSError, err :
				return False
		#print src, dst
		if src == dst :
			if delete and os.path.isfile(src) : os.remove(src)
			return True
		with open(src, 'rb') as srcFile :
			with open(dst, 'wb') as dstFile :
				dstFile.write(srcFile.read())
		if delete and os.path.isfile(srcFile.name) : os.remove(srcFile.name)
		return True
	else :
		return False

def pathPrefix():
	if Path.platform == 'win':
		return unicode(os.path.dirname(os.tempnam()))
	else:
		return u''

def toolTipsHTMLWrap(iconPath = '', text = ''):
	return \
	'<table width="100%" border="0">\
		<col align="center" />\
		<col align="left"  width="100%" />\
		<tr>\
			<td><img src="' + iconPath + '" alt="" /></td>\
			<td>' + text + '</td>\
		</tr>\
	</table>'

def InCache(str_ = ''):
	if os.path.isfile(Path.tempCache(str_)) :
		return True, Path.tempCache(str_)
	elif os.path.isfile(Path.cache(str_)) :
		return True, Path.cache(str_)
	return False, ''

def avatarInCache(str_ = ''):
	if os.path.isfile(Path.tempAvatar(str_)) :
		return True, Path.tempAvatar(str_)
	elif os.path.isfile(Path.avatar(str_)) :
		return True, Path.avatar(str_)
	return False, ''

def DelFromCache(str_):
	i = 0
	result = [False, False, False, False]
	for path_ in [Path.TempCache, \
				 Path.TempAvatar, \
				 Path.Cache, \
				 Path.Avatar] :
		path = os.path.join(path_, str_)
		if os.path.isfile(path) :
			os.remove(path)
			result[i] = True
		i += 1
	return result

def getFolderSize(folder):
	total_size = os.path.getsize(folder)
	for item in os.listdir(folder) :
		itempath = os.path.join(folder, item)
		if os.path.isfile(itempath) :
			total_size += os.path.getsize(itempath)
		elif os.path.isdir(itempath) :
			total_size += getFolderSize(itempath)
	return total_size
