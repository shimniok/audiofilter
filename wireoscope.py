#!/usr/bin/env python3

"""
PyAudio Example: Make a wire between input and output (i.e., record a
few samples and play them back immediately).

This is the callback (non-blocking) version.
"""

from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import pyaudio
import time
from scipy.signal import butter, lfilter_zi, lfilter
import numpy as np
import matplotlib.pyplot as plt
import struct
import array

WIDTH = 2
MAXINT = 32767
CHANNELS = 1
RATE = 44100
BPH = 18000
SAMPLES = RATE
LOWCUT = 1000.0
HIGHCUT = 8000.0

data = list([0]*SAMPLES)
print(data)
count = 0

app = QtGui.QApplication([])

win = pg.GraphicsWindow(title="Python Oscilloscope")
win.resize(1000,600)
win.setWindowTitle('Python Oscilloscope')

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

p6 = win.addPlot(title="Updating plot")
p6.setYRange(-1,1)
p6.setXRange(0,SAMPLES)
p6.showGrid(x=True, y=True)
p6.getViewBox().disableAutoRange()

curve = p6.plot(pen='y')

def update():
    global curve, p6, data
    curve.setData(data[:SAMPLES])

def design_filter(lowcut, highcut, fs, order=3):
    nyq = 0.5*fs
    low = lowcut/nyq
    high = highcut/nyq
    b,a = butter(order, [low,high], btype='band')
    return b,a

def to_floats(block):
    count = len(block)/WIDTH
    format = "@%dh"%(count)
    unpacked = struct.unpack(format, block)
    # convert to float between -1.0 and 1.0
    # int16 is -32768 to 32767.
    norm = list(map(lambda x: float(x) / MAXINT, unpacked))
    return norm

def to_string(block):
    count = len(block)
    format = "@%dh"%(count)
    ints = list(map(lambda x: int(x * MAXINT), block))
    packed = struct.pack(format, *ints)
    return packed

p = pyaudio.PyAudio()

# design the filter
b,a = design_filter(LOWCUT, HIGHCUT, RATE, 3)

# compute the initial conditions.
zi = lfilter_zi(b, a)

def callback(in_data, frame_count, time_info, status):
    global zi, data, count

    #out_data,zi = lfilter(b, a, to_floats(in_data), zi=zi)
    out_data = to_floats(in_data)

    print(count)

    if count >= SAMPLES:
        count = 0
    data[count:count+1024] = out_data
    count += 1024
    update()

    #out_data = list(map(lambda x: x * 0.1, out_data))

    s = to_string(out_data)

    return (s, pyaudio.paContinue)

stream = p.open(format=pyaudio.get_format_from_width(WIDTH),
                channels=CHANNELS,
                rate=RATE,
                input=True,
                output=True,
                stream_callback=callback)

stream.start_stream()

def closeEvent():
    stream.stop_stream()
    stream.close()
    p.terminate()


## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
