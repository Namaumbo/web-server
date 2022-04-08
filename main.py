#!/usr/bin/env python
import configparser
import io
import logging
import mimetypes
import os
import posixpath
import shutil
import sys
import urllib.parse
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
# from scripts.logsHandlers.LogsClass import Logs
from scripts.MultipleRequestHandler import MultipleRequestsHandler

# THE START OF THE SERVER

html_string_error = """
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Error response</title>

</head>
<body>
   <h2
        style="background-color:tomato;
        font-family:Sans-serif;
        text-align:center;
        font-size:30px;
        color:white">
         Error Response log 
   </h2>
        <hr />
        <br />
       <h1>Error accessing {path}</h1>
       <p>{message}</p>
</body>
"""
html_string_listing = """

<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>root index</title>

</head>
<body>
<h2
        style="
        background-color :lightgreen;
        padding-left : 30px;
        color:black;
        font-family:Sans-serif;
        text-align:center;
        font-size:25px

";

>Here are the resources </h2>
<h2><b>for the listing of {path}</b></h2>
<hr/>
<br/>
<ul>
  {0}
</ul>
</body>
 """
# html for error listing
Error_Page = html_string_error
# html for listing the current directory listings
Listing_Page = html_string_listing
# reading the configuration file from the operating system
config = configparser.ConfigParser()
<<<<<<< HEAD
config.read('/etc/myConfigfiles/myServer.ini')
=======
config.read('/etc/myConfigFiles/configuration.ini')
>>>>>>> 274c70f6898fd671fcd8165c0a574b981a68afbd
PORT = config.get('Server_info', 'PORT')
IP = config.get('Server_info', 'IP')

DIRECTORIES = config.get('dir', 'DIRECTORIES')

# # edulab details
# edulab_directory = config.get('edulabWebsite', 'DocumentRoot')
# edulab_app_name = config.get('edulabWebsite', 'ServerName')
# edulab_app_name_alias = config.get('edulabWebsite', 'aliasServerName')

# # hangover details
# hangover_directory = config.get('hangoverWebsite', 'DocumentRoot')
# hangover_app_name = config.get('hangoverWebsite', 'ServerName')
# hangover_app_name_alias = config.get('hangoverWebsite', 'aliasServerName')

DEFAULT_ERROR_MESSAGE = """\
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
        "http://www.w3.org/TR/html4/strict.dtd">
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
        <title>Error response</title>
    </head>
    <body>
        <h1>Error response</h1>
        <p>Error code: %(code)d</p>
        <p>Message: %(message)s.</p>
        <p>Error code explanation: %(code)s - %(explain)s.</p>
    </body>
</html>
"""


class main(BaseHTTPRequestHandler):
    extensions_map = {
        '.manifest': 'text/cache-manifest',
        '.html': 'text/html',
        '.txt': 'text/txt',
        '.png': 'image/png',
        '.jpg': 'image/jpg',
        '.svg': 'image/svg+xml',
        '.css': 'text/css',
        '.mp4': 'video/mpeg',
        '.php': 'application/x-httpd-php',
        '.py': 'text/x-python-code',
        '.json': 'application/json',
        '.pdf': 'application/pdf',
        '.mp3': 'application/x-mplayer2',
        '.xml': 'application/xml',
        '.js': 'application/x-javascript',
        '': 'application/octet-stream',  # Default
    }
    protocol_version = "HTTP/1.1"

    def __init__(self, *args, directory=None, **kwargs):

        super().__init__(*args, **kwargs)
        self.full_path = None

    def do_GET(self):
        # this function will serve the simple get request
        f = self.send_head()
        if f:
            try:
                self.copyfile(f, self.wfile)
            finally:
                f.close()

    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
        post_data = self.rfile.read(content_length)  # <--- Gets the data itself
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                     str(self.path), str(self.headers), post_data.decode('utf-8'))
        self._set_response()
        self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))

    def send_head(self):
