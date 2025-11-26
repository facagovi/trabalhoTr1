import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

# plotting
try:
    import matplotlib
    matplotlib.use('TkAgg')
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
except Exception as e:
    matplotlib = None

import numpy as np
from fisica import ask, fsk, qpsk, qam16
from decode_fis import ask_decode, fsk_decode, qpsk_decode, qam16_decode

# helper conversions

def string_to_bits(message):
    return [int(bit) for bit in ''.join(format(ord(c), '08b') for c in message)]

def bits_to_string(bits):
    # ensure length multiple of 8
    if len(bits) % 8 != 0:
        # truncate to multiple of 8 for printable chars
        bits = bits[:len(bits) - (len(bits) % 8)]
    chars = [chr(int(''.join(map(str, bits[i:i+8])), 2)) for i in range(0, len(bits), 8)]
    return ''.join(chars)

# main GUI
class PlotGUI:
    def __init__(self, root):
        self.root = root
        root.title('Visualizador de Modulação (ASK/FSK/QPSK/QAM16)')
        root.geometry('1100x750')

        top = tk.Frame(root)
        top.pack(side=tk.TOP, fill=tk.X, padx=8, pady=8)

        tk.Label(top, text='Mensagem:').pack(side=tk.LEFT)
        self.entry = tk.Entry(top, width=40)
        self.entry.pack(side=tk.LEFT, padx=6)
        self.entry.insert(0, 'Oi')

        tk.Label(top, text='Modulação:').pack(side=tk.LEFT, padx=(10,0))
        self.mod_var = tk.StringVar(value='ASK')
        mod_opts = ['ASK', 'FSK', 'QPSK', 'QAM16']
        self.mod_combo = ttk.Combobox(top, values=mod_opts, textvariable=self.mod_var, width=8, state='readonly')
        self.mod_combo.pack(side=tk.LEFT, padx=6)

        tk.Label(top, text='Amp (ASK/QAM):').pack(side=tk.LEFT, padx=(10,0))
        self.amp_var = tk.DoubleVar(value=1.0)
        self.amp_entry = tk.Entry(top, textvariable=self.amp_var, width=6)
        self.amp_entry.pack(side=tk.LEFT, padx=4)

        tk.Label(top, text='f1,f2 (FSK):').pack(side=tk.LEFT, padx=(10,0))
        self.f1_var = tk.IntVar(value=5)
        self.f2_var = tk.IntVar(value=10)
        self.f1_entry = tk.Entry(top, textvariable=self.f1_var, width=4)
        self.f1_entry.pack(side=tk.LEFT, padx=(4,2))
        self.f2_entry = tk.Entry(top, textvariable=self.f2_var, width=4)
        self.f2_entry.pack(side=tk.LEFT, padx=(0,6))

        btn_plot = tk.Button(top, text='Gerar/Plotar', command=self.plot)
        btn_plot.pack(side=tk.LEFT, padx=8)

        # Figure area
        if matplotlib is None:
            tk.Label(root, text='Matplotlib não encontrado. Instale com: pip install matplotlib', fg='red').pack(padx=10, pady=20)
            return

        self.fig = Figure(figsize=(10,5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # bottom text
        bottom = tk.LabelFrame(root, text='Decodificação / Observações')
        bottom.pack(side=tk.BOTTOM, fill=tk.X, padx=8, pady=6)
        self.result_text = tk.Text(bottom, height=6, wrap='word')
        self.result_text.pack(fill=tk.X, padx=4, pady=4)

    def plot(self):
        message = self.entry.get()
        if not message:
            messagebox.showerror('Erro', 'Digite uma mensagem')
            return

        bits = string_to_bits(message)
        mod = self.mod_var.get()

        # pad bits for symbol groups
        if mod == 'QPSK':
            if len(bits) % 2 != 0:
                bits.append(0)
        if mod == 'QAM16':
            while len(bits) % 4 != 0:
                bits.append(0)

        # generate signal
        try:
            if mod == 'ASK':
                amp = float(self.amp_var.get())
                sig = ask(bits, amp)
                decoded = ask_decode(sig, amp)

            elif mod == 'FSK':
                f1 = int(self.f1_var.get())
                f2 = int(self.f2_var.get())
                sig = fsk(bits, f1, f2)
                decoded = fsk_decode(sig, f1, f2)

            elif mod == 'QPSK':
                sig = qpsk(bits)
                decoded = qpsk_decode(sig)

            elif mod == 'QAM16':
                sig = qam16(bits)
                decoded = qam16_decode(sig)

            else:
                messagebox.showerror('Erro', 'Modulação inválida')
                return
        except Exception as e:
            messagebox.showerror('Erro na geração do sinal', str(e))
            return

        # prepare x axis: show first N samples for readability
        N = min(len(sig), 800)  # show up to 800 samples
        t = np.arange(N)

        self.ax.clear()
        self.ax.plot(t, sig[:N], linewidth=1)
        self.ax.set_title(f'{mod} - sinal codificado (primeiros {N} amostras)')
        self.ax.set_xlabel('Amostras')
        self.ax.set_ylabel('Amplitude')
        self.ax.grid(True)
        self.canvas.draw()

        # show decoded bits and message
        self.result_text.delete('1.0', tk.END)
        self.result_text.insert(tk.END, f'Mensagem original: {message}\n')
        self.result_text.insert(tk.END, f'Trem de bits ({len(bits)}): {bits}\n')
        self.result_text.insert(tk.END, '-'*80 + '\n')
        self.result_text.insert(tk.END, f'Trem decodificado ({len(decoded)}): {decoded}\n')

        decoded_msg = bits_to_string(decoded)
        self.result_text.insert(tk.END, f'Mensagem decodificada: {decoded_msg}\n')
        if decoded_msg == message:
            self.result_text.insert(tk.END, '\n✓ Decodificação OK\n')
        else:
            self.result_text.insert(tk.END, '\n✗ Decodificação diferente (pode ser por padding ou perda)\n')


if __name__ == '__main__':
    root = tk.Tk()
    app = PlotGUI(root)
    root.mainloop()
