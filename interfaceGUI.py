import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import numpy as np

# Função de codificação simples (ASK - Amplitude Shift Keying)
def ask(amp, bits):
    sinal = []
    for bit in bits:
        if bit == 1:
            for t in range(100):  # 100 amostras por bit
                valor = amp * np.sin(2 * np.pi * (t / 100))  # Gera onda para bit = 1
                sinal.append(valor)
        else:
            for t in range(100):  # Sinal de 0 (pode ser 0 ou um valor muito pequeno)
                sinal.append(0.001)
    return sinal

# Função de decodificação simples (ASK)
def ask_decode(sinal, amp):
    trem = []
    for i in range(0, len(sinal), 100):
        segmento = sinal[i:i+100]
        media = np.mean(np.abs(segmento))  # Calcula a média das amostras
        if media > (amp / 2):  # Se média for maior que metade da amplitude, é 1
            trem.append(1)
        else:
            trem.append(0)
    return trem

# Função chamada quando o botão "Enviar" for pressionado
def enviar_dados(button):
    msg = entry_msg.get_text()  # Pega o texto da entrada
    bits = [int(b) for b in ''.join(format(ord(char), '08b') for char in msg)]  # Converte mensagem para bits
    print(f"Mensagem: {msg} -> Bits: {bits}")
    
    # Chama a modulação ASK
    sinal = ask(1, bits)  # Amplitude 1 para simplicidade

    # Chama a decodificação
    bits_decodificados = ask_decode(sinal, 1)  # Decodifica com a mesma amplitude

    # Exibe os resultados na interface
    label_resultado.set_text(f"Mensagem decodificada: {''.join(map(str, bits_decodificados))}")

# Configuração da interface GTK
win = Gtk.Window()
win.set_title("Simulação de Modulação ASK")
win.set_size_request(400, 300)

# Layout da janela
box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
win.add(box)

# Campo de entrada para a mensagem
label_msg = Gtk.Label(label="Digite a mensagem:")
box.pack_start(label_msg, False, False, 0)

entry_msg = Gtk.Entry()
box.pack_start(entry_msg, False, False, 0)

# Botão para enviar dados
btn_enviar = Gtk.Button(label="Enviar Dados")
btn_enviar.connect("clicked", enviar_dados)
box.pack_start(btn_enviar, False, False, 0)

# Label para mostrar o resultado
label_resultado = Gtk.Label(label="Mensagem decodificada: ")
box.pack_start(label_resultado, False, False, 0)

# Exibe a janela
win.connect("destroy", Gtk.main_quit)
win.show_all()

# Inicia o loop principal do GTK
Gtk.main()
