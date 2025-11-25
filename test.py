from decode_fis import qam16_decode
from fisica import qam16


bits = [0,0,0,1,  1,0,0,1,  0,1,0,1,  0,0,1,0]
sinal = qam16(bits)
rec = qam16_decode(sinal)

print(bits)
print(rec)
