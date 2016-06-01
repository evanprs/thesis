#!/opt/local/bin/python2.7

import math
import pyaudio
import numpy as np


def sine(frequency, length, rate):
    length = int(length * rate)
    factor = float(frequency) * (math.pi * 2) / rate
    return np.sin(np.arange(length) * factor)


def play_tone(stream, frequencies=[440,880], length=1, rate=44100):
    chunks = []
    data = sum([sine(f, length, rate) for f in frequencies])
    chunks.append(data)
    chunk = np.concatenate(chunks) * 0.25

    stream.write(chunk.astype(np.float32).tostring())



if __name__ == '__main__':
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32,
                    channels=1, rate=44100, output=1)
    play_tone(stream,frequencies=np.array([.5,1,2,3,4,5])*400)
    stream.close()
    p.terminate()
    