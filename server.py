#!/usr/bin/env python


from BaseHTTPServer import BaseHTTPRequestHandler

class GetHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.wfile.write("hi")



if __name__ == '__main__':
    from BaseHTTPServer import HTTPServer
    sever = HTTPServer(('localhost',8080),GetHandler)
    print 'Starting server, use <Ctrl-C> to stop'
    sever.serve_forever()
