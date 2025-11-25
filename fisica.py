import numpy as np

# NRZ - Non-Return to Zero
# retorna um sinal onde 1 é representado por +1 e 0 por -1
def nrz(trem):
    sinal = []

    for bit in trem:
        if bit == 1:
            sinal.append(1)
        else:
            sinal.append(-1)
    return sinal

# Manchester
# Faz um XOR entre o bit e o clock
# para sincronização efetiva entre transmissor e receptor
def manchester(trem):
    sinal = []

    for bit in trem:
        if bit == 1:
            sinal.extend([1, -1])
        else:
            sinal.extend([-1, 1])
    return sinal

# Bipolar
# Alterna entre +1 e -1 para bits com valor 1
# bit 0 permanece em 0
def bipolar(trem):
    sinal = []

    ultimo = True
    for bit in trem:
        if bit == 1:
            if ultimo:
                sinal.append(1)
                ultimo = False
            else:
                sinal.append(-1)
                ultimo = True
        else:
            sinal.append(0)
    return sinal

# ASK - Amplitude Shift Keying
# Modula a amplitude com base no trem de bits
# Amplitude será 'amp' para bit 1 e 0 para bit 0
def ask(trem, amp):
    sinal = []
    
    for bit in trem:
        if bit == 1:
            for t in range(100):
                # Usa-se 100 amostras por bit para nossa simulação
                valor = amp * np.sin(2 * np.pi * (t / 100))
                sinal.append(valor)
        else:
            for t in range(100):
                # sinal muito próximo de zero a fim de a decodificação funcionar
                sinal.append(0.001)
    return sinal


# FSK - Frequency Shift Keying
# Modula a frequência com base no trem de bits
# senoide com frequência f1 para bit 1 e f2 para bit 0
def fsk(trem, f1, f2):
    sinal = []

    for bit in trem:
        if bit == 1:
        # Usa-se 100 amostras por bit para nossa simulação
            for t in range(100):
                valor = np.sin(2 * np.pi * f1 * (t / 100))
                sinal.append(valor)
        else:
            for t in range(100):
                valor = np.sin(2 * np.pi * f2 * (t / 100))
                sinal.append(valor)
    return sinal

# QPSK - Quadrature Phase Shift Keying
# Modula a fase com base em pares de bits
def qpsk(trem):
    sinal = []

    fase_map = {
        (0, 0): np.pi/4,
        (0, 1): 3 * np.pi/4,
        (1, 1): 5 * np.pi/4,
        (1, 0): 7 * np.pi/4,}
    
    for i in range(0, len(trem), 2):
        b_pair = (trem[i], trem[i+1])
        fase = fase_map[b_pair]
        for n in range(100):
            # frequência de 1Hz para simplicidade
            # assim comom amplitude de 1
            valor = np.sin( (n/100) +fase)
            sinal.append(valor)
    return sinal

# QAM - Quadrature Amplitude Modulation
# Modula em função tanto da amplitude quanto da fase
def qam16(trem):
    sinal = []
    map = {
        (0,0,0,0): (0.33, 225),
        (0,0,0,1): (0.75, 255),
        (0,0,1,0): (0.75, 195),
        (0,0,1,1): (1.00, 225),
        (0,1,0,0): (0.33, 135),
        (0,1,0,1): (0.75, 105),
        (0,1,1,0): (0.75, 165),
        (0,1,1,1): (1.00, 135),
        (1,0,0,0): (0.33, 315),
        (1,0,0,1): (0.75, 285),
        (1,0,1,0): (0.75, 345),
        (1,0,1,1): (1.00, 315),
        (1,1,0,0): (0.33, 45),
        (1,1,0,1): (0.75, 75),
        (1,1,1,0): (0.75, 15),
        (1,1,1,1): (1.00, 45),
    }

    for i in range(0, len(trem), 4):
        quad = (trem[i], trem[i+1], trem[i+2], trem[i+3])
        amp, fase_deg = map[quad]
        fase = fase_deg * np.pi / 180.0

        for n in range(100):
            valor = amp * np.sin(2 * np.pi * n/100 + fase)
            sinal.append(valor)

    return sinal
