#!/usr/bin/env python3

"""
PyAudio Example: Make a wire between input and output (i.e., record a
few samples and play them back immediately).

This is the callback (non-blocking) version.
"""

import pyaudio
import time
from scipy.signal import butter, lfilter_zi, lfilter
import numpy as np
import struct
import array

WIDTH = 2
CHANNELS = 1
RATE = 44100
LOWCUT = 1000
HIGHCUT = 10000

def design_filter(lowcut, highcut, fs, order=3):
    nyq = 0.5*fs
    low = lowcut/nyq
    high = highcut/nyq
    b,a = butter(order, [low,high], btype='band')
    return b,a

def to_array(block):
    count = len(block)/WIDTH
    format = "%dh"%(count)
    unpacked = struct.unpack(format, block)
# convert to float between -1.0 and 1.0
# int16 is -32768 to 32767.
    norm = list(map(lambda x: float(x) / 32768, unpacked))
    return unpacked

def to_string(block):
    count = len(block)
    return []

p = pyaudio.PyAudio()

# design the filter
b,a = design_filter(LOWCUT, HIGHCUT, RATE, 3)

# compute the initial conditions.
zi = lfilter_zi(b, a)

def callback(in_data, frame_count, time_info, status):
    global zi
#    print(to_array(in_data))
    out_data,zi = lfilter(b, a, to_array(in_data), zi=zi)
    #to_string(out_data)
    return (in_data, pyaudio.paContinue)

stream = p.open(format=pyaudio.get_format_from_width(WIDTH),
                channels=CHANNELS,
                rate=RATE,
                input=True,
                output=True,
                stream_callback=callback)

stream.start_stream()

while stream.is_active():
    time.sleep(0.1)

stream.stop_stream()
stream.close()

p.terminate()
