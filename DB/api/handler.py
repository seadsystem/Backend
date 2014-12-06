import http.server

import url_parser
import db

USAGE = "Usage: http://db.sead.systems:8080/(device id)?[[start_time=(start time as UTC unix timestamp)], [end_time=(end time as UTC unix timestamp)], [type=(Sensor type code)], [subset=(subsample result down to this many rows)], [limit=(truncate result to this many rows)], [json=(set to something to get the result in JSON format)]].join('&')"


class ApiHandler(http.server.SimpleHTTPRequestHandler):

	def __init__(self, req, client_addr,server):
		http.server.SimpleHTTPRequestHandler.__init__(self, req, client_addr, server)

	def do_GET(self):
		try:
			parsed = url_parser.parse(self.path)
		except Exception as inst:
			if self.path == '/':
				self.send_response(200)
				self.send_header("Content-type", "text/plain")
				self.end_headers()
				self.wfile.write(USAGE.encode("utf-8"))
				self.wfile.flush()
			else:
				print(type(inst))
				print(inst.args)
				print(inst)

				self.send_error(404)
			return

		try:
			r = db.query(parsed)

			self.send_response(200)
			self.send_header("Content-type", "application/json;charset=utf-8")  # Not actually using JSON format. Causes errors in Chrome when it tries to validate

			self.end_headers()
			for line in r:
				self.wfile.write(line.encode("utf-8"))
		except Exception as inst:
			self.send_error(500)
			print(type(inst))
			print(inst.args)
			print(inst)

			return

		self.wfile.flush()
