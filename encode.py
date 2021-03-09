import struct
import wave

from utils import *
import pyaudio as pa
from bitarray import bitarray


def nrzi4b5b(x):
    temp = bitarray()
    for i in range(int(len(x) / 4)):
        temp = temp + bitarray(di[str(x[4 * i:4 * i + 4:])[10:14:]])
    res = bitarray('1')
    for i in range(len(temp)):
        if temp[i]:
            res.append(1 - res[i])
        else:
            res.append(res[i])
    res.remove('1')
    return res


def speaker(bits, filename):
    wf = wave.open(filename, 'wb')
    wf.setnchannels(1)
    wf.setframerate(framerate)
    wf.setsampwidth(pa.get_sample_size(pa.paInt16))
    frames = []
    for i in range(len(bits)):
        if bits[i]:
            frames.append(one)
        else:
            frames.append(zero)
    wf.writeframes(b''.join(frames))
    wf.close()


def encode(src, dst, msg, filename):
    src = struct.pack('!LH', src // (2 ** 15), src % (2 ** 15))
    dst = struct.pack('!LH', dst // (2 ** 15), dst % (2 ** 15))
    if isinstance(msg, str):
        msg = bytes(msg, 'utf8')
    else:
        msg = struct.pack('!H', msg)
    msgLen = struct.pack('!H', len(msg))
    tempFrame = dst + src + msgLen + msg
    frame = bitarray()
    frame.frombytes(tempFrame)
    frame = frame + crc32(frame)
    preamble = bitarray(7 * '10101010' + '10101011')
    bits = preamble + nrzi4b5b(frame)
    speaker(bits, filename)


def run():
    print("src:")
    src = int(input())
    print("dst:")
    dst = int(input())
    print("message:")
    msg = str(input())
    print("file name:")
    filename = str(input())
    encode(src, dst, msg, filename)


run()
