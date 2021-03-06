# encoding: utf-8
import logging
import BaseHTTPServer
import smisk.util.fcgiproto as fcgi
import socket
import os
import mimetools
import time
from smisk import __version__ as smisk_version
from cStringIO import StringIO

log = logging.getLogger(__name__)


class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
	def __init__(self, *va, **kw):
		log.debug('handler init')
		self.server_version = 'smiskhttpd/%s' % smisk_version
		#self.protocol_version = 'HTTP/1.1' # todo 1.1 support, like chunked enc.
		BaseHTTPServer.BaseHTTPRequestHandler.__init__(self, *va, **kw)
	
	def handle_one_request(self):
		self.raw_requestline = self.rfile.readline()
		if not self.raw_requestline:
			self.close_connection = 1
			return
		if not self.parse_request(): # An error code has been sent, just exit
			return
		try:
			ch = self.server.get_fcgi_backend()
			if not ch:
				log.error('fastcgi error: backend unavailable')
				try:
					self.send_response(503, 'Service Unavailable')
					self.wfile.write('\r\n503 Service Unavailable (FastCGI backend unavailable)\n')
				except:
					pass
			else:
				try:
					self.handle_fcgi_request(ch)
				finally:
					self.server.put_fcgi_backend(ch)
		except socket.error, e:
			log.error('fastcgi channel error: %s', e, exc_info=1)
		except:
			log.error('server error while handing request:', exc_info=1)
	
	def send_response(self, code, message=None):
		self.log_request(code)
		if message is None:
			if code in self.responses:
				message = self.responses[code][0]
			else:
				message = ''
		if self.request_version != 'HTTP/0.9':
			self.wfile.write("%s %d %s\r\n" %
							 (self.protocol_version, code, message))
	
	def handle_fcgi_request(self, ch):
		rid = 1
		content_length = 0
		query_string = ''
		if '?' in self.path:
			query_string = self.path[self.path.index('?')+1:]
		params = {
			'GATEWAY_INTERFACE': 'CGI/1.1',
			'PATH_INFO': '',
			'QUERY_STRING': query_string,
			'REMOTE_ADDR': self.client_address[0],
			'REMOTE_HOST': self.server.fqdn,
			'REQUEST_METHOD': self.command,
			'SCRIPT_NAME': '/' + self.path.lstrip('/'),
			'SERVER_NAME': '%s:%d' % (self.server.fqdn, self.server.naddr[1]),
			'SERVER_PORT': '%d' % self.server.naddr[1],
			'SERVER_PROTOCOL': self.request_version,
			'SERVER_SOFTWARE': self.server_version,
			
			# Following are not part of CGI 1.1:
			'DOCUMENT_ROOT': self.server.document_root,
			'REMOTE_PORT': '%d' % self.client_address[1],
			'REQUEST_URI': self.path,
			'SCRIPT_FILENAME': self.server.document_root + '/' + self.path.lstrip('/'),
			'SERVER_ADDR': self.server.naddr[0],
		}
		
		# read http headers and transfer to params
		for k in self.headers:
			v = self.headers.get(k)
			params['HTTP_'+k.replace('-','_').upper()] = v
			if k == 'content-length':
				content_length = int(v)
			elif k == 'content-type':
				params['CONTENT_TYPE'] = v
		if content_length:
			params['CONTENT_LENGTH'] = str(content_length)
		
		# begin
		role = fcgi.FCGI_RESPONDER
		flags = 0
		content = '%c%c%c\000\000\000\000\000' % ((role&0xFF00)>>8, role&0xFF, flags)
		ch.writePacket(fcgi.Record(fcgi.FCGI_BEGIN_REQUEST, rid, content))
		
		# params
		content = ''
		for k,v in params.items():
			s = fcgi.writeNameValue(k,v)
			if len(content)+len(s) > fcgi.FCGI_MAX_PACKET_LEN:
				ch.writePacket(fcgi.Record(fcgi.FCGI_PARAMS, rid, content))
				content = s
			else:
				content += s
		ch.writePacket(fcgi.Record(fcgi.FCGI_PARAMS, rid, content))
		ch.writePacket(fcgi.Record(fcgi.FCGI_PARAMS, rid))
		
		# EOF on stdin
		if content_length == 0:
			ch.writePacket(fcgi.Record(fcgi.FCGI_STDIN, rid, ''))
		
		# read reply
		started = False
		wrote_stdin_eof = content_length
		indata = ''
		outbuf = ''
		transfer_encoding = None
		skipout = False
		while 1:
			if content_length:
				try:
					r = ch.readPacket(True)
				except socket.error, e:
					if e.args[0] == 35: # "Resource temporarily unavailable"
						# probably waiting for stdin
						n = content_length
						if n > fcgi.FCGI_MAX_PACKET_LEN:
							n = fcgi.FCGI_MAX_PACKET_LEN
							content_length -= n
						else:
							content_length = 0
						
						indata = self.rfile.read(n)
						
						if not indata:
							log.warn('client sent EOF on stdin even though not all bytes indicated by '\
											 'content-length have been read -- aborting request')
							ch.writePacket(fcgi.Record(fcgi.FCGI_ABORT_REQUEST, rid))
							break
						
						log.info('got %d bytes on http stdin -- forwarding on FCGI channel', len(indata))
						
						ch.writePacket(fcgi.Record(fcgi.FCGI_STDIN, rid, indata))
						
						if content_length == 0:
							# write EOF
							ch.writePacket(fcgi.Record(fcgi.FCGI_STDIN, rid))
							wrote_stdin_eof = True
						
						continue
					else:
						raise
			else:
				r = ch.readPacket()
			log.debug('received packet %r', r)
			if r.type == fcgi.FCGI_STDOUT:
				if not started:
					outbuf += r.content
					r.content = ''
					p = outbuf.find('\r\n\r\n')
					if p != -1:
						sf = StringIO(outbuf[:p])
						r.content = outbuf[p+4:]
						headers = mimetools.Message(sf, True)
						
						# status
						status = headers.get('status', None)
						if status:
							status = status.split(' ',1)
							status[0] = int(status[0])
							self.send_response(*status)
						else:
							self.send_response(200)
						
						# required headers
						skipk = ['server', 'date', 'transfer-encoding']
						self.send_header('Server', headers.getheader('server', self.version_string()))
						self.send_header('Date', headers.getheader('date', self.date_time_string()))
						
						# content length
						if not headers.getheader('content-length', False):
							if self.protocol_version == 'HTTP/1.1':
								transfer_encoding = headers.getheader('server', 'chunked').lower()
								self.send_header('Transfer-Encoding', transfer_encoding)
							else:
								self.close_connection = 1
						
						# send other headers
						for k in headers:
							if k not in skipk:
								self.send_header(k.capitalize(), headers.getheader(k))
						
						self.wfile.write('\r\n')
						started = True
				if r.content and not skipout:
					self.wfile.write(r.content)
			elif r.type == fcgi.FCGI_STDERR:
				log.error('%s: %s', ch, r.content)
			elif r.type == fcgi.FCGI_END_REQUEST:
				if transfer_encoding == 'chunked':
					self.wfile.write('')
				break
		
		# EOF on stdin
		if not wrote_stdin_eof:
			ch.writePacket(fcgi.Record(fcgi.FCGI_STDIN, rid))
	

