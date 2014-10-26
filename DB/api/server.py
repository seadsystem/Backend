#!/usr/bin/env python3
# Python 3

import http.server
import socketserver

import handler

PORT = 8080

Handler = handler.ApiHandler

httpd = socketserver.TCPServer(("", PORT), Handler)

print("serving at port", PORT)
httpd.serve_forever()

