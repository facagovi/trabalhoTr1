class EnlaceTx:
    def __init__(self):
    # padrão IEEE/ASCII
    #FLAG 01111110 (Usada para marcar inicio/fim)
        self.FLAG = [0, 1, 1, 1, 1, 1, 1, 0] 
    
    #ESC 00011011 (Usada para proteger dados que parecem flags)
        self.ESC  = [0, 0, 0, 1, 1, 0, 1, 1] 

    def _lista_para_bits(self, valor, num_bits):
        binario_str = f'{valor:0{num_bits}b}' # Cria string ex: '00001010'
        return [int(b) for b in binario_str]  # Retorna lista [0, 0, 0, 0, 1, 0, 1, 0]
    
    def enquadra_contagem_caracteres(self, dados):
        #calculamos quantos bytes (grupos de 8 bits) existem na lista
        quantidade_bytes = len(dados) // 8
        header = self._lista_para_bits(quantidade_bytes, 16)
        return header + dados 
    
    def enquadra_insercao_bytes(self, dados):
        quadro_protegido = []

        #loop que percorre a lista de 8 em 8 bits (byte a byte)
        for i in range(0, len(dados), 8):
            #8bits=1 byte
            byte_atual = dados[i : i+8]

            #verifica colisão: O dado parece uma FLAG ou um ESC?
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

            #logica de contagem
            if bit == 1:
                contador_uns += 1                
                if contador_uns == 5:
                    buffer_saida.append(0) #insere um 0 forçado para não confundir com flag
                    contador_uns = 0   
            else:
                contador_uns = 0

        #enquadramento entre duas flags
        return self.FLAG + buffer_saida + self.FLAG 
    
    def detecta_paridade_par(self, dados):
        qtd_uns = dados.count(1)
        bit_paridade = 1 if qtd_uns % 2 != 0 else 0
        return dados + [bit_paridade]
    
    def detecta_checksum(self, dados):
        #checksum (Soma de 16 bits com complemento de 1)
        dados_copia = list(dados)
        
        #mensagem precisa ter tamanho múltiplo de 16 bits para a soma
        #se não tiver, completa com 0
        while len(dados_copia) % 16 != 0:
            dados_copia.append(0)
        soma = 0
        #itera pegando pedaços de 16 em 16 bits
        for i in range(0, len(dados_copia), 16):
            pedaco_bits = dados_copia[i : i+16]
            #converte lista de bits para número inteiro
            pedaco_str = "".join(str(x) for x in pedaco_bits)
            pedaco_int = int(pedaco_str, 2)
            soma += pedaco_int
            #overflow = soma passa de 16 bits (> 65535)
            #pegamos o bit que sobrou e somamos de volta no início.
            while soma > 0xFFFF: # 0xFFFF é 65535
                carry = soma >> 16  # Pega o bit que sobrou
                soma = soma & 0xFFFF # Pega apenas os 16 bits principais
                soma += carry        # Soma o excesso de volta
        
        #inverte os bits
        # ~ faz a inversão e o & 0xFFFF garante que fique em 16 bits
        checksum = ~soma & 0xFFFF
        
        # converte o resultado do checksum em lista de bits e anexa ao final
        checksum_bits = self._lista_para_bits(checksum, 16)
        return dados + checksum_bits

    def detecta_crc32(self, dados):
        #gerador do IEEE 802.3
        # valor Hex: 0x04C11DB7
        polinomio = [1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1]
        
        #adiciona 32 zeros ao final da mensagem (Grau do polinômio - 1)
        # Trabalhamos com uma cópia para não alterar o original
        dados_aumentados = list(dados) + [0] * 32
        
        #(XOR)
        for i in range(len(dados)):
            # Só fazemos a divisão se o bit atual for 1 
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

        #processa a mensagem de 4 em 4 bits (Nibbles)
        for i in range(0, len(dados_trabalho), 4):
            #pega o bloco atual de 4 dados (d1, d2, d3, d4)
            chunk = dados_trabalho[i : i+4]
            d1, d2, d3, d4 = chunk[0], chunk[1], chunk[2], chunk[3]

            # calculo das Paridades (Aritmética Módulo 2 / XOR)
            # p1 verifica as posições 1, 3, 5, 7 (d1, d2, d4)
            p1 = d1 ^ d2 ^ d4
            # p2 verifica as posições 2, 3, 6, 7 (d1, d3, d4)
            p2 = d1 ^ d3 ^ d4
            # p4 verifica as posições 4, 5, 6, 7 (d2, d3, d4)
            p4 = d2 ^ d3 ^ d4
            bloco_codificado = [p1, p2, d1, p4, d2, d3, d4]
            saida.extend(bloco_codificado)

        return saida