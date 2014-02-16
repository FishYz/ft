#!/use/bin/env python

import BaseHTTPServer
import sys


class Handler(BaseHTTPServer.BaseHTTPRequestHandler):
    dataPath = 'data/'

    def do_GET(self):
        self.wfile.write(self.dataPath)

def RunServer(port):
    server = BaseHTTPServer.HTTPServer(('', port), Handler)
    print 'Enter ctrl+c to stop server'
    server.serve_forever()

if __name__ == '__main__':
    RunServer(int(sys.argv[1]))
