#!/usr/bin/env python
import configparser
import mimetypes
import os
import posixpath
import urllib
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from scripts.MultipleRequestHandler import MultipleRequestsHandler
# from scripts.BaseHTTPRequestHandler import BaseRequestsHandler


# configTree = ET.parse("configurations/config.xml")

# try:
# check this code
#  arguments, values = getopt.getopt(argumentList, short_options, long_options)
# for currentArgument, currentValue in arguments:
#   if currentArgument in ("-b", "--bind"):
#       # from here <ip/> in XML will be overridden
# root_element = configTree.getroot()
#  for element in root_element.findall("ip"):
#    element.text = currentValue
#  configTree.write(r"./configurations/config.xml", encoding='UTF-8', xml_declaration=True)


# THE START OF THE SERVER
from scripts.fileHandlers.FileHandlerCases import case_no_file, case_existing_file, case_directory_index_file, \
    case_always_fail
from scripts.logsHandlers.LogsClass import Logs

html_string_error = """"
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Error logs</title>

</head>
<body>
   <h2
        style="color:black;
        font-family:Sans-serif;
        text-align:center;
        font-size:35px;
        color:red
        "
        > Error Response log </h2>
        <hr />
        <br />
       <h1>Error accessing {path}</h1>
       <p>{message}</p>
</body>"""
html_string_listing = """

<body>
<h2
        style="
        background-color : skyblue;
        padding-left : 30px;
        color:black;
        font-family:Sans-serif;
        text-align:center;
        font-size:25px

";

>Here are the resources </h2>
<h1> <b>for the listing of {path}  </b></h1>
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
config.read('/etc/myConfigfiles/myServer.ini')
PORT = config.get('Server_info', 'PORT')
IP = config.get('Server_info', 'IP')


class Main(BaseHTTPRequestHandler):
    Cases = [case_no_file(),
             case_existing_file(),
             case_directory_index_file(),
             case_always_fail()]
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

    # overridden function provided by the BaseHTTPRequestHandle
    def do_GET(self):
        try:
            # Figure out what exactly is being requested.
            # removing the white spaces
            self.full_path = os.getcwd() + self.path
            # self.full_path = directory_obj["directory_served"] + self.path
            # split the path by the spaces given as %20 by default
            full_path = self.full_path.split("%20")
            # then join the list of path parts by space
            self.full_path = " ".join(full_path)
            # Figure out how to handle it.s
            for case in self.Cases:
                handler = case
                if handler.test(self):
                    handler.act(self)
                    break
        # Handle errors.
        except Exception as message:
            self.handle_error(message)

    # getting the mime type
    def get_mimetype(self, content):
        base, ext = posixpath.splitext(self.path)
        if ext in self.extensions_map:
            # return extension
            return self.extensions_map[ext]
        # lowercase extensions
        ext = ext.lower()
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        guess, _ = mimetypes.guess_type(self.path)
        if guess:
            return guess
        return 'application/octet-stream'

    # handling error
    def handle_error(self, error_message):
        content = Error_Page.format(path=self.path, message=error_message)
        self.send_content(content, 404)

    # listing all directories
    def list_dir(self, full_path):
        try:
            # listing everything in that directory
            entries = os.listdir(full_path)
            # parsing the url
            display_path = urllib.parse.unquote(self.path, errors='surrogates')
            # this will append the url with / for it not to redirect
            if not self.path.endswith('/'):
                # status  A browser redirects to the new URL and search
                # engines update their links to the resource
                self.send_response(HTTPStatus.MOVED_PERMANENTLY)
                # then the header will Notify the location
                self.send_header("Location", self.path + "/")
                self.end_headers()
                return None
            bullets = ['<li> <a href="{0}">{0}</a></li>'.format(e) for e in entries if
                       not e.startswith('.')]
            # appending the listings to the listing html page
            page = Listing_Page.format('\n'.join(bullets), path=display_path)
            # sending the contents
            self.send_content(page)
        except OSError as error_message:
            error_message = "'{0}' cannot be listed: {1}".format(self.path, error_message)
            self.handle_error(error_message)

    # this will check what mime is asked for by the client. and return the mime type
    def handle_file(self, full_path):
        try:
            # check the path file extension to hand files differently
            extension = full_path.split(".")[1]
            if extension == "pdf":
                pdf_file = open(full_path, 'rb')
                st = os.fstat(pdf_file.fileno())
                length = st.st_size
                data = pdf_file.read()
                self.send_response(HTTPStatus.OK)
                self.send_header('Content-type', 'application/pdf')
                self.send_header('Content-length', str(length))
                self.send_header('Keep-Alive', 'timeout=5 ,max=100')
                self.send_header('Accept-Ranges', 'bytes')
                self.end_headers()
                self.wfile.write(data)
                pdf_file.close()
            else:
                try:
                    # using manual opening and reading until all the bytes are read
                    file = open(full_path, 'rb')
                    mime_type = self.get_mimetype(file)
                    st = os.fstat(file.fileno())
                    length = st.st_size
                    data = file.read()
                    self.send_response(HTTPStatus.OK)
                    self.send_header('Content-type', mime_type[1])
                    self.send_header('Content-Length', str(length))
                    self.send_header('Keep-Alive', 'timeout=5, max=100')
                    self.send_header('Accept-Ranges', 'bytes')
                    self.end_headers()
                    self.wfile.write(data)
                    file.close()
                except IOError:
                    self.log_error('File Not Found: %s' % self.path, 404)
        except IOError as io_error:
            msg = "'{0}' cannot be read: {1}".format(self.path, io_error)
            self.handle_error(io_error)

    # serving different types of contents
    def send_content(self, content, status=200):
        mime_type = self.get_mimetype(content)
        self.send_response(status)
        self.send_header("Location", self.full_path)
        self.send_header("Content-type", mime_type[1])
        self.send_header("Content-Length", str(len(content)))
        self.send_header("User-Agent", str(self.headers))
        self.end_headers()
        if isinstance(content, str):
            self.wfile.write(content.encode(encoding="utf-8"))
        else:
            self.wfile.write(content)

    # messages logs
    def log_message(self, format: str, *args):
        Logs.access_log(self, *args)
        Logs.server_log(self, *args)


if __name__ == '__main__':
    global ip_address
    if IP is None:
        ip_address = ""
    else:
        ip_address = IP
    with MultipleRequestsHandler((str(ip_address), int(PORT)), Main) as httpd:
        httpd.serve_forever()
