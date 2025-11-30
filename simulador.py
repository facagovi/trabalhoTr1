import numpy as np
from enlace import EnlaceTx
from decode_enlance import EnlaceRx
import fisica
import decode_fis

class Simulador:
#caminho da mensagem + ruído + volta 
    def __init__(self):
        self.tx = EnlaceTx()
        self.rx = EnlaceRx()

    def bitamento(self, message):
        return [int(bit) for bit in ''.join(format(ord(c), '08b') for c in message)]

    def stringamento(self, bits):
        limite = len(bits) - (len(bits) % 8)
        bits = bits[:limite]
        chars = [chr(int(''.join(map(str, bits[i:i+8])), 2)) for i in range(0, len(bits), 8)]
        return ''.join(chars)

    def ruido(self, sinal, sigma):
        ruido = np.random.normal(0, sigma, len(sinal))
        return sinal + ruido

    def executar_simulacao(self, mensagem, config):
        #TRANSMISSOR
        bits_dados = self.bitamento(mensagem)
        bits_enlace_entrada = list(bits_dados) 

        #enlace - controle de erro
        if config['erro'] == 'Paridade':
            bits_dados = self.tx.detPar(bits_dados)
        elif config['erro'] == 'Checksum':
            bits_dados = self.tx.detSoma(bits_dados)
        elif config['erro'] == 'CRC32':
            bits_dados = self.tx.det32(bits_dados)
        elif config['erro'] == 'Hamming':
            bits_dados = self.tx.hamming(bits_dados)

        #enlace - enquadramento
        if config['enquadramento'] == 'Contagem':
            bits_quadro = self.tx.enqCont(bits_dados)
        elif config['enquadramento'] == 'Byte Stuffing':
            bits_quadro = self.tx.enqBytes(bits_dados)
        elif config['enquadramento'] == 'Bit Stuffing':
            bits_quadro = self.tx.enqBits(bits_dados)
        else:
            bits_quadro = bits_dados # Sem enquadramento

        #física - modulção
        sinal_modulado = []
        mod = config['modulacao']
        
        if mod == 'NRZ': sinal_modulado = fisica.nrz(bits_quadro)
        elif mod == 'Manchester': sinal_modulado = fisica.manchester(bits_quadro)
        elif mod == 'Bipolar': sinal_modulado = fisica.bipolar(bits_quadro)
        elif mod == 'ASK': sinal_modulado = fisica.ask(bits_quadro, 1)
        elif mod == 'FSK': sinal_modulado = fisica.fsk(bits_quadro, 5, 10)
        elif mod == 'QPSK': sinal_modulado = fisica.qpsk(bits_quadro)
        elif mod == 'QAM16': sinal_modulado = fisica.qam16(bits_quadro)

        #RUÍDO
        sinal_com_ruido = self.ruido(sinal_modulado, config['sigma_ruido'])

        #RECEPTOR "decode"

        #física-demodulação
        bits_recebidos_fisica = []
        if mod == 'NRZ': bits_recebidos_fisica = decode_fis.nrz_decode(sinal_com_ruido)
        elif mod == 'Manchester': bits_recebidos_fisica = decode_fis.manchester_decode(sinal_com_ruido)
        elif mod == 'Bipolar': bits_recebidos_fisica = decode_fis.bipolar_decode(sinal_com_ruido)
        elif mod == 'ASK': bits_recebidos_fisica = decode_fis.ask_decode(sinal_com_ruido, 1)
        elif mod == 'FSK': bits_recebidos_fisica = decode_fis.fsk_decode(sinal_com_ruido, 5, 10)
        elif mod == 'QPSK': bits_recebidos_fisica = decode_fis.qpsk_decode(sinal_com_ruido)
        elif mod == 'QAM16': bits_recebidos_fisica = decode_fis.qam16_decode(sinal_com_ruido)

        #enlace-desenquadramento
        bits_desenquadrados = []
        if config['enquadramento'] == 'Contagem':
            bits_desenquadrados = self.rx.denqCont(bits_recebidos_fisica)
        elif config['enquadramento'] == 'Byte Stuffing':
            bits_desenquadrados = self.rx.denqBytes(bits_recebidos_fisica)
        elif config['enquadramento'] == 'Bit Stuffing':
            bits_desenquadrados = self.rx.denqBits(bits_recebidos_fisica)
        else:
            bits_desenquadrados = bits_recebidos_fisica

        #enlace-correção de erro
        status = "Sem Verificação"
        bits_finais = bits_desenquadrados
        
        if config['erro'] == 'Paridade':
            ok, dados_uteis = self.rx.Ddetpar(bits_desenquadrados)
            status = "Sucesso" if ok else "Erro Detectado (Paridade)"
            bits_finais = dados_uteis
        elif config['erro'] == 'Checksum':
            ok, dados_uteis = self.rx.Ddetsoma(bits_desenquadrados)
            status = "Sucesso" if ok else "Erro Detectado (Checksum)"
            bits_finais = dados_uteis
        elif config['erro'] == 'CRC32':
            ok, dados_uteis = self.rx.Ddet32(bits_desenquadrados)
            status = "Sucesso" if ok else "Erro Detectado (CRC32)"
            bits_finais = dados_uteis
        elif config['erro'] == 'Hamming':
            bits_finais = self.rx.decoHamming(bits_desenquadrados)
            status = "Hamming Executado (Tentativa de Correção)"
        texto_final = self.stringamento(bits_finais)

        return {
            "sinal_tx": sinal_modulado,
            "sinal_rx": sinal_com_ruido,
            "texto_final": texto_final,
            "status": status,
            "bits_tx": bits_enlace_entrada,
            "bits_rx": bits_finais
        }