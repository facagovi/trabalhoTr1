from bitarray import bitarray # type: ignore
import numpy as np

def nrz_decode(sinal):
    trem = []
    for volt in sinal:
        if volt == 1:
            trem.append(1)
        else:
            trem.append(0)
    return trem

def manchester_decode(sinal):
    trem = []
    for i in range(0, len(sinal), 2):
        if sinal[i] == 1 and sinal[i+1] == -1:
            trem.append(1)
        else:
            trem.append(0)
    return trem

def bipolar_decode(sinal):
    trem = []
    for volt in sinal:
        if volt == 0:
            trem.append(0)
        else:
            trem.append(1)
    return trem

def ask_decode(sinal, amp):
    trem = []

    for i in range(0, len(sinal), 100):
        segmento = sinal[i:i+100]

        # limite de ruído escolhido como metade da amplitude
        if any(abs(valor) > amp / 2 for valor in segmento):
            trem.append(1)
        else:
            trem.append(0)

    return trem

def fsk_decode(sinal, f1, f2):
    trem = []

    for i in range(0, len(sinal), 100):
        segmento = sinal[i:i+100]
        erro1 = 0
        erro2 = 0

        for t, amostra in enumerate(segmento):
            # recria ondas do encoder para calcular o erro
            ref1 = np.sin(2 * np.pi * f1 * (t / 100))
            ref2 = np.sin(2 * np.pi * f2 * (t / 100))
            erro1 += abs(amostra - ref1)
            erro2 += abs(amostra - ref2)

        if erro1 < erro2:
            trem.append(1)
        else:
            trem.append(0)

    return trem


def qpsk_decode(sinal):
    trem = []
    # mapeamentos de dibits
    map = {
        (0, 0): np.pi/4,
        (0, 1): 3 * np.pi/4,
        (1, 1): 5 * np.pi/4,
        (1, 0): 7 * np.pi/4,
    }

    for i in range(0, len(sinal), 100):
        segmento = sinal[i:i+100]
        melhor_par = None
        melhor_erro = None

        for bits, fase in map.items():
            erro = 0
            for t, amostra in enumerate(segmento):
                ref = np.sin((t / 100) + fase)
                erro += abs(amostra - ref)

            if (melhor_erro == None) or (erro < melhor_erro):
                melhor_erro = erro
                melhor_par = bits

        trem.extend([melhor_par[0], melhor_par[1]])

    return trem

def qam16_decode(sinal):
    trem = []
    # mapeamentod e quadribits
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

    for i in range(0, len(sinal), 100):
        segmento = sinal[i:i+100]
        melhor_quad = None
        menor_erro = None

        for quad, (amp, fase_deg) in map.items():
            fase = fase_deg * np.pi / 180.0
            erro = 0

            for n, amostra in enumerate(segmento):
                ref = amp * np.sin(2 * np.pi * n/100 + fase)
                erro += abs(amostra - ref)

            if (menor_erro is None) or (erro < menor_erro):
                menor_erro = erro
                melhor_quad = quad
        trem.extend(list(melhor_quad))

    return trem

