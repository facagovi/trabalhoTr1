import socket

from requests import post

tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_client.connect(('localhost', 9999))

status = tcp_client.send(b'Hello, Server!')

print(f'Sent {status} bytes to the server.')