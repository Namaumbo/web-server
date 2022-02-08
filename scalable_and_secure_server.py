import mimetypes
import os
import posixpath
import socket
import urllib
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from configparser import ConfigParser
from socketserver import ThreadingMixIn

# opening html files stored in htmlPages

with open(r'htmlPages/Error_logs.html') as f:
    html_string_error = f.read()

# # opening the listings of a directory
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
server_configuration.read('./configurations/configurations.ini')

# getting the sections from the config file
server_obj = server_configuration["server_info"]

directory_obj = server_configuration["directories"]


# setting the ipaddress
def getting_interface_ip():
    interface_ip = socket.gethostbyname(socket.gethostname())
    server_configuration.set("server_info", "host_ip", interface_ip)


def access_log(self, *args, ):
    # ip address - authentication - [date and time]
    # "request from the client"[HTTP
    # action, status, size_in_bytes
    # identifier of the web browser]

    f = open("Logs/access.log", "a")
    f.write('{} - -[{}] - - "{}" - - {} - - {} \n'.format(self.client_address[0], self.date_time_string().split(",")[1],

                                                          args[1], args[2], self.headers["User-Agent"]))
    f.close()


# THE START OF THE SERVER
class http_handler(BaseHTTPRequestHandler):
    Cases = [case_no_file(),
             case_existing_file(),
             case_directory_index_file(),
             case_always_fail()]

    # mimetypes
    extensions_map = {
        '.manifest': 'text/cache-manifest',
        '.html': 'text/html',
        '.txt': 'text/txt',
        '.png': 'image/png',
        '.jpg': 'image/jpg',
        '.svg': 'image/svg+xml',
        '.css': 'text/css',
        '.json': 'application / json',
        '.pdf': 'application/pdf',
        '.mp3': 'application/x-mplayer2',
        '.xml': 'application/xml',
        '.js': 'application/x-javascript',
        '': 'application/octet-stream',  # Default
    }

    # overridden function provided by the BaseHTTPRequestHandler
    def do_GET(self):

        # cheking the ip

        try:
            # Figure out what exactly is being requested.
            global msg

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
        except Exception as msg:
            self.handle_error(msg)

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

    def handle_file(self, full_path):
        try:

            # check the path file extension to hand files differently
            extension = full_path.split(".")[1]

            if extension not in ["png", "jpg", "pdf", "txt", "mp3"]:
                with open(full_path, 'r') as reader:
                    content = reader.read()
                    self.send_content(content)

                # serving pdf files
            else:
                try:

                    # using manual opening and reading until all the bytes are read
                    file = open(full_path, 'rb')
                    st = os.fstat(file.fileno())
                    length = st.st_size
                    data = file.read()
                    mime_type = self.get_mimetype(file)
                    self.send_response(200)
                    self.send_header('Content-type', mime_type[1])
                    self.send_header('Content-Length', str(length))
                    self.send_header('Keep-Alive', 'timeout=5, max=100')
                    self.send_header('Accept-Ranges', 'bytes')
                    self.end_headers()
                    self.wfile.write(data)
                    file.close()


                except IOError:
                    self.log_error('File Not Found: %s' % self.path, 404)
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
        except OSError as msg:
            msg = "'{0}' cannot be listed: {1}".format(self.path, msg)
            self.handle_error(msg)

        # this will check what mime is asked for by the client. and return the mime type

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

    # this will be for logging and it is overridden from the baseHTTPhandler
    def log_message(self, format, *args):
        # This will print in the terminal
        # access_log(self, request, *args)
        print("client : {} | port : {} | http request :{}, status :{}".format(self.client_address[0],
                                                                              self.client_address[1],
                                                                              args[0],
                                                                              args[1]))


# this class will allow multiple clients to be served at once

# class MultipleRequestsHandler(HTTPServer):
#     """Mix-in class to handle each request in a new thread."""
#
#     # Decides how threads will act upon termination of the
#     # main process
#     daemon_threads = False
#     # If true, server_close() waits until all non-daemonic threads terminate.
#     block_on_close = True
#     # For non-daemonic threads, list of threading.Threading objects
#     # used by server_close() to wait for all threads completion.
#     _threads = None
#
#     def process_request_thread(self, request, client_address):
#         """Same as in BaseServer but as a thread.
#
#         In addition, exception handling is done here.
#
#         """
#         try:
#             self.finish_request(request, client_address)
#         except Exception:
#             self.handle_error(request, client_address)
#         finally:
#             self.shutdown_request(request)
#
#     def process_request(self, request, client_address):
#         """Start a new thread to process the request."""
#         t = threading.Thread(target=self.process_request_thread,
#                              args=(request, client_address))
#         t.daemon = self.daemon_threads
#         if not t.daemon and self.block_on_close:
#             if self._threads is None:
#                 self._threads = []
#             self._threads.append(t)
#         t.start()

class MultipleRequestsHandler(ThreadingMixIn, HTTPServer):
    pass


if __name__ == '__main__':
    # getting_interface_ip()
    print('server is stating.....')
    print("Server started at:: http://%s:%s" % (str(server_obj["host"]), int(server_obj['port'])))
    # with MultipleRequestsHandler((str(server_obj["host_ip"]), int(server_obj['port'])), http_handler) as server:
    #     server.serve_forever()
    with HTTPServer((str(server_obj["host"]), int(server_obj['port'])), http_handler) as server:
        server.serve_forever()