<<<<<<< HEAD
        # self.full_path = self.translate_path(self.path)
        # global final_path
        if self.headers["Host"].split(":")[0] in [edulab_app_name.strip(), edulab_app_name_alias.strip()]:
            self.full_path = edulab_directory + self.path
        elif self.headers["Host"].split(":")[0] in [hangover_app_name.strip(), hangover_app_name_alias.strip()]:
            self.full_path = hangover_directory + self.path
        else:
            self.full_path = DIRECTORIES + self.path
            full_path = self.full_path.split("%20")
            self.full_path = " ".join(full_path)

=======
        # # path = self.translate_path(self.path)
        # # global final_path
        # if self.headers["Host"].split(":")[0] in [edulab_app_name.strip(), edulab_app_name_alias.strip()]:
        #     self.full_path = edulab_directory + self.path
        # elif self.headers["Host"].split(":")[0] in [hangover_app_name.strip(), hangover_app_name_alias.strip()]:
        #     print(hangover_directory)
        #     self.full_path = hangover_directory+ self.path
        # else:
        self.full_path = self.path
        # if not self.path.endswith('/'):
        #     self.send_response(HTTPStatus.MOVED_PERMANENTLY)
        #     self.send_header('Location', self.path + "/")
        #     self.end_headers()
        #     return None
>>>>>>> 274c70f6898fd671fcd8165c0a574b981a68afbd

        if os.path.isdir(self.full_path):
            for index in "index.html", "index.htm":
                index = os.path.join(self.full_path, index)
                if os.path.exists(index):
                    self.full_path = index
                    break


            else:
                return self.list_directory(self.full_path)
        mime_type = self.guess_type(self.full_path)
        if self.full_path.endswith("/"):
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return None
        try:
            f = open(self.full_path, 'rb')
        except OSError:
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return None
        try:
            fs = os.fstat(f.fileno())
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-type", mime_type)
            self.send_header("Content-Length", str(fs[6]))
            self.end_headers()
            return f
        except:
            f.close()
            raise

    def list_directory(self, full_path):
        try:

            entries = os.listdir(full_path)

            display_path = urllib.parse.unquote(self.path, errors='surrogates')
            enc = sys.getfilesystemencoding()

            if not self.path.endswith('/'):
                self.send_response(HTTPStatus.MOVED_PERMANENTLY)
                self.send_header('Location', self.path + "/")
                self.end_headers()
                return None

            bullets = ['<li><a href="{0}">{0}</a></li>'.format(e) \
                       for e in entries if not e.startswith('.')]
            page = Listing_Page.format('\n'.join(bullets), path=display_path)
            f = io.BytesIO()
            f.write(page.encode(encoding="utf-8"), )
            f.seek(0)
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-type", "text/html; charset=%s" % enc)
            self.send_header("Content-Length", str(len(page)))
            self.end_headers()
            return f
        except OSError:
            self.send_error(
                HTTPStatus.NOT_FOUND,
                "No permission to list directory")
            return None

    def translate_path(self, path):
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]

        trailing_slash = path.rstrip().endswith('/')
        try:
            path = urllib.parse.unquote(path)
        except UnicodeDecodeError as message:
            self.send_content(message, 404)

        path = posixpath.normpath(path)
        words = path.split('/')

        path = self.directory
        for word in words:
            if os.path.dirname(word) or word in (os.curdir, os.pardir):
                continue
            path = os.path.join(path, word)
        if trailing_slash:
            path += '/'
        return path

    # def log_message(self, format: str, *args):
    #     Logs.access_log(self, *args)
    #     Logs.server_log(self, *args)

    def copyfile(self, source, out_put_file):
        shutil.copyfileobj(source, out_put_file)

    def guess_type(self, path):

        base, ext = posixpath.splitext(path)
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        ext = ext.lower()
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        guess, _ = mimetypes.guess_type(path)
        if guess:
            return guess
        return 'application/octet-stream'

    def send_content(self, content, status=200):
        mime_type = self.guess_type(content)
        self.send_response(status)
        self.send_header("Location", self.path)
        self.send_header('Content-type', mime_type[1])
        # self.send_header("Content-Length", str(len(content)))
        self.send_header("User-Agent", str(self.headers))


if __name__ == '__main__':
    global ip_address
    if IP is None:
        ip_address = ""
    else:
        ip_address = IP
    with MultipleRequestsHandler((str(ip_address), int(PORT)), main) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nKeyboard interrupt received, exiting.")
            sys.exit(0)