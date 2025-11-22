import socket
from bitarray import bitarray # type: ignore

# cria um socket servidor
tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# hoespedado em um IP e porta
tcp_server.bind(('localhost', 9999))

# está disposto a receber uma mensagem
tcp_server.listen()

print('ouvidos na porta 9999...')
# tcp_server aceita a conexão
# cria novo socket de conexão
# e aceita o endereço do client
conn, addr = tcp_server.accept()

# recebe a mensagem em um pacote de 1024 bytes
data = conn.recv(1024)
print(f'Recebido cru: {data}')

# transfrormando em trem de bits
bits = bitarray()
bits.frombytes(data)
print(f'Recebido bits: {bits}')

# printa a mensagem decodificada
decod_data = data.decode('utf-8')
print(f'Recebidos: {decod_data}')

# fecha a conexão
conn.close()
tcp_server.close()