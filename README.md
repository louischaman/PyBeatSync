# AutoClock

A python project that uses the madmom audio and music analysis library to cary out beat detection from a live audio stream and generate a syncronised beat response.

Uses python 2.7

install requirements with

```
pip install -r requirements.txt
```

run with

```
python metronome_basic.py
```

also working on a multi threaded version where the audio stream is running constantly and the metronome adjusts every 10s

to run this 

```
python metronome_threaded.py
```
