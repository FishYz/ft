#!/use/bin/env python

import BaseHTTPServer
import sys
import os
import cgi
import urllib
import shutil
import posixpath
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


class Handler(BaseHTTPServer.BaseHTTPRequestHandler):


    """Serve the GET request"""
    def do_GET(self):
        path = self.translate_path(self.path)
        f = self.show_page(path)
        if f:
            shutil.copyfileobj(f, self.wfile)
            f.close()


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
            if word in (os.curdir, os.pardir):
                continue
            path = os.path.join(path, word)
        return path


    """Use to list files and show the upload form"""
    def show_page(self, path):
        try:
            list = os.listdir(path)
        except os.error:
            self.send_error(404, "No permission to list directory")
            return None
        list.sort(key=lambda a: a.lower())
        f = StringIO()
        displaypath = cgi.escape(urllib.unquote(self.path))
        f.write('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
        f.write('<html>\n<title>Directory listing for %s</title>\n' % displaypath)
        f.write('<body>\n<h2>Directory listing for %s</h2>\n' % displaypath)
        f.write('<form method="post"')
        f.write('enctype="multipart/form-data">')
        f.write('<label for="file">Filename:</label>')
        f.write('<input type="file" name="file" id="file" />')
        f.write('<br />')
        f.write('<input type="submit" name="submit" value="Submit" />')
        f.write('</form>')
        f.write('<hr>\n<ul>\n')
        for name in list:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
            if os.path.islink(fullname):
                displayname = name + "@"
                # Note: a link to a directory displays with @ and links with /
            f.write('<li><a href="%s">%s</a>\n'
                    % (urllib.quote(linkname), cgi.escape(displayname)))
        f.write("</ul>\n<hr>\n</body>\n</html>\n")
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        encoding = sys.getfilesystemencoding()
        self.send_header("Content-type", "text/html; charset=%s" % encoding)
        self.send_header("Content-Length", str(length))
        self.end_headers()
        return f


def RunServer(port):
    fileName = os.path.abspath(sys.argv[0])
    filePath = os.path.dirname(fileName)
    os.chdir(filePath + '/data')
    server = BaseHTTPServer.HTTPServer(('', port), Handler)
    print "Enter ctrl+c to stop server"
    server.serve_forever()


if __name__ == "__main__":
    RunServer(int(sys.argv[1]))
