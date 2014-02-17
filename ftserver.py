#!/use/bin/env python

import BaseHTTPServer
import sys
import os


class Handler(BaseHTTPServer.BaseHTTPRequestHandler):


    """Serve the GET request"""
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(self.path)


    """Serve the HEAD request"""
    def do_HEAD(self):
        pass


    """Send response code and handler"""
    def send_head(self):
        path = self.translate_path(self.path)
        return self.show_page(path)


    """Translate the /-separated path to the local filename """
    def translate_path(self, path):
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]
        path = posixpath.normpath(urllib.unquote(path))
        words = path.split('/')
        words = filter(None, words)
        path = os.getcwd()
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir): continue
            path = os.path.join(path, word)
        return path


    """Use to list files and show the upload form"""
    def show_page(self, path):
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
