import pyaudio
import numpy as np
import madmom
import time
import midi_tools as mt
import sys
from Metronome import Metronome
import MetronomeAudio as ma

'''
This script records audio using pyaudio then analyses it using the MetronomeAudio module
It then prints a beat counter which prints beats in time to the playing audio

It is intended to work on music with a fixed bpm 
such as electronic dance music or pop music
'''

out_ports = mt.user_midi_output(2)
out_port = out_ports.values()[0]

default_chunksize   = 8192
default_format      = pyaudio.paInt16
default_channels    = 1
default_samplerate  = 44100
record_seconds = 5

print("start")
audio = pyaudio.PyAudio()

data_full = []
out_port.send(mt.stop)

print("recording")

stream = audio.open(
    # input_device_index = 2, # use this to select other input devices
    format=default_format,
    channels=default_channels,
    rate=default_samplerate,
    input=True,
    frames_per_buffer=default_chunksize,
)
data = stream.read(default_chunksize)
first_time = time.time()
nums = np.fromstring(data, np.int16)
data_full.extend(nums)
for i in range(1, int(default_samplerate / default_chunksize
                        * record_seconds)):
    data = stream.read(default_chunksize)
    nums = np.fromstring(data, np.int16)
    data_full.extend(nums)


stream.stop_stream()
stream.close()

# this is how we estimate the start time of the audio stream
start_time = first_time  - float(default_chunksize)/default_samplerate

print("finished recording")

data_full = np.array(data_full)
time_process = time.time()

# process the audio to generate features
beats, when_beats, beat_step, first_downbeat = ma.process_audio(start_time, data_full)

# find key
# key = madmom.features.key.CNNKeyRecognitionProcessor()(data_full)
# is_key = np.argmax(key)
# maj_min = is_key / 12
# note = 57 + is_key % 12
# print(note)


metronome = Metronome(first_downbeat- 0.04, beat_step , out_port, note = note) 
# first_downbeat-0.04 seems to keep it synced better 
# TODO - figure out how to calibrate this

try:
    while 1:
        metronome.play()
        time.sleep(0.000001)
except KeyboardInterrupt:
    #out_port.send(mt.stop)
    sys.exit()
