# Python 3

import http.server

import url_parser
import db

class ApiHandler(http.server.SimpleHTTPRequestHandler):

	def __init__(self, req, client_addr,server):
		http.server.SimpleHTTPRequestHandler.__init__(self, req, client_addr, server)

	def do_GET(self):
		try:
			parsed = url_parser.parse(self.path)
		except:
			self.send_error(404)
			return

		try:
			r = db.query(parsed)
		except:
			self.send_error(500)
			return

		self.send_response(200)
		self.send_header("Content-type", "application/json;charset=utf-8")

#		self.send_header("Content-length", len(r))
		self.end_headers()
		self.wfile.write('[\n'.encode("utf-8"))
		for line in r:
			self.wfile.write(line.encode("utf-8"))
		self.wfile.write(']\n'.encode("utf-8"))
		self.wfile.flush()