class Server(BaseHTTPServer.HTTPServer):
	fcgichannel = None
	document_root = '/tmp'
	
	def __init__(self, address, fcgi_address=('127.0.0.1', 5000), request_handler=RequestHandler, *va, **kw):
		self.document_root = os.path.realpath('.')
		self.fcgi_address = fcgi_address
		BaseHTTPServer.HTTPServer.__init__(self, address, request_handler)
	
	def server_bind(self):
		x = BaseHTTPServer.HTTPServer.server_bind(self)
		self.fqdn = socket.getfqdn(self.server_address[0])
		self.naddr = list(self.server_address)
		if self.naddr[0] == '0.0.0.0':
			self.naddr[0] = '127.0.0.1'
		elif self.naddr[0] == '::0':
			self.naddr[0] = '::1'
		self.naddr = tuple(self.naddr)
		return x
	
	def fcgi_connect(self, addr):
		channel = fcgi.Channel()
		channel.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		channel.sock.connect(addr)
		return channel
	
	def get_fcgi_backend(self, addr=None, max_connect_retries=10):
		if addr == None:
			addr = self.fcgi_address
		while True:
			try:
				return self.fcgi_connect(addr)
			except socket.error, e:
				if e.args[0] == 61:
					# connection refused
					if max_connect_retries == -1 or max_connect_retries > 0:
						try:
							log.warn('fcgi backend %s refused connection -- reconnecting...', addr)
							time.sleep(1)
							if max_connect_retries > 0:
								max_connect_retries -= 1
							continue
						except:
							pass
					log.error('fcgi backend %s refused connection', addr)
					break
				raise
	
	def put_fcgi_backend(self, ch):
		try:
			ch.sock.close()
		except:
			pass
	

if __name__ == '__main__':
	logging.basicConfig(level=logging.DEBUG)
	server = Server(('localhost', 8080))
	#server.handle_request()
	server.serve_forever()
