import socket
from bitarray import bitarray # type: ignore


# Cria socket client
tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# associa a um IP e porta
tcp_client.connect(('localhost', 9999))

# manda mensagem
data = input("Fale com o mundo: ")
by_data = data.encode('utf-8')
bits = bitarray()
bits.frombytes(by_data)
print('Bits: ',  bits)
print('Cru: ',  by_data)
status = tcp_client.send(by_data)

# printa status
print(f'Sent {status} bytes to the server.')

# fecha o socket
tcp_client.close()