#!/use/bin/env python

import BaseHTTPServer
import sys
import os
import cgi
import urllib
import shutil
import posixpath
import mimetypes
import re
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

    def do_POST(self):
        """Serve a POST request."""
        r, info = self.deal_post_data()
        print r, info, "by: ", self.client_address
        f = StringIO()
        f.write('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
        f.write("<html>\n<title>Upload Result Page</title>\n")
        f.write("<body>\n<h2>Upload Result Page</h2>\n")
        f.write("<hr>\n")
        if r:
            f.write("<strong>Success:</strong>")
        else:
            f.write("<strong>Failed:</strong>")
        f.write(info)
        f.write("<br><a href=\"%s\">back</a>" % self.headers['referer'])
        f.write("</body>\n</html>\n")
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        if f:
            self.copyfile(f, self.wfile)
            f.close()
        
    def deal_post_data(self):
        boundary = self.headers.plisttext.split("=")[1]
        remainbytes = int(self.headers['content-length'])
        line = self.rfile.readline()
        remainbytes -= len(line)
        if not boundary in line:
            return (False, "Content NOT begin with boundary")
        line = self.rfile.readline()
        remainbytes -= len(line)
        fn = re.findall(r'Content-Disposition.*name="file"; filename="(.*)"', line)
        if not fn:
            return (False, "Can't find out file name...")
        path = self.translate_path(self.path)
        fn = os.path.join(path, fn[0])
        while os.path.exists(fn):
            fn += "_"
        line = self.rfile.readline()
        remainbytes -= len(line)
        line = self.rfile.readline()
        remainbytes -= len(line)
        try:
            out = open(fn, 'wb')
        except IOError:
            return (False, "Can't create file to write, do you have permission to write?")
                
        preline = self.rfile.readline()
        remainbytes -= len(preline)
        while remainbytes > 0:
            line = self.rfile.readline()
            remainbytes -= len(line)
            if boundary in line:
                preline = preline[0:-1]
                if preline.endswith('\r'):
                    preline = preline[0:-1]
                out.write(preline)
                out.close()
                return (True, "File '%s' upload success!" % fn)
            else:
                out.write(preline)
                preline = line
        return (False, "Unexpect Ends of data.")

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
        f.write('<html>\n<head>\n<title>Directory listing for %s</title>\n' % displaypath)
        f.write("""<style>
		#section{font-family: "Georgia", "Microsoft YaHei", "FangSong";}
        .container{display:inline-block;min-height:200px;min-width:360px;color:#f30;padding:30px;border:3px solid #ddd;-moz-border-radius:10px;-webkit-border-radius:10px;border-radius:10px;}
		.preview{max-width:360px;}
		#files-list{position:absolute;top:0;left:500px;}
		#list{width:460px;}
		#list .preview{max-width:250px;}
		#list p{color:#888;font-size:12px;}
		#list .green{color:#09c;}
    </style>""")
    	f.write('</head>')    		
        f.write('<body>\n<h2>Directory listing for %s</h2>\n' % displaypath)
        f.write("""<div id="section">
        <p>Please put your file in container: </p>
        <div id="container" class="container">
            
        </div>
		<div id ="files-list">
			<p>the draged files:</p>
			<ul id="list"></ul>
		</div>
    </div>""")
        f.write('<form method="post"')
        f.write('enctype="multipart/form-data">')
        f.write('<label for="file">Filename:</label>')
        f.write('<input type="file" name="file" id="file" />')
        f.write('<br />')
        f.write('<input type="submit" name="submit" value="Submit" />')
        f.write('</form>')
        f.write('<hr>\n<ul>\n')
        f.write("""<script>
	var progressBarZone = document.getElementById('container');

function sendFile(files) {
       if (!files || files.length < 1) {
             return;
      }
      
       var percent = document.createElement('div' );
      progressBarZone.appendChild(percent);
      
       var fileNames = '' ;
       
       var formData = new FormData();             // new a FormData      
       for ( var i = 0; i < files.length; i++) {
             var file = files[i];    // file has name, size attribute
            
            formData.append( 'file' , file);       // append files object in the formData
            
            fileNames += '<' + file.name + '>, ' ;
      }
      
       var xhr = new XMLHttpRequest();
      xhr.upload.addEventListener( 'progress',
             function uploadProgress(evt) {
                   // evt has three attribute:
                   // lengthComputable - Calculatethenumber of bytes uploaded
                   // total -The total number of bytes
                   // loaded -The number of bytes uploaded so far
                   if (evt.lengthComputable) {
                        percent.innerHTML = fileNames + ' upload percent :' + Math.round((evt.loaded / evt.total)  * 100) + '%' ;
                  }
            }, false); 

      xhr.upload.onload = function() {
            percent.innerHTML = fileNames + 'Upload complete.' ;
      };

      xhr.upload.onerror = function(e) {
            percent.innerHTML = fileNames + ' Upload fail.' ;
      };

      formData.append( 'submit', 'Submit' );  
      xhr.open( 'post', '/' , true);
      xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
      xhr.send(formData);            // send formData object.
}

	if (window.FileReader) {

		var list = document.getElementById('list'),
			cnt = document.getElementById('container');



		// handle drag list
		function handleFileSelect(evt) {
			evt.stopPropagation();
			evt.preventDefault();

			var files = evt.dataTransfer.files;
				sendFile(files)
			for (var i = 0, f; f = files[i]; i++) {

				var t = f.type ? f.type : 'n/a',
					reader = new FileReader(),
					looks = function (f) {
						list.innerHTML += '<li><strong>' + f.name + '</strong> (' + t +
							') - ' + f.size+ ' bytes' + '</li>';
						
					};

				// handle the file
				if (true) {
					reader.onload = (function (theFile) {
						return function (e) {
							
							looks(theFile);
						};
					})(f)
					reader.readAsDataURL(f);
				} 

			}

		}
		
		// Handle Drag  insert effects
		function handleDragEnter(evt){ this.setAttribute('style', 'border-style:dashed;'); }
		function handleDragLeave(evt){ this.setAttribute('style', ''); }

		// Processing file into an event,  prevent default browser redirect
		function handleDragOver(evt) {
			evt.stopPropagation();
			evt.preventDefault();
		}
		
		cnt.addEventListener('dragenter', handleDragEnter, false);
		cnt.addEventListener('dragover', handleDragOver, false);
		cnt.addEventListener('drop', handleFileSelect, false);
		cnt.addEventListener('dragleave', handleDragLeave, false);
		
	} 
	
	else {
		document.getElementById('section').innerHTML = 'Sorry,Your browser does not support!';
	}
	
	</script>""")
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