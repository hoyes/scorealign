import factory
import abc
import poissongaussian
import numpy as np
import logging

class LikelihoodProcessor:
    @abc.abstractmethod
    def calculate(self, fft, state, is_rest):
        """Takes a fft frame and a state and calculates a cost, which is
        greatest when the two are a perfect match"""
        return
    def post_process(self, costs):
        pass
        
class PoissonLikelihoodProcessor(LikelihoodProcessor):
    def calculate(self, fft, state, is_rest):
        l = 0.0
        peaks = fft.peaks_bool()
        model = poissongaussian.GaussianFactory.get(state.notes)
        num = 0
        for k in range(0, len(fft.data)):
            if peaks[k] == 1.0:
                l += np.log(1 - np.exp(-model.data[k]))
                num += 1
            else:
                l += -model.data[k]
        return -l
    
class SpectragramLikelihoodProcessor(LikelihoodProcessor):
    def calculate(self, fft, state, is_rest):
        semitones = fft.semitone_bins()
        audio_spect = np.zeros(12)
        for i in range(0, len(semitones)): audio_spect[i % 12] += semitones[i]
        norm = np.linalg.norm(audio_spect)
        if norm > 0: audio_spect /= norm

        
        midi_spect = np.zeros(12)
        for note in state.notes: midi_spect[note % 12] += 1
        norm = np.linalg.norm(midi_spect)
        if norm > 0: midi_spect /= norm
        else: midi_spect = np.ones(12)*0.15
        
        if is_rest: midi_spect *= 1

        return np.log(np.linalg.norm(audio_spect - midi_spect))

class PSDLikelihoodProcessor(LikelihoodProcessor):
    def calculate(self, fft, state, is_rest):
        semitones = fft.semitone_bins()
        bins = []
        for note in state.notes:
            for i in range(0,8):
                index = note + i*12
                if index < len(semitones) - 1: bins += [index]
        
        if len(bins) > 0:
            power = 0.0
            for index in bins: 
                power += semitones[index]
            total_power = 0.0
            for i in range(min(bins), max(bins)):
                total_power += semitones[i]
            return 1 - power / total_power
        else:
            return 0.8
    def post_process(self, costs):
        logging.log(str(costs[:,0]))
        logging.log(str(costs[:,1]))
        pass
        #for t in range(0,np.size(costs,0)-1):
            #for i in range(0, np.size(costs,1)):
                #costs[t,i] = costs[t+1,i] - costs[t,i]
        
    
factory = factory.Factory({
    "poisson": lambda: PoissonLikelihoodProcessor(),
    "spectra": lambda:SpectragramLikelihoodProcessor(),
    "psd": lambda:PSDLikelihoodProcessor(),
})
