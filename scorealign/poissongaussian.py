import numpy as np
import audio
import miditools
import logging

miu_c = 0.001
rho = 0.8
num_harmonics = 20
B = 0.00062

class GaussianFactoryClass:
    def __init__(self):
        self.cache = {}
    def get(self, notes):
        if not self.cache.has_key(tuple(notes)):
            logging.log("Generating model for " + str(notes))
            self.cache[tuple(notes)] = GaussianModel(notes)
        return self.cache[tuple(notes)]

GaussianFactory = GaussianFactoryClass()

class NoteGaussianFactoryClass:
    def __init__(self):
        self.cache = {}
    def get(self, note):
        if not self.cache.has_key(note):
            logging.log("Generating model for " + str(note))
            self.cache[note] = GaussianModel([note], one_note = True)
        return self.cache[note]
NoteGaussianFactory = NoteGaussianFactoryClass()


class GaussianModel:
    def __init__(self, notes, one_note = False):
        self.data = np.zeros(audio.num_bins)
        for k in range(0, len(self.data)):
            if not one_note: self.data[k] = miu_c
            for note in notes:
                if one_note:
                   self.data[k] = self.note_gaussian(note, k)
                else: 
                   g = NoteGaussianFactory.get(note)
                   self.data[k] += g.data[k]
    def note_gaussian(self, note, k):
        total = 0.0
        for h in range(1, num_harmonics+1):
                if abs(self.ktofreq(k) - self.harmonic(note, h)) > 50: continue
                miu2 = np.power(h, 2*rho)
                factor = 1 / (np.sqrt(2*np.pi*miu2) )
                exp =  np.exp( - pow(self.ktofreq(k) - self.harmonic(note, h) , 2) / ( 2 * miu2) )
                total +=  factor * exp
        return total
    def ktofreq(self, k):
        return k * (audio.sample_rate / audio.nsamples / 8)
    def harmonic(self, note, h):
        return miditools.fundamental(note) * h * np.sqrt(1 + B * h * h)
