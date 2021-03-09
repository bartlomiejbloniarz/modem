import wave
from utils import *
from bitarray import bitarray

CHUNK = int(framerate*length)
inv_di = {v: k for k, v in di.items()}


def zeroOrOne(data):
    data = struct.unpack('{n}h'.format(n=CHUNK), data)
    data = np.array(data)

    T = np.fft.fft(data)
    freq = np.fft.fftfreq(len(T))

    imax = np.argmax(np.abs(T))
    #print(np.abs(w[44]), np.abs(w[88]), i)
    freq = freq[imax]
    freqInHertz = abs(freq * framerate)
    #print(freqInHertz)
    if freqInHertz == freq1:
        return '0'
    else:
        return '1'


def reverseNrzi4b5b(x):
    temp = bitarray()
    for i in range(1, len(x)):
        if x[i] == x[i-1]:
            temp = temp + '0'
        else:
            temp = temp + '1'
    res = bitarray()
    for i in range(int(len(temp) / 5)):
        res = res + bitarray(inv_di[str(temp[5 * i:5 * i + 5:])[10:15:]])
    return res


def decode(fileName):
    wf = wave.open(fileName, 'rb')
    b = bitarray()
    while True:
        data = wf.readframes(CHUNK)
        if data:
            b = b + zeroOrOne(data)
        else:
            break
    print(b[63::])
    frame = reverseNrzi4b5b(b[63::])
    crc = frame[len(frame)-32:len(frame):]
    frame = frame[0:len(frame)-32:]
    if crc32(frame) != crc:
        return None

    dst = frame[0:48:]
    src = frame[48:96:]
    msgLen = frame[96:112:]
    msgLen = 8 * struct.unpack("!H", msgLen)[0]
    print(msgLen)
    frame = frame[112::]
    dstStruct = struct.unpack("!LH", dst)
    srcStruct = struct.unpack("!LH", src)
    return srcStruct[0]*(2**15)+srcStruct[1], dstStruct[0]*(2**15)+dstStruct[1], frame.tobytes().decode('utf8')


print("filename:")
a = input()
try:
    print(decode(a))
except:
    print("Error")
