import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from simulador import Simulador

class Interface:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador TR1 - Camada Física e Enlace")
        self.root.geometry("1200x800")
        
        self.simulador = Simulador()

        self._setup_ui()

    def _setup_ui(self):
        frame_config = tk.LabelFrame(self.root, text="Configurações", padx=10, pady=10)
        frame_config.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        tk.Label(frame_config, text="Mensagem:").pack(anchor="w")
        self.entry_msg = tk.Entry(frame_config, width=30)
        self.entry_msg.insert(0, "TR1 Rocks")
        self.entry_msg.pack(pady=5)

        tk.Label(frame_config, text="Enquadramento:").pack(anchor="w", pady=(10,0))
        self.combo_enq = ttk.Combobox(frame_config, values=["Contagem", "Byte Stuffing", "Bit Stuffing"], state="readonly")
        self.combo_enq.current(0)
        self.combo_enq.pack(fill=tk.X)

        tk.Label(frame_config, text="Detecção/Correção de Erro:").pack(anchor="w", pady=(10,0))
        self.combo_erro = ttk.Combobox(frame_config, values=["Paridade", "Checksum", "CRC32", "Hamming"], state="readonly")
        self.combo_erro.current(0)
        self.combo_erro.pack(fill=tk.X)

        tk.Label(frame_config, text="Modulação (Física):").pack(anchor="w", pady=(10,0))
        mod_opts = ["NRZ", "Manchester", "Bipolar", "ASK", "FSK", "QPSK", "QAM16"]
        self.combo_mod = ttk.Combobox(frame_config, values=mod_opts, state="readonly")
        self.combo_mod.current(0)
        self.combo_mod.pack(fill=tk.X)

        tk.Label(frame_config, text="Nível de Ruído (Sigma):").pack(anchor="w", pady=(10,0))
        self.scale_ruido = tk.Scale(frame_config, from_=0.0, to=2.0, resolution=0.1, orient=tk.HORIZONTAL)
        self.scale_ruido.set(0.0)
        self.scale_ruido.pack(fill=tk.X)

        btn_enviar = tk.Button(frame_config, text="SIMULAR TRANSMISSÃO", bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), command=self.run_simulacao)
        btn_enviar.pack(pady=20, fill=tk.X)

        frame_result = tk.Frame(self.root)
        frame_result.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.fig = Figure(figsize=(8, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Sinal no Meio de Comunicação (Com Ruído)")
        self.ax.set_xlabel("Tempo / Amostras")
        self.ax.set_ylabel("Amplitude (V)")
        self.ax.grid(True)

        self.canvas = FigureCanvasTkAgg(self.fig, master=frame_result)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        frame_logs = tk.LabelFrame(frame_result, text="Logs da Simulação", height=200)
        frame_logs.pack(fill=tk.X, pady=10)
        
        self.txt_log = tk.Text(frame_logs, height=10, font=("Consolas", 9))
        self.txt_log.pack(fill=tk.BOTH, padx=5, pady=5)

    def run_simulacao(self):
        msg = self.entry_msg.get()
        if not msg:
            messagebox.showwarning("Aviso", "Digite uma mensagem!")
            return

        config = {
            "enquadramento": self.combo_enq.get(),
            "erro": self.combo_erro.get(),
            "modulacao": self.combo_mod.get(),
            "sigma_ruido": self.scale_ruido.get()
        }

        try:
            resultado = self.simulador.executar_simulacao(msg, config)
            self.ax.clear()
            
            sinal_tx = resultado['sinal_tx']
            sinal_rx = resultado['sinal_rx']
            
            limit = 1000
            if len(sinal_tx) > limit: 
                sinal_tx = sinal_tx[:limit]
                sinal_rx = sinal_rx[:limit]
            
            self.ax.plot(sinal_tx, color='green', linewidth=2, alpha=0.5, label='Transmitido (Tx)')
            self.ax.plot(sinal_rx, color='blue', linewidth=0.8, label='Recebido (Rx)')
            self.ax.set_title(f"Sinal Modulado: Tx vs Rx ({config['modulacao']})")
            self.ax.legend() # <--- IMPORTANTE: Adiciona a legenda para saber quem é quem
            self.ax.grid(True, linestyle='--', alpha=0.6)
            self.canvas.draw()
            self.txt_log.delete("1.0", tk.END)
            self.txt_log.insert(tk.END, f"=== CONFIGURAÇÃO ===\n")
            self.txt_log.insert(tk.END, f"Enquadramento: {config['enquadramento']} | Erro: {config['erro']} | Mod: {config['modulacao']}\n\n")
            
            self.txt_log.insert(tk.END, f"=== RESULTADOS ===\n")
            self.txt_log.insert(tk.END, f"1. Texto Original: {msg}\n")
            self.txt_log.insert(tk.END, f"2. Bits Transmitidos (App): {resultado['bits_tx']}\n")
            self.txt_log.insert(tk.END, f"3. Status Receptor: {resultado['status']}\n")
            self.txt_log.insert(tk.END, f"4. Texto Decodificado: {resultado['texto_final']}\n")
            
            if msg == resultado['texto_final']:
                self.txt_log.insert(tk.END, "\n>> SUCESSO TOTAL: Mensagem chegou íntegra! <<\n")
            else:
                self.txt_log.insert(tk.END, "\n>> FALHA: Mensagem corrompida ou incompleta. <<\n")

        except Exception as e:
            messagebox.showerror("Erro Crítico", f"Falha na simulação:\n{str(e)}")
            print(e)

if __name__ == "__main__":
    root = tk.Tk()
    app = Interface(root)
    root.mainloop()