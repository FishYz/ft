#!/use/bin/env python

import BaseHTTPServer
import sys
import os
import cgi
import urllib
import shutil
import posixpath
import mimetypes
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


class Handler(BaseHTTPServer.BaseHTTPRequestHandler):


    """Serve the GET request"""
    def do_GET(self):
        f = self.send_head()
        if f:
            shutil.copyfileobj(f, self.wfile)
            f.close()


    """Serve the HEAD request"""
    def do_HEAD(self):
        f = self.send_head()
        if f:
            f.close()


    """Send response code and handler"""
    def send_head(self):
        path = self.translate_path(self.path)
        f = None
        if os.path.isdir(path):
            if not self.path.endswith('/'):
                # redirect browser - doing basically what apache does
                self.send_response(301)
                self.send_header("Location", self.path + "/")
                self.end_headers()
                return None
            else:
                return self.show_page(path)
        ctype = self.guess_type(path)
        try:
            # Always read in binary mode. Opening files in text mode may cause
            # newline translations, making the actual size of the content
            # transmitted *less* than the content-length!
            f = open(path, 'rb')
        except IOError:
            self.send_error(404, "File not found")
            return None
        self.send_response(200)
        self.send_header("Content-type", ctype)
        fs = os.fstat(f.fileno())
        self.send_header("Content-Length", str(fs[6]))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        return f


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


    """A method used to copy the contents from source to outputfile"""
    def copyfile(self, source, outputfile):
        shutil.copyfileobj(source, outputfile)

    def guess_type(self, path):
        """Guess the type of a file.

        Argument is a PATH (a filename).

        Return value is a string of the form type/subtype,
        usable for a MIME Content-type header.

        The default implementation looks the file's extension
        up in the table self.extensions_map, using application/octet-stream
        as a default; however it would be permissible (if
        slow) to look inside the data to make a better guess.

        """

        base, ext = posixpath.splitext(path)
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        ext = ext.lower()
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        else:
            return self.extensions_map['']


    if not mimetypes.inited:
        mimetypes.init() # try to read system mime.types
    extensions_map = mimetypes.types_map.copy()
    extensions_map.update({
        '': 'application/octet-stream', # Default
        '.py': 'text/plain',
        '.c': 'text/plain',
        '.h': 'text/plain',
        })

def RunServer(port):
    fileName = os.path.abspath(sys.argv[0])
    filePath = os.path.dirname(fileName)
    os.chdir(filePath + '/data')
    server = BaseHTTPServer.HTTPServer(('', port), Handler)
    print "Enter ctrl+c to stop server"
    server.serve_forever()


if __name__ == "__main__":
    RunServer(int(sys.argv[1]))
