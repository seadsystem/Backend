import sys
import os
# add Backend directory to python path so we can do
# cross directory imports
path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(path[:-7])

import socketserver
import DB.api.handler as handler
PORT = 8081


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """ Handle requests in a separate thread """


Handler = handler.ApiHandler

httpd = ThreadedTCPServer(("", PORT), Handler)

print("serving at port", PORT)
httpd.serve_forever()

