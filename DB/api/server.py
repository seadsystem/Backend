#!/usr/bin/env python3

import http.server
import socketserver
import threading
import handler

PORT = 8080


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """ Handle requests in a separate thread """


Handler = handler.ApiHandler

httpd = ThreadedTCPServer(("", PORT), Handler)

print("serving at port", PORT)
httpd.serve_forever()
