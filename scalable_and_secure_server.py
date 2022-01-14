from http.server import BaseHTTPRequestHandler, HTTPServer


class http_handler(BaseHTTPRequestHandler):
    print("working class")


if __name__ == '__main__':
    with HTTPServer(('', 8000), http_handler) as server:
        # the server will serve the clients untill they have to close the connection
        server.serve_forever()
