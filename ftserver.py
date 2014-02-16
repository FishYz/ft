#!/use/bin/env python

from SimpleHTTPServer import HTTPServer

def run_server():
    server = HTTPServer()
    print 'Enter ctrl+c to stop server'
    server.serve_forever()

if __name__ == '__main__':
    run_server()
