import madmom
import numpy as np
import scipy.stats
import time
import math

debug = True
round_on = True

def process_audio(start_time, audio_data):
    start_process = time.time()
    beats = madmom.features.beats.RNNBeatProcessor()(audio_data)
    when_beats = madmom.features.beats.BeatTrackingProcessor(fps=100)(beats)
    # sig = madmom.audio.signal.Signal(audio_data, sample_rate=44100)
    # downbeat_prob = madmom.features.downbeats.RNNBarProcessor()((sig, when_beats))
    # downbeat_prob = downbeat_prob[:-1]
    # downbeat_prob_sub = downbeat_prob[:4 * int( len(downbeat_prob)/4 )]
    # summed_downbeats = np.sum(np.reshape(downbeat_prob_sub[:,1],(-1,4)),axis = 0)
    beat_intervals = np.diff(when_beats)

    when_beats2 = when_beats[1:]
    m_res = scipy.stats.linregress(np.arange(len(when_beats)),when_beats)
    m_res2 = scipy.stats.linregress(np.arange(len(when_beats2)),when_beats2)

    # first_downbeat = start_time + downbeat_prob[np.argmax(summed_downbeats),0]
    first_downbeat2 = start_time + m_res.intercept 

    beat_step3 = m_res2.slope
    beat_step2 = m_res.slope
    beat_step1 = (np.mean(np.diff(when_beats[len(when_beats)/2:])))
    beat_step = np.mean(np.diff(when_beats[1:]))


    if debug:
        print("processing takes: {}".format(time.time()- start_process) )
        print("bpm",60/beat_step, 60/beat_step1, 60/beat_step2, 60/beat_step3)

    if round_on and ( abs( 60/beat_step2 - round(60/beat_step2) )<0.1 ):
        bpm = round(60/beat_step2)
        print("rounding to ", bpm)
        final_beatstep = 60/bpm
    else:
        final_beatstep = beat_step2
    # beats = when_beats
    # beat_intervals_rounded = np.round(beat_intervals,5)
    # (values,counts) = np.unique(beat_intervals_rounded,return_counts=True)
    # follow = np.divide(np.cumsum(np.diff(when_beats)),np.arange(1,len(when_beats)))
    # lm_res = scipy.stats.linregress(np.arange(len(when_beats)),when_beats)
    # avg_interval = np.mean(beat_intervals)
    # beat_step = (lm_res.slope +avg_interval)/2

    # print("bpm = {}".format( 60/beat_step))
    return beats, when_beats, final_beatstep, first_downbeat2
