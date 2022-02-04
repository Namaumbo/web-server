import json
import subprocess
import socket
proc = subprocess.check_output('ipconfig').decode('utf-8')

ip = socket.gethostbyname(socket.gethostname())
print(ip)