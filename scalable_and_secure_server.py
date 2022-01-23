import mimetypes
import os
import posixpath
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from configparser import ConfigParser

# opening html files stored in htmlPages
import io

with open(r'htmlPages/Error_logs.html') as f:
    html_string_error = f.read()

# opening the listings of a directory
with open(r'htmlPages/Listing_page.html') as f:
    html_string_listing = f.read()

# variable
Error_Page = html_string_error


class case_no_file(object):
    '''File or directory does not exist.'''

    def test(self, handler):
        return not os.path.exists(handler.full_path)

    def act(self, handler):
        raise Exception("'{0}' not found".format(handler.path))


class case_existing_file(object):
    '''File exists.'''

    def test(self, handler):
        return os.path.isfile(handler.full_path)

    def act(self, handler):
        handler.handle_file(handler.full_path)


class case_always_fail(object):
    '''Base case if nothing else worked.'''

    def test(self, handler):
        return True

    def act(self, handler):
        handler.list_dir(handler.full_path)


class case_directory_index_file(object):
    '''Serve index.html page for a directory.'''

    def index_path(self, handler):
        return os.path.join(handler.full_path, 'index.html')

    def test(self, handler):
        return os.path.isdir(handler.full_path) and \
               os.path.isfile(self.index_path(handler))

    def act(self, handler):
        handler.handle_file(self.index_path(handler))


# html for listing the current directory listings
Listing_Page = html_string_listing
# getting the configurations data
server_configuration = ConfigParser()
server_configuration.read(r'configurations\configurations.ini')

# getting the sections from the config file
server_obj = server_configuration["server_info"]


class http_handler(BaseHTTPRequestHandler):
    Cases = [case_no_file(),
             case_existing_file(),
             case_directory_index_file(),
             case_always_fail()]

    # mimetypes
    extensions_map = {
        '.manifest': 'text/cache-manifest',
        '.html': 'text/html',
        '.png': 'image/png',
        '.jpg': 'image/jpg',
        '.svg': 'image/svg+xml',
        '.css': 'text/css',
        '.json': 'application / json',
        '.pdf': 'application/pdf',
        '.xml': 'application/xml',
        '.js': 'application/x-javascript',
        '': 'application/octet-stream',  # Default
    }

    # overridden function provided by the BaseHTTPRequestHandler
    def do_GET(self):
        try:
            # Figure out what exactly is being requested.
            global msg

            self.full_path = os.getcwd() + self.path

            # Figure out how to handle it.
            for case in self.Cases:
                handler = case
                if handler.test(self):
                    handler.act(self)
                    break

        # Handle errors.
        except Exception as msg:
            self.handle_error(msg)

    def handle_file(self, full_path):
        try:
            # check the path file extension to hand files differently
            extension = full_path.split(".")[1]
            if extension != "png":
                with open(full_path, 'r') as reader:
                    content = reader.read()
                    self.send_content(content)
            else:
                with open(full_path, 'rb') as reader:
                    content = reader.read()
                    self.send_content(content)
        except IOError as msg:
            msg = "'{0}' cannot be read: {1}".format(self.path, msg)
            self.handle_error(msg)

        # Handle unknown objects.

    def handle_error(self, msg):

        content = Error_Page.format(path=self.path, msg=msg)
        self.send_content(content, 404)

    def list_dir(self, full_path):
        try:
            # listing everything in that directory
            entries = os.listdir(full_path)

            # links added to the listings but faulty
            bullets = ['<li> <a href="{0}">{0}</a></li>'.format(e) for e in entries if not e.startswith('.')]

            page = Listing_Page.format('\n'.join(bullets))

            # sending the contents
            self.send_content(page)
        except OSError as msg:
            msg = "'{0}' cannot be listed: {1}".format(self.path, msg)
            self.handle_error(msg)

        # this will check what mime is asked for by the client. and return the mime type

    def get_mimetype(self, content):
        base, ext = posixpath.splitext(self.path)
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        ext = ext.lower()
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        guess, _ = mimetypes.guess_type(self.path)
        if guess:
            return guess
        return 'application/octet-stream'

    # serving different types of contents
    def send_content(self, content, status=200):
        mime_type = self.get_mimetype(content)
        self.send_response(status)
        self.send_header("Content-type", mime_type[1])
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        if isinstance(content, str):
            self.wfile.write(content.encode(encoding="UTF-8"))
        else:
            self.wfile.write(content)

    # this will be for logging and it is overridden
    def log_message(self, format, *args):
        # This will print in the terminal
        print("host : {} | port : {} | http request :{}, status :{}".format(self.client_address[0],
                                                                            self.client_address[1],
                                                                            args[0],
                                                                            args[1]
                                                                            ))


if __name__ == '__main__':
    with HTTPServer(('', int(server_obj['port'])), http_handler) as server:
        # the server will serve the clients until they have to close the connection
        server.serve_forever()
