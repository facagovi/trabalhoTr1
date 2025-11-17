import socket

tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_server.bind(('localhost', 9999))

tcp_server.listen()
print('Server is listening on port 9999...')
conn, addr = tcp_server.accept()

while True:
    data = conn.recv(1024)
    if not data:
        break
    print(f'Received: {data.decode('utf-8')}')