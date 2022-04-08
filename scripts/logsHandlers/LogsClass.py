# import configparser
import configparser

# using the config file use the path to append what ever is being sent as a log
config = configparser.ConfigParser()
config.read('/etc/myConfigFiles/configuration.ini')

ERROR_FILE_LOG = config.get('log', 'ErrorLogs')
ACCESS_FILE_LOG = config.get('log', 'AccessLogs')
SERVER_FILE_LOG = config.get('log', 'ServerLogs')

class Logs:
    def __init__(self):
        self.headers = None
        self.client_address = None
        self.date_time_string = None

    def server_log(self, *args):
        """
        :rtype: object
        """
        f = open(SERVER_FILE_LOG, "a")
        f.write("client : {} | port : {} | http request :{}, status :{} \n".format(self.client_address[0],
                                                                                   self.client_address[1],
                                                                                   args[0],
                                                                                   args[1]))

    def access_log(self, *args, ):
        # ip address - authentication - [date and time]
        # "request from the client"[HTTP]
        # action, status, size_in_bytes
        # identifier of the web browser
        f = open(ACCESS_FILE_LOG, "a")
        f.write('{} - -[{}] - - "{}" - - {} - - {} \n'.format(self.client_address[0],
                                                              self.date_time_string().split(",")[1],
                                                              args[0], args[1], self.headers["User-Agent"]))
        f.close()

    def log_error(self, *args):
        pass
        # f = open(ERROR_FILE_LOG,"a")
        # f.write(self)