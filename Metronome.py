import midi_tools as mt
import itertools
import time
import mido

class BeatCycle:
    def __init__(self, first_downbeat, beat_step):
        self.beat_print = ['beat <---- first', 'beat', 'beat', 'beat']
        self.beat_i = itertools.cycle(range(4))
        self.next_beat = first_downbeat
        self.beat_step = beat_step
        self.which_beat = next(self.beat_i)

    def __iter__(self):
        return self

    def next(self):
        self.which_beat = next(self.beat_i)
        self.next_beat = self.next_beat + self.beat_step

    def __str__(self):
        return self.beat_print[self.which_beat]

class Metronome:
    def __init__(self, first_downbeat, beat_step, out_port = None, note = 57):
        self.note = note
        self.beat = BeatCycle(first_downbeat, beat_step)
        self.catchup_first()
        self.out_port = out_port
        if out_port:
            self.clock_step = beat_step/24
            self.next_clock = self.beat.next_beat

            self.out_port.send(mt.stop)
            while time.time()<self.beat.next_beat:
                time.sleep(0.00001)
            self.out_port.send(mt.start)
    
    def catchup_first(self):
        while time.time()>self.beat.next_beat or \
              not (self.beat.which_beat == 0):
            self.beat.next()

    def update_metronome(self, new_beat_step, new_downbeat):

        self.beat = BeatCycle(new_downbeat, new_beat_step)
        while time.time()>self.beat.next_beat:
            self.beat.next()
    
    def play(self):
        
        if time.time()>self.beat.next_beat:
            print(self.beat )
            self.beat.next()

            # if self.beat.which_beat == 0:
            #     self.out_port.send(mt.stop)
            #     self.out_port.send(mt.start)


        # if self.out_port:
        #     if time.time()>self.next_clock:
        #         self.out_port.send(mt.clock)
        #         self.next_clock = self.next_clock + self.clock_step
