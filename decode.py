import pyaudio
from utils import *
from bitarray import bitarray

CHUNK = int(framerate*length)
inv_di = {v: k for k, v in di.items()}

delta = 100

isId = False
idFreq1 = -1
idFreq2 = -1


def zeroOrOne(data):
    data = struct.unpack('{n}h'.format(n=CHUNK), data)
    data = np.array(data)

    T = np.fft.fft(data)
    freq = np.fft.fftfreq(len(T))

    imax = np.argmax(np.abs(T))
    freq = freq[imax]
    freqInHertz = abs(freq * framerate)
    #print(freqInHertz)
    if freq1 - delta <= freqInHertz <= freq1 + delta:
        return '0'
    elif freq2 - delta <= freqInHertz <= freq2 + delta:
        return '1'
    else:
        return None


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


def check(data):
    global isId, idFreq1, idFreq2
    data = struct.unpack('{n}h'.format(n=CHUNK), data)
    data = np.array(data)

    T = np.fft.fft(data)
    freq = np.fft.fftfreq(len(T))

    if not isId:
        isId = True
        for imax in range(len(freq)):
            if abs(freq[imax] * framerate) == freq1:
                idFreq1 = imax
            if abs(freq[imax] * framerate) == freq2:
                idFreq2 = imax
            if idFreq1 != -1 and idFreq2 != -1:
                break

    imax = np.argmax(np.abs(T))
    #print(np.abs(w[idFreq1]), np.abs(w[idFreq2]), i)
    return max(np.abs(T[idFreq1]), np.abs(T[idFreq2])) / min(np.abs(T[idFreq1]), np.abs(T[idFreq2])), imax


def argMax(results):
    k = 0
    idx = 0
    for i in range(len(results)):
        if k < results[i][0]:
            idx = i
        k = max(k, results[i][0])
    return idx


def checkAll(results):
    for i in range(10):
        if results[i][1] != idFreq1 and results[i][1] != idFreq2:
            return True
    return False


def record():
    b = bitarray()
    pa = pyaudio.PyAudio()

    stream = pa.open(
        input=True,
        channels=1,
        rate=44000,
        format=pyaudio.paInt16,
        frames_per_buffer=CHUNK,
    )

    frames = []
    results = []
    i = 0

    chunk = int(CHUNK/10)
    while True:
        data = stream.read(chunk)
        frames.append(data)
        if i >= 10:
            frames.pop(0)
            results.append(check(b''.join(frames)))
            if i >= 20:
                results.pop(0)
                if checkAll(results):
                    i = i+1
                    continue
                imax = argMax(results)
                stream.read(chunk*(imax+1))
                while data := stream.read(CHUNK):
                    res = zeroOrOne(data)
                    #print(res)
                    if res is None:
                        break
                    b = b + res
                break
        i = i+1

    stream.stop_stream()
    stream.close()
    pa.terminate()
    return b


def cutPreamble(b):
    for i in range(len(b)):
        if b[i] == b[i+1]:
            return b[i+1::]


def decode():
    b = record()
    b = cutPreamble(b)
    #print(b)
    msgLen = b[0:141:]
    msgLen = reverseNrzi4b5b(msgLen)
    msgLen = msgLen[96:112:]
    msgLen = 8 * struct.unpack("!H", msgLen)[0]
    #print(b[0:int((144+msgLen)*5/4)+1:])
    #print(msgLen)
    frame = reverseNrzi4b5b(b[0:int((144+msgLen)*5/4)+1:])
    crc = frame[112+msgLen:144+msgLen:]
    frame = frame[0:112+msgLen:]
    if crc32(frame) != crc:
        print(":(((")
        return None

    dst = frame[0:48:]
    src = frame[48:96:]
    frame = frame[112::]
    dstStruct = struct.unpack("!LH", dst)
    srcStruct = struct.unpack("!LH", src)
    return srcStruct[0]*(2**15)+srcStruct[1], dstStruct[0]*(2**15)+dstStruct[1], frame.tobytes().decode('utf8')


def listen():
    while True:
        try:
            print(decode())
        except:
            print("Error")


listen()
