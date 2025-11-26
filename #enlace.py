class EnlaceTx:
    def __init__(self):
    # padrão IEEE/ASCII
    #FLAG 01111110 (Usada para marcar inicio/fim)
        self.FLAG = [0, 1, 1, 1, 1, 1, 1, 0] 
    #ESC 00011011 (Usada para proteger dados que parecem flags)
        self.ESC  = [0, 0, 0, 1, 1, 0, 1, 1] 

    def _lista_para_bits(self, valor, num_bits):
        binario_str = f'{valor:0{num_bits}b}'
        return [int(b) for b in binario_str]  
    
    def enquadra_contagem_caracteres(self, dados):
        quantidade_bytes = len(dados) // 8
        header = self._lista_para_bits(quantidade_bytes, 16)
        return header + dados 
    
    def enquadra_insercao_bytes(self, dados):
        quadro_protegido = []
        for i in range(0, len(dados), 8):
            #8bits=1 byte
            byte_atual = dados[i : i+8]
            if byte_atual == self.FLAG or byte_atual == self.ESC:
                #insere o ESC de proteção antes
                quadro_protegido.extend(self.ESC)

            quadro_protegido.extend(byte_atual)

        return self.FLAG + quadro_protegido + self.FLAG 
    
    def enquadra_insercao_bits(self, dados):
        buffer_saida = []
        contador_uns = 0

        for bit in dados:
            buffer_saida.append(bit)
            if bit == 1:
                contador_uns += 1                
                if contador_uns == 5:
                    buffer_saida.append(0)
                    contador_uns = 0   
            else:
                contador_uns = 0
        return self.FLAG + buffer_saida + self.FLAG 
    
    def detecta_paridade_par(self, dados):
        qtd_uns = dados.count(1)
        bit_paridade = 1 if qtd_uns % 2 != 0 else 0
        return dados + [bit_paridade]
    
    def detecta_checksum(self, dados):
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
        checksum_bits = self._lista_para_bits(checksum, 16)
        return dados + checksum_bits

    def detecta_crc32(self, dados):
        #gerador do IEEE 802.3
        polinomio = [1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1]
        dados_aumentados = list(dados) + [0] * 32
        #(XOR)
        for i in range(len(dados)): 
            if dados_aumentados[i] == 1:
                for j in range(len(polinomio)):
                    dados_aumentados[i + j] = dados_aumentados[i + j] ^ polinomio[j] #subtração em GF(2) é XOR
        resto = dados_aumentados[-(len(polinomio)-1):]
        return dados + resto 
    
    def correcao_hamming(self, dados):
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