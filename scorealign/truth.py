import csv
import numpy as np
import path

class Event:
    def __init__(self, onset, offset, pitch):
        self.onset = onset
        self.offset = offset
        self.pitch = pitch
        self.on_used = False
        self.off_used = False

class Truth:
    def __init__(self, filename, score, audio):
        self.path = []
        with open(filename, 'rb') as truth:
            for s in truth:
                self.path.append(int(s))
    def get_path(self):
        return self.path

class TruthTxt:
    def __init__(self, filename, score, audio):
        with open(filename, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter="\t", quoting=csv.QUOTE_NONE)
            
            self.events = []
            for row in reader:
                if row[0] == "OnsetTime": continue
                self.events.append(Event(float(row[0]),float(row[1]),int(row[2])))
                
            self.length = audio.length()
            self.frame_duration = audio.frame_duration()
            self.frame_count = audio.frame_count()
            self.score = score
            
    def get_path(self):
        truth_path = []
        curstate = 0
        costs = np.zeros((self.frame_count, self.score.state_count()))

        for t in range(0, self.frame_count):
            notes = self.get_notes(t*self.frame_duration)
            for i in range(0, self.score.state_count()):
                state_notes = self.score.states[i].notes
                if notes == state_notes:
                    costs[t,i] = 10
                else:
                    costs[t, i] =  1-float(len(notes.intersection(state_notes))) / len(notes.union(state_notes))
        
        truth_path = path.factory("dtw").calculate(costs, self.score)
        return truth_path
    
    def get_notes(self, t):
        notes = set()
        for event in self.events:
            if event.onset <= t and t < event.offset:
                notes.add(event.pitch)
            if event.onset > t and event.offset > t:
                break
        return notes
