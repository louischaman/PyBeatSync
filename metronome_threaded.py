import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import madmom
import collections
import time
import itertools
import midi_tools as mt
import sys
import scipy
from Metronome import Metronome
import MetronomeAudio as ma
import threading
import Queue

out_ports = mt.user_midi_output(2)
out_port = out_ports.values()[0]

default_chunksize   = 8192
default_format      = pyaudio.paInt16
default_channels    = 1
default_samplerate  = 44100

print("start")
audio = pyaudio.PyAudio()

seconds = 5

out_port.send(mt.stop)

print("recording")
stream = audio.open(
    # input_device_index = 2,
    format=default_format,
    channels=default_channels,
    rate=default_samplerate,
    input=True,
    frames_per_buffer=default_chunksize,
)



class Thread_record(threading.Thread):
    def __init__(self, audio_stream, data_to_process, 
                 sample_rate, chunksize, 
                 seconds_record, seconds_process, max_size):
        threading.Thread.__init__(self)
        self.data_full = collections.deque(maxlen=sample_rate * max_size)
        self.data_to_process = data_to_process

        self.sample_rate = sample_rate
        self.chunksize = chunksize
        self.seconds_record = seconds_record
        self.seconds_process = seconds_process
        self.max_size = max_size


        self.n_chunks_process = (self.sample_rate * self.seconds_process) / self.chunksize 
        self.n_samples_process = self.n_chunks_process * self.chunksize
        print(float(self.n_samples_process)/ sample_rate)

    def run(self):

        to_process = []
        samples_records = 0

        data = stream.read(default_chunksize)
        samples_records = samples_records +  default_chunksize

        start_time = time.time() - float(self.chunksize)/self.sample_rate
        nums = np.fromstring(data, np.int16)
        self.data_full.extend(nums)
        to_process.extend(nums)

        for i in range(1, int(default_samplerate / default_chunksize
                                * self.seconds_record)):
            data = stream.read(default_chunksize)
            samples_records = samples_records +  default_chunksize

            start_sample = max(0, samples_records - self.n_samples_process)

            # print("chunk")

            nums = np.fromstring(data, np.int16)
            self.data_full.extend(nums)
            to_process.extend(nums)
            if len(to_process) == self.n_samples_process:

                print("start sample", start_sample)
                # time when chunk starts
                time_chunk_start = start_time + float(start_sample)/self.sample_rate
                # self.data_to_process.put( (time_chunk_start, np.array(to_process) ) )
                self.data_to_process.put( ( start_time - 0.03, np.array(to_process) ) )
                to_process = []
                data = stream.read(default_chunksize)
                first_time = time.time()
                print(first_time - start_time)
                start_time = first_time- float(self.chunksize)/self.sample_rate
                samples_records = samples_records +  default_chunksize

                nums = np.fromstring(data, np.int16)
                self.data_full.extend(nums)
                to_process.extend(nums)

        # start_time = time.time()

        # for i_chunks_recorded in range(0, int(self.sample_rate / self.chunksize
        #                         * self.seconds_record)):
        #     data = stream.read(default_chunksize)
        #     samples_records = samples_records +  default_chunksize
        #     start_sample = max(0, samples_records - self.sample_rate * self.max_size)
        #     nums = np.fromstring(data, np.int16)
        #     self.data_full.extend(nums)
        #     to_process.extend(nums)
        #     if len(to_process) == self.n_samples_process:
        #         # time when chunk starts
        #         time_chunk_start = start_time + float(start_sample)/self.sample_rate
        #         # self.data_to_process.put( (time_chunk_start, np.array(to_process) ) )
        #         self.data_to_process.put(( start_time - 0.03, np.array(list(self.data_full))))
        #         to_process = []



class Thread_process(threading.Thread):
    def __init__(self, data_to_process, processed_data):
        threading.Thread.__init__(self)
        self.data_to_process = data_to_process
        self.processed_data = processed_data

    def run(self):
        while 1:
            chunk_start, data_got = self.data_to_process.get()
            print("length_sample", float(len(data_got))/default_samplerate)
            processed_data = ma.process_audio(chunk_start, data_got)
            self.processed_data.put(processed_data)



class Thread_metronome(threading.Thread):
    def __init__(self, processed_data, out_port = None):
        threading.Thread.__init__(self)
        self.processed_data = processed_data

    def run(self):
        beats, when_beats, beat_step, first_downbeat = self.processed_data.get()
        metronome = Metronome(first_downbeat, beat_step, out_port)
        beats_full = collections.deque(maxlen=60*411)

        print("bpm = ", 60/beat_step)
        # try:
        while 1:
            if not self.processed_data.empty():
                beats, when_beats, beat_step, first_downbeat = self.processed_data.get()

                # print(time.time() - first_downbeat)
                # beats_full.extend(list(beats))
                # when_beats = madmom.features.beats.BeatDetectionProcessor(fps=100)(np.array(beats_full))
                # beat_step = np.mean(np.diff(when_beats))
                print("bpm = ", 60/beat_step)
                metronome = Metronome(first_downbeat, beat_step, out_port)
            else:
                metronome.play()
                time.sleep(0.000001)
        # except :
        #     out_port.send(mt.stop)
        #     sys.exit()


            

audio_data_to_process = Queue.Queue()
processed_data = Queue.Queue()
thread_record = Thread_record(stream, audio_data_to_process, 
                        default_samplerate, default_chunksize, 60*10,10, max_size = 20)
thread_process = Thread_process(audio_data_to_process, processed_data)
metronome_process = Thread_metronome(processed_data, out_port = out_port)

thread_record.start()
thread_process.start()
metronome_process.start()
thread_record.join()


# for i in range(0, int(default_samplerate / default_chunksize
#                         * seconds)):
#     data = stream.read(default_chunksize)
#     nums = np.fromstring(data, np.int16)
#     data_full.extend(nums)

# stream.stop_stream()
# stream.close()

# print("finished recording")

# data_full = np.array(data_full)
# time_process = time.time()

# beats, when_beats, beat_step, first_downbeat = ma.process_audio(start_time, data_full)

# print("process takes: ", time.time()-time_process)

# metronome = Metronome(first_downbeat, beat_step, out_port)

# try:
#     while 1:
#         metronome.play()
#         time.sleep(0.000001)
# except KeyboardInterrupt:
#     out_port.send(mt.stop)
#     sys.exit()



# # when_beats_rev = when_beats[::-1]

# # beats = when_beats
# # follow = np.divide(60,np.divide(np.cumsum(np.diff(beats)[::-1]),np.arange(1,len(beats))))
# # np.mean(follow[len(follow)/2:])