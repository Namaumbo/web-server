import sys
from http.server import BaseHTTPRequestHandler
import logging


class server_logs(BaseHTTPRequestHandler):
    # logging.basicConfig(filename="./Logs/access.log",
    #                     format='%(Pastime)s %(message)s',
    #                     filemode='w')
    # logger = logging.getLogger()
    #
    # logger.setLevel(logging.DEBUG)

    # this will be for logging and it is overridden from the baseHTTHandler
    def server_log(self, *args):

        # This will print in the terminal
        sys.stderr.write("client : {} | port : {} | http request :{}, status :{}".format(self.client_address[0],
                                                                                    self.client_address[1],
                                                                                    args[0],
                                                                                    args[1]))

    def access_log(self, *args, ):
        # ip address - authentication - [date and time]
        # "request from the client"[HTTP
        # action, status, size_in_bytes
        # identifier of the web browser]

        f = open("Logs/access.log", "a")
        f.write('{} - -[{}] - - "{}" - - {} - - {} \n'.format(self.client_address[0],
                                                              self.date_time_string().split(",")[1],
                                                              args[1], args[2], self.headers["User-Agent"]))
        f.close()
