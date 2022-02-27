import sys
# import logging


class Logs:
    # logging.basicConfig(filename="./Logs/access.log",
    #                     format='%(Pastime)s %(message)s',
    #                     filemode='w')
    # logger = logging.getLogger()
    #
    # logger.setLevel(logging.DEBUG)

    # this will be for logging and it is overridden from the baseHTTHandler
    def __init__(self):
        self.headers = None
        self.client_address = None
        self.date_time_string = None

    def server_log(self, *args):
        """

        :rtype: object
        """
        # This will print in the terminal
        sys.stdout.write("client : {} | port : {} | http request :{}, status :{} \n".format(self.client_address[0],
                                                                                            self.client_address[1],
                                                                                            args[0],
                                                                                            args[1]))

    def access_log(self, *args, ):
        # ip address - authentication - [date and time]
        # "request from the client"[HTTP
        # action, status, size_in_bytes
        # identifier of the web browser]

        f = open("/var/log/my-server-access.log", "a")
        f.write('{} - -[{}] - - "{}" - - {} - - {} \n'.format(self.client_address[0],
                                                              self.date_time_string().split(",")[1],
                                                              args[0], args[1], self.headers["User-Agent"]))
        f.close()
