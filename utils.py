from bitarray import bitarray
import numpy as np
import struct

di = {
    '0000': '11110', '0001': '01001', '0010': '10100', '0011': '10101', '0100': '01010', '0101': '01011',
    '0110': '01110', '0111': '01111', '1000': '10010', '1001': '10011', '1010': '10110', '1011': '10111',
    '1100': '11010', '1101': '11011', '1110': '11100', '1111': '11101'
}

crcDiv = bitarray('100000100110000010001110110110111')

amplitude = 0.1
framerate = 44000

length = 0.1
freq1 = 440
freq2 = 880

points = np.round(framerate * length)

tone1 = np.sin(np.arange(points) / points * 2 * np.pi * freq1 * length)
tone2 = np.sin(np.arange(points) / points * 2 * np.pi * freq2 * length)

zero = b''.join([struct.pack('h', int(e * (2 ** 15) * amplitude)) for e in np.array(tone1)])
one = b''.join([struct.pack('h', int(e * (2 ** 15) * amplitude)) for e in np.array(tone2)])


def deg(x):
    y = len(x)
    for j in range(len(x)):
        if not x[j]:
            y = y - 1
        else:
            break
    return y - 1


def removeZeros(x):
    while not x[0]:
        x.remove('')
        if len(x) == 0:
            break
    return x


def divide(x, y):
    temp = bitarray()
    res = bitarray()
    for i in range(len(x)):
        temp.append(x[i])
        if deg(temp) < deg(y):
            res.append(0)
        else:
            res.append(1)
            temp = temp[len(temp) - deg(temp)::] ^ y[len(y) - deg(y)::]
    return removeZeros(res), removeZeros(temp)


def crc32(x):
    y = x + 32 * '0'
    temp = divide(y, crcDiv)[1]
    while len(temp) < 32:
        temp = bitarray('0') + temp
    return temp
