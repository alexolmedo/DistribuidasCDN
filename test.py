import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('172.29.64.175', 8999))