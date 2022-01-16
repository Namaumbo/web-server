import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from http_parser.http import HttpStream

Error_Page = """\
       <html>
       <body>
       <h2 
        style="color:black;
        font-family:Sans-serif;
        text-align:center;
        font-size:35px"
        >Welcome to Mandebvu Server </h2>
        <hr />
        <br />
       <h1>Error accessing {path}</h1>
       <p>{msg}</p>
       </body>
       </html>
       """


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


class case_directory_index_file(object):
    '''Serve index.html page for a directory.'''

    def index_path(self, handler):
        return os.path.join(handler.full_path, 'index.html')

    def test(self, handler):
        return os.path.isdir(handler.full_path) and \
               os.path.isfile(self.index_path(handler))

    def act(self, handler):
        handler.handle_file(self.index_path(handler))




Listing_Page = '''\
             <html>
             <body>
             <ul>
             {0}
             </ul>
             </body>
             </html>'''


class http_handler(BaseHTTPRequestHandler):
    Cases = [case_no_file(),
             case_existing_file(),
             case_directory_index_file(),
             case_always_fail()]

    def act(self, handler):
        handler.list_dir(handler.full_path)



    # overridden function provided by the BaseHTTPRequestHandler
    def do_GET(self):
        try:
            # Figure out what exactly is being requested.
            global msg
            self.full_path = os.getcwd() + self.path

            # Figure out how to handle it.
            for case in self.Cases:
                handler = case()
                if handler.test(self):
                    handler.act(self)
                    break

        # Handle errors.
        except Exception as msg:
            self.handle_error(msg)

    def handle_file(self, full_path):
        try:
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

        # Send actual content.

    def list_dir(self, full_path):
        try:
            entries = os.listdir(full_path)
            bullets = ['<li>{0}</li>'.format(e)
                       for e in entries if not e.startswith('.')]
            page = Listing_Page.format('\n'.join(bullets))
            self.send_content(page)
        except OSError as msg:
            msg = "'{0}' cannot be listed: {1}".format(self.path, msg)
            self.handle_error(msg)

    def send_content(self, content, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content.encode(encoding="UTF-8"))


if __name__ == '__main__':
    with HTTPServer(('', 8000), http_handler) as server:
        # the server will serve the clients until they have to close the connection
        server.serve_forever()
