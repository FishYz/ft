#!/use/bin/env python

import BaseHTTPServer
import sys
import os


class Handler(BaseHTTPServer.BaseHTTPRequestHandler):
    """Send response code and handler"""
    def send_head(self):
        pass


    """Translate the /-separated path to the local filename """
    def translate_path(self, path):
        pass


    """Serve the GET request"""
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write("123")


    """Serve the HEAD request"""
    def do_HEAD(self):
        pass

def RunServer(port):
    fileName = os.path.abspath(sys.argv[0])
    filePath = os.path.dirname(fileName)
    os.chdir(filePath + '/data')
    server = BaseHTTPServer.HTTPServer(('', port), Handler)
    print "Enter ctrl+c to stop server"
    server.serve_forever()


if __name__ == "__main__":
    RunServer(int(sys.argv[1]))
