import wave
import numpy as np
import struct
import scipy as sp
import scipy.signal as sig
import miditools
import logging
from pylab import *

sample_rate = 44100.0
nyq_rate = sample_rate / 2
nsamples = 4096
cutoff_hz = 5000.0
num_bins = int(cutoff_hz / (sample_rate /nsamples/8))
winfilter = sig.firwin(100, cutoff_hz / nyq_rate , window='blackman')

class AudioFile:
    """A class representing an audio file"""
    def __init__(self, filename, length = None):
        self.filename = filename
        self.handle = wave.open(filename, 'r')

        width = self.handle.getsampwidth()
        nframes = self.handle.getnframes()
        nchannels = self.handle.getnchannels()

        self.total_length = float(nframes) / self.handle.getframerate();

        if not length is None and float(length) < self.total_length:
            nframes = int(float(length) * self.handle.getframerate())
        self.data = np.zeros((nframes))
	        		        	
        for i in range(0, nframes):
            f = self.handle.readframes(1)
            total = 0
            for n in range(0, self.handle.getnchannels()):
                sample = f[n*width:(n+1)*width]
                total += float(struct.unpack('h', sample)[0]) / 65536
            total /= nchannels
            self.data[i] = total
    def size(self):
	    return np.size(self.data)
    def frame_duration(self):
        return nsamples / sample_rate
    def frame(self, i):
		framedata = self.data[i*nsamples:(i+1)*nsamples]
		data = sig.lfilter(winfilter, 1.0, framedata)
		freq = sp.fft(data, len(data)*8)
		return FreqFrame(np.abs(freq[0:num_bins]))
    def frame_count(self):
        return int(np.floor(len(self.data) / nsamples))
    def length(self):
        return np.size(self.data) / sample_rate
    def get_ffts(self):
        ffts = []
        for i in range(0, self.frame_count()):
                logging.log("Generating fft num " + str(i))
                f = self.frame(i)
                ffts.append(f)
        return ffts

class Peak:
    def __init__(self, freq, magnitude):
        self.freq = freq
        self.magnitude = magnitude
    def __repr__(self):
        freq = self.freq * (sample_rate / nsamples / 8)
        return "\r\nPeak: "+ str(round(freq,2))+ " Hz, "+ str(round(self.magnitude,2)) + " dB"
        
class FreqFrame:
    def __init__(self, data):
        for i in range(0, len(data)): 
                if data[i] == 0.0: data[i] = 0.0001
        max_val = np.max(data)
        #if max_val > 0.0: data /= max_val
        #data = 20 * np.log10(data)
        self.data = data
        self.peaks_cache = None
        self.peaks_bool_cache = None
        self.thres_cache = None
    def threshold(self):
        if self.thres_cache is None:
            self.thres_cache = np.zeros(np.size(self.data))
            length = len(self.data)
            for i in range(0, length):
                self.thres_cache[i] = np.median(self.data[max(0,i-100):min(i+100,length-1)]) + 6
              
        return self.thres_cache
    def peaks(self):
        if self.peaks_cache is None:
            thres = self.threshold()
            self.peaks_cache = []
            for i in range(1, len(self.data)-1):
                if (self.data[i] - self.data[i-1]) > 0.0 and self.data[i] - self.data[i+1] > 0.0:
                    if self.data[i] > thres[i]:
                        self.peaks_cache.append(Peak(i, self.data[i]))
        return self.peaks_cache
    def peaks_bool(self):
        if self.peaks_bool_cache is None:
            self.peaks_bool_cache = np.zeros(len(self.data))
            for p in self.peaks():
                self.peaks_bool_cache[p.freq] = 1
        return self.peaks_bool_cache
    def semitone_bins(self):
        boundaries = miditools.semitone_boundaries()
        bins = np.zeros(len(boundaries))
        curbin = 0
        for i in range(0,num_bins):
            freq = i*sample_rate / nsamples / 8
            if freq >= boundaries[curbin+1]:
                if curbin+2 == len(bins): break
                else: curbin += 1
            bins[curbin] += self.data[i]
        return bins
    def plot(self, show_now=True):
        t = sp.arange(int(num_bins)) * (sample_rate / nsamples / 8)
        plot(t, self.data)
        xlabel('Frequency (Hz)')
        ylabel('Magnitude (dB)')
        grid(True)
        if show_now: show()
    def plotPeaks(self, show_now=True, axis = None):
    	if axis is None:
            axis = subplot(1,1,1)
        t = sp.arange(int(num_bins)) * (sample_rate / nsamples / 8)
        peaks = self.peaks()
        x = np.zeros(len(peaks))
        y = np.zeros(len(peaks))
        for i in range(0, len(peaks)):
                x[i] = peaks[i].freq * (sample_rate / nsamples / 8)
                y[i] = peaks[i].magnitude
        axis.plot(t, self.data, 'b-', t, self.threshold(), 'g--', x, y, 'yo')
        axis.set_xlabel('Frequency (Hz)')
        #axis.xscale('log')
        axis.set_ylabel('Magnitude (dB)')
        axis.grid(True)
        if show_now: show()
