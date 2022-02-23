import os
import sys
import getopt
import logging

from http.server import BaseHTTPRequestHandler,  HTTPServer
from CGIHTTPServer
import json

# CRUD to REST conventions
# POST   Create
# GET    Retrieve
# PUT    Update
# DELETE Delete

"""
API REST del servidor.

GET /todos        - Recupera la lista de tareas (ToDos)
DELETE /todos/id  - Elimina la tarea con el id especificado
POST /todos       - Añade una nueva tarea con los valores especificados como parámetros
PUT /todos/id     - Actualiza los valores espcificados en los parámetros para la tarea con
                    el id dado

Tanto los parámetros (en el cuerpo de la petición) como las respuestas son en formato JSON.
"""

logging.basicConfig(level=logging.DEBUG)

class RESTHTTPRequestHandler(CGIHTTPRequestHandler):


    def _GET(self):
        if self.path == self.res_path:
            tasks = self.dao.findTasks()
            return {'code': 'ok', 'data': tasks}
        else:
            _,res,id = self.path.split("/")
            int(id)
            assert(res==self.res_string)
            data = self.dao.retrieveTask(id)
            return {'code': 'ok', 'data': data}

    def _POST(self):
        assert(self.path == self.res_path)
        if 'Content-length' in self.headers:
            data = json.loads(self.rfile.read(int(self.headers['Content-length'])))
        else:
            data = json.load(self.rfile)
        self.dao.createTask(data)
        return {'code': 'ok'}


    def _PUT(self):
        _,res,id = self.path.split("/")
        int(id)
        assert(res==self.res_string)
        if 'Content-length' in self.headers:
            data = json.loads(self.rfile.read(int(self.headers['Content-length'])))
        else:
            data = json.load(self.rfile)
        self.dao.updateTask(id, data)
        return {'code': 'ok'}


    def _DELETE(self):
        _,res,id = self.path.split("/")
        int(id)
        assert(res==self.res_string)
        self.dao.deleteTask(id)
        return {'code': 'ok'}


    def _send(self, data):
        response = json.dumps(data)
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Content-Length", len(response))
        self.end_headers()
        self.wfile.write(response)


    # El BaseHTTPRequestHandler no está pensado para ésto :(
    def do_POST(self):
        self._reroute()
    def do_PUT(self):
        self._reroute()
    def do_GET(self):
        self._reroute()
    def do_DELETE(self):
        self._reroute()
    def _reroute(self):
        try:
            if self.path.startswith(self.res_path):
                method_name = '_' + self.command
                method = getattr(self, method_name)
                try:
                    self._send(method())
                except (ValueError, AssertionError):
                    self.send_error(400, "Invalid request")
                except:
                    logging.exception("Database access error")
                    self.send_error(500, "DDBB error")
            else:
                if self.path == "/" or self.path == "/index.html":
                    self.path = "/cgi-bin/todolist.cgi"
                method_name = 'do_' + self.command
                method = getattr(CGIHTTPRequestHandler, method_name)
                method(self)
        except AttributeError:
            self.send_error(501, "Unsupported method (%r)" % self.command)


#---- Defaults
port = "8080"
basedir = "www/"
#----

#----------------------------------------
def usage():
    print ("Uso: " +  os.path.basename(sys.argv[0]) + " -h -p port")
    print ("     -h         Muestra este mensaje")
    print ("     -p port    Sirve en el puerto indicado (def={0})".format(port))
    print ("     -d dirname Sirve el contenido del directorio indicado (def={0})".format(basedir))

#----------------------------------------

try:
    opts, args = getopt.getopt(sys.argv[1:], "hp:d:", ["help", "port=", "dir="])
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o in ("-h", "--help"):
        usage()
        sys.exit()
    if o in ("-p", "--port"):
        port = a
    if o in ("-d", "--dir"):
        basedir = a

if (port == None):
    usage()
    sys.exit()

try:
    address = ('', int(port))
except ValueError:
    usage()
    sys.exit(2)

httpd = BaseHTTPServer.HTTPServer(address,
                                  RESTHTTPRequestHandler)
os.chdir(basedir)
httpd.serve_forever()