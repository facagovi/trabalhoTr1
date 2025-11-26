class EnlaceRx:
    def __init__(self):
        self.FLAG = [0, 1, 1, 1, 1, 1, 1, 0] 
        self.ESC  = [0, 0, 0, 1, 1, 0, 1, 1] 

    def _bits_para_int(self, lista_bits):
        binario_str = "".join(str(b) for b in lista_bits)
        return int(binario_str, 2)
    
    def desenquadra_contagem_caracteres(self, quadro):
        if len(quadro) < 16:
            return []
        header = quadro[:16]
        qtd_bytes = self._bits_para_int(header)
        fim_dados = 16 + (qtd_bytes * 8)
        return quadro[16:fim_dados]

    def desenquadra_insercao_bytes(self, quadro):
        if quadro[:8] == self.FLAG:
            quadro = quadro[8:]
        if quadro[-8:] == self.FLAG:
            quadro = quadro[:-8]
            
        dados_limpos = []
        i = 0
        while i < len(quadro):
            byte_atual = quadro[i : i+8]
            if byte_atual == self.ESC:
                #pula o ESC (i+8) e pega o próximo byte como dado literal
                i += 8
                proximo_byte = quadro[i : i+8]
                dados_limpos.extend(proximo_byte)
            else:
                dados_limpos.extend(byte_atual)
            i += 8
        return dados_limpos

    def desenquadra_insercao_bits(self, quadro):
        if quadro[:8] == self.FLAG:
            quadro = quadro[8:]
        if quadro[-8:] == self.FLAG:
            quadro = quadro[:-8]

        dados_limpos = []
        contador_uns = 0
        
        i = 0
        while i < len(quadro):
            bit = quadro[i]
            
            if bit == 1:
                contador_uns += 1
                dados_limpos.append(bit)
            else:
                if contador_uns == 5:
                    pass #ignora o 0 inserido na transmissão
                else:
                    dados_limpos.append(bit)
                
                contador_uns = 0 
            i += 1
        return dados_limpos

    def checa_paridade_par(self, quadro):
        qtd_uns = quadro.count(1)
        if qtd_uns % 2 == 0:
            return True, quadro[:-1]
        else:
            return False, []
    def checa_checksum(self, quadro):
        dados_copia = list(quadro)
        soma = 0
        for i in range(0, len(dados_copia), 16):
            pedaco = dados_copia[i : i+16]
            pedaco_int = int("".join(str(x) for x in pedaco), 2)
            soma += pedaco_int
            while soma > 0xFFFF:
                carry = soma >> 16
                soma = soma & 0xFFFF
                soma += carry
        if (~soma & 0xFFFF) == 0:
            return True, quadro[:-16]
        else:
            return False, []
    def checa_crc32(self, quadro):
        polinomio = [1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1]
        dados_trabalho = list(quadro)
        
        for i in range(len(dados_trabalho) - 32):
            if dados_trabalho[i] == 1:
                for j in range(len(polinomio)):
                    dados_trabalho[i + j] ^= polinomio[j]         
        resto = dados_trabalho[-32:]
        if 1 not in resto: 
            return True, quadro[:-32] 
        else:
            return False, []
    def decodifica_hamming(self, quadro):
        dados_finais = []
        
        for i in range(0, len(quadro), 7):
            bloco = quadro[i : i+7]
            if len(bloco) < 7: break 
            #verificaçao p1
            s1 = bloco[0] ^ bloco[2] ^ bloco[4] ^ bloco[6]
            #verificao p2
            s2 = bloco[1] ^ bloco[2] ^ bloco[5] ^ bloco[6]
            #verificaçao p4
            s3 = bloco[3] ^ bloco[4] ^ bloco[5] ^ bloco[6]
            posicao_erro = (s3 * 4) + (s2 * 2) + s1
            
            if posicao_erro != 0:
                idx = posicao_erro - 1
                bloco[idx] = 1 if bloco[idx] == 0 else 0
            
            nibble = [bloco[2], bloco[4], bloco[5], bloco[6]]
            dados_finais.extend(nibble)
            
        return dados_finais