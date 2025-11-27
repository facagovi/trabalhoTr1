class EnlaceTx:
    def __init__(self):
    #FLAG 01111110 (Usada para marcar inicio/fim)
        self.FLAG = [0, 1, 1, 1, 1, 1, 1, 0] 
    #ESC 00011011 (Usada para proteger dados que parecem flags)
        self.ESC  = [0, 0, 0, 1, 1, 0, 1, 1] 

    def trem(self, valor, num_bits):
        binario_str = f'{valor:0{num_bits}b}'
        return [int(b) for b in binario_str]  
    
    def enqCara(self, dados):
        quantbyt = len(dados) // 8
        header = self.trem(quantbyt, 16)
        return header + dados 
    
    def enqBytes(self, dados):
        proteg = []
        for i in range(0, len(dados), 8):
            #8bits=1 byte
            byta = dados[i : i+8]
            if byta == self.FLAG or byta == self.ESC:
                #insere o ESC de proteção antes
                proteg.extend(self.ESC)
            proteg.extend(byta)
        return self.FLAG + proteg + self.FLAG 
    
    def enqBits(self, dados):
        buffer_saida = []
        uns = 0

        for bit in dados:
            buffer_saida.append(bit)
            if bit == 1:
                uns += 1                
                if uns == 5:
                    buffer_saida.append(0)
                    uns = 0   
            else:
                uns = 0
        return self.FLAG + buffer_saida + self.FLAG 
    
    def detPar(self, dados):
        qtd_uns = dados.count(1)
        bit_paridade = 1 if qtd_uns % 2 != 0 else 0
        return dados + [bit_paridade]
    
    def detSoma(self, dados):
        #checksum (Soma de 16 bits com complemento de 1)
        dados_copia = list(dados)
        while len(dados_copia) % 16 != 0:
            dados_copia.append(0)
        soma = 0
        for i in range(0, len(dados_copia), 16):
            pedaco_bits = dados_copia[i : i+16]
            #converte lista de bits para número inteiro
            pedaco_str = "".join(str(x) for x in pedaco_bits)
            pedaco_int = int(pedaco_str, 2)
            soma += pedaco_int
            while soma > 0xFFFF: # 0xFFFF é 65535
                carry = soma >> 16 
                soma = soma & 0xFFFF
                soma += carry       
        #inversão
        checksum = ~soma & 0xFFFF
        checksum_bits = self.trem(checksum, 16)
        return dados + checksum_bits

    def det32(self, dados):
        #IEEE 802.3
        crc = [1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1]
        dados_aumentados = list(dados) + [0] * 32
        #(XOR)
        for i in range(len(dados)): 
            if dados_aumentados[i] == 1:
                for j in range(len(crc)):
                    dados_aumentados[i + j] = dados_aumentados[i + j] ^ crc[j] #subtração em GF(2) é XOR
        resto = dados_aumentados[-(len(crc)-1):]
        return dados + resto 
    
    def hamming(self, dados):
        dados_trabalho = list(dados)
        saida = []
        while len(dados_trabalho) % 4 != 0:
            dados_trabalho.append(0)

        #nibbles
        for i in range(0, len(dados_trabalho), 4):
            chunk = dados_trabalho[i : i+4]
            d1, d2, d3, d4 = chunk[0], chunk[1], chunk[2], chunk[3]
            p1 = d1 ^ d2 ^ d4
            p2 = d1 ^ d3 ^ d4
            p4 = d2 ^ d3 ^ d4
            bloco_codificado = [p1, p2, d1, p4, d2, d3, d4]
            saida.extend(bloco_codificado)

        return saida