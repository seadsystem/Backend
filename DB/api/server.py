import socketserver
import DB.api.handler as handler
PORT = 8081


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """ Handle requests in a separate thread """


Handler = handler.ApiHandler

httpd = ThreadedTCPServer(("", PORT), Handler)

print("serving at port", PORT)
httpd.serve_forever()

