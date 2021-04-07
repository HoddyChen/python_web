# coding=utf-8

import socket
import time

HOST = 'localhost'  # The remote host
PORT = 8000  # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

s.sendall(bytes("Hello, \n", encoding="utf8"))
time.sleep(5)
s.sendall(bytes("old, \n", encoding="utf8"))

data = s.recv(1024)

print('Received', repr(data))

time.sleep(60)
s.close()