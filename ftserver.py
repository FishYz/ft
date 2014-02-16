#!/use/bin/env python

import BaseHTTPServer
impoer sys


class Handler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        self.wfile.write('Hello')

def RunServer(port):
    server = BaseHTTPServer.HTTPServer(('localhost', port), Handler)
    print 'Enter ctrl+c to stop server'
    BaseHTTPServer.test(SimpleHTTPRequestHandler, BaseHTTPServer.HTTPServer)

if __name__ == '__main__':
    RunServer(sys.argv[1])
