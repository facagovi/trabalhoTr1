import tkinter as tk
from tkinter import messagebox
from tkinter import scrolledtext
from fisica import nrz, manchester, bipolar, ask, fsk, qpsk, qam16
from decode_fis import nrz_decode, manchester_decode, bipolar_decode, ask_decode, fsk_decode, qpsk_decode, qam16_decode

# Função para converter mensagem em lista de bits (simples)
def string_to_bits(message):
    return [int(bit) for bit in ''.join(format(ord(c), '08b') for c in message)]

def bits_to_string(bits):
    chars = [chr(int(''.join(map(str, bits[i:i+8])), 2)) for i in range(0, len(bits), 8)]
    return ''.join(chars)

# Função para codificar a mensagem com a modulação escolhida
def encode_message():
    message = entry_message.get()
    if not message:
        messagebox.showerror("Erro", "Precisa-se de uma mensagem")
        return

    bit_stream = string_to_bits(message)
    
    # Limpar o texto anterior
    output_text.config(state=tk.NORMAL)
    output_text.delete('1.0', tk.END)
    
    # Obter a modulação selecionada
    modulation_type = modulation_var.get()

    output_text.insert(tk.END, f"Mensagem Original: {message}\n")
    output_text.insert(tk.END, f"Trem de Bits: {bit_stream}\n")
    output_text.insert(tk.END, "="*80 + "\n\n")

    try:
        if modulation_type == "NRZ":
            encoded_signal = nrz(bit_stream)
            decoded_signal = nrz_decode(encoded_signal)
            
        elif modulation_type == "Manchester":
            encoded_signal = manchester(bit_stream)
            decoded_signal = manchester_decode(encoded_signal)
            
        elif modulation_type == "Bipolar":
            encoded_signal = bipolar(bit_stream)
            decoded_signal = bipolar_decode(encoded_signal)
            
        elif modulation_type == "ASK":
            amp = 1.0
            encoded_signal = ask(bit_stream, amp)
            decoded_signal = ask_decode(encoded_signal, amp)
            
        elif modulation_type == "FSK":
            f1, f2 = 5, 10
            encoded_signal = fsk(bit_stream, f1, f2)
            decoded_signal = fsk_decode(encoded_signal, f1, f2)
            
        elif modulation_type == "QPSK":
            # QPSK trabalha com pares de bits
            encoded_signal = qpsk(bit_stream)
            decoded_signal = qpsk_decode(encoded_signal)
            
        elif modulation_type == "QAM16":
            # QAM16 trabalha com quadriciclos de bits
            encoded_signal = qam16(bit_stream)
            decoded_signal = qam16_decode(encoded_signal)
            
        else:
            messagebox.showerror("Erro", "Modulação não implementada.")
            output_text.config(state=tk.DISABLED)
            return
        
        # Exibir a codificação
        output_text.insert(tk.END, f"SINAL CODIFICADO:\n{encoded_signal}\n\n")
        output_text.insert(tk.END, "="*80 + "\n\n")
        
        # Decodificar para verificar
        output_text.insert(tk.END, f"TREM DECODIFICADO:\n{decoded_signal}\n\n")
        output_text.insert(tk.END, "="*80 + "\n\n")
        
        # Mostrar mensagem decodificada
        decoded_message_str = bits_to_string(decoded_signal)
        output_text.insert(tk.END, f"Mensagem Decodificada: {decoded_message_str}\n")
        
        # Verificar se a decodificação foi bem-sucedida
        if decoded_message_str == message:
            output_text.insert(tk.END, "\n✓ Decodificação bem-sucedida!\n", "success")
        else:
            output_text.insert(tk.END, "\n✗ Decodificação com erro!\n", "error")
        
    except Exception as e:
        output_text.insert(tk.END, f"Erro na modulação: {str(e)}\n")
    
    output_text.config(state=tk.DISABLED)

# Criando a interface gráfica com Tkinter
root = tk.Tk()
root.title("Testador de Modulação - Camada Física")
root.geometry("1000x700")

# Frame superior para entrada e escolha de modulação
frame_top = tk.Frame(root)
frame_top.pack(padx=10, pady=10, fill=tk.X)

# Label e Entry para digitar a mensagem
label_message = tk.Label(frame_top, text="Digite a mensagem:")
label_message.pack(side=tk.LEFT, padx=5)

entry_message = tk.Entry(frame_top, width=40)
entry_message.pack(side=tk.LEFT, padx=5)

# Botão de Codificação e Decodificação
button_encode = tk.Button(frame_top, text="Codificar e Decodificar", command=encode_message, bg="#4CAF50", fg="white")
button_encode.pack(side=tk.LEFT, padx=5)

# Frame para escolha de modulação
frame_modulation = tk.LabelFrame(root, text="Escolha a modulação:", padx=10, pady=10)
frame_modulation.pack(padx=10, pady=5, fill=tk.X)

modulation_var = tk.StringVar(value="NRZ")

radio_nrz = tk.Radiobutton(frame_modulation, text="NRZ", variable=modulation_var, value="NRZ")
radio_nrz.pack(side=tk.LEFT, padx=5)

radio_manchester = tk.Radiobutton(frame_modulation, text="Manchester", variable=modulation_var, value="Manchester")
radio_manchester.pack(side=tk.LEFT, padx=5)

radio_bipolar = tk.Radiobutton(frame_modulation, text="Bipolar", variable=modulation_var, value="Bipolar")
radio_bipolar.pack(side=tk.LEFT, padx=5)

radio_ask = tk.Radiobutton(frame_modulation, text="ASK", variable=modulation_var, value="ASK")
radio_ask.pack(side=tk.LEFT, padx=5)

radio_fsk = tk.Radiobutton(frame_modulation, text="FSK", variable=modulation_var, value="FSK")
radio_fsk.pack(side=tk.LEFT, padx=5)

radio_qpsk = tk.Radiobutton(frame_modulation, text="QPSK", variable=modulation_var, value="QPSK")
radio_qpsk.pack(side=tk.LEFT, padx=5)

radio_qam16 = tk.Radiobutton(frame_modulation, text="QAM16", variable=modulation_var, value="QAM16")
radio_qam16.pack(side=tk.LEFT, padx=5)

# Frame para saída de texto
frame_output = tk.LabelFrame(root, text="Resultado da Codificação/Decodificação:", padx=5, pady=5)
frame_output.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

# ScrolledText para mostrar saída completa
output_text = scrolledtext.ScrolledText(frame_output, wrap=tk.WORD, width=100, height=25, font=("Courier", 9))
output_text.pack(fill=tk.BOTH, expand=True)

# Configurar tags para cores
output_text.tag_configure("success", foreground="green", font=("Courier", 9, "bold"))
output_text.tag_configure("error", foreground="red", font=("Courier", 9, "bold"))

# Inicializar a interface
root.mainloop()
