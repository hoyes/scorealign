from music21 import *
import scipy as sp
import logging

class State:
    def __init__(self):
        self.midi_duration = 0.125
        self.duration = 0.125
        self.notes = set()
    def add_note(self, note):
        self.notes.add(note)
        #self.notes.sort()
        return self
    def merge_in(self, state):
        self.notes.update(state.notes)
        self.duration += state.duration
        self.midi_duration += state.midi_duration

class Score:
    def __init__(self, filename, audio_length = None, length = None):
        self.states = []

        self.filename = filename
        score = converter.parseFile(filename)

        total_length = score.duration.quarterLength * 8
        if not length is None:
            if total_length > length * 16: total_length = length * 16

        matrix = sp.zeros((total_length, 128))
        for i in range(0, int(score.duration.quarterLength * 8)+1):
	        self.states.append(State())

        for n in score.flat.notes:
            for s in range(int(n.offset*8)+1, int((n.offset+n.quarterLength)*8)+1):
                if s < len(self.states):
                    if n.isNote:
		                self.states[s].add_note(n.midi)
                    elif n.isChord:
                        for pitch in n.pitches:
                            self.states[s].add_note(pitch.midi)
		
        #Collapse adjacent identical states
        i=0
        while i < len(self.states) - 1:
	        if self.states[i].notes == self.states[i+1].notes:
		        self.states[i].midi_duration += self.states[i+1].midi_duration
		        self.states[i].duration += self.states[i+1].duration
		        self.states.pop(i+1)
	        else:
		        i+=1
		                
        i=0
        pos=0.0
        midi_pos=0
        for (start, end, m) in score.flat.metronomeMarkBoundaries():
	        while i < len(self.states) and midi_pos < end:
		        midi_pos += self.states[i].midi_duration
		        time = m.durationToSeconds(self.states[i].midi_duration)
		        self.states[i].duration = time
		        pos += time
		        i += 1
        
        if not audio_length is None:
            self.resize(audio_length)
        #self.set_minimum_duration(0.05)
        
        if len(self.states[len(self.states)-1].notes) == 0:
            self.states.pop()
            
        self.score = score

    def state_count(self):
        return len(self.states)
    def duration(self):
        return sum(s.duration for s in self.states)
    def resize(self, length):
            multiplier = length / float(self.duration())
            for s in self.states:
                s.duration *= multiplier
    def stateMatrix(self, rate = 10.7666, show_now = True):
            data = np.zeros(self.duration() * rate)
            pos = 0.0
            state = 0
            for s in self.states:
                    next = pos + s.duration * rate
                    for i in range(int(pos), int(next)):
                            data[i] = state
                    state += 1
                    pos = next
            times = np.arange(0, len(data)) / rate
            plot(times, data)
            if show_now: show()
    def length(self):
        return sum(s.midi_duration for s in self.states)
    def note_range(self):
        pitches = self.score.pitches
        min_note = 108
        max_note = 21
        for pitch in pitches:
            if pitch.midi < min_note:
                min_note = pitch.midi
            if pitch.midi > max_note:
                max_note = pitch.midi
        return (min_note, max_note)
    def set_minimum_duration(self, min_duration):
        i = 0
        while i < self.state_count() - 1:
            if self.states[i].duration < min_duration:
                self.states[i].merge_in(self.states[i+1])
                self.states.pop(i+1)
            else:
                i += 1
    def events(self):
        events = []
        offset = 0.0
        for s in self.states:
            events.append({'notes': list(s.notes), 'start': offset, 'duration': s.midi_duration})
            offset += s.midi_duration
        return events
