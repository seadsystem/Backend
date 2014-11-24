#!/usr/bin/env python3

import http.server
import socketserver

import handler

PORT = 8080

Handler = handler.ApiHandler

socketserver.ThreadingTCPServer.allow_reuse_address = True
httpd = socketserver.TCPServer(("", PORT), Handler)

print("serving at port", PORT)
httpd.serve_forever()

