import path, likelihood
import numpy as np
import sys, audio, logging
import data
import time

class Alignment:
    def __init__(self, costs, path, lik_method, path_method):
        self.costs = costs
        self.path = path
        self.name = "test"
        self.lik_method = lik_method
        self.path_method = path_method
        self.truth_path = None
    def frame_count(self):
        return np.size(self.costs,0)
    def frame_duration(self):
        return audio.nsamples / audio.sample_rate
    def state_count(self):
        return np.size(self.costs,1)
    def set_name(self, name):
        self.name = name
    def get_events(self, score):
        duration = 0.0
        last_state = -1
        midi_points = []
        audio_points = []
        for i in range(0, len(self.path)):
            if self.path[i] != last_state:
                last_state = self.path[i]
                midi_points.append(duration)
                audio_points.append(i*self.frame_duration())
                duration += score.states[int(self.path[i])].midi_duration
        return (audio_points, midi_points)
    def get_truth_events(self, score):
        duration = 0.0
        last_state = -1
        midi_points = []
        audio_points = []
        for i in range(0, len(self.truth_path)):
            if self.truth_path[i] != last_state:
                last_state = self.truth_path[i]
                midi_points.append(duration)
                audio_points.append(i*self.frame_duration())
                duration += score.states[int(self.truth_path[i])].midi_duration
        return (audio_points, midi_points)

class AlignmentProcessor:
    def __init__(self, lik_method, path_method):
        self.likproc = likelihood.factory(lik_method)
        self.pathproc = path.factory(path_method)
        self.lik_method = lik_method
        self.path_method = path_method
    def get_costs(self, audio, score, const_width=None, rel_width=None):
        """Calculates t*i cost matrix"""
        costs = np.zeros((audio.frame_count(), score.state_count()))
        ffts = audio.get_ffts()
       
        width = audio.frame_count()
        if const_width != None: width = const_width
        elif rel_width != None: width *= rel_width

        expected_t = 0.0
        for i in range(0, score.state_count()):
            logging.log("Calculating likelihoods for state " + str(i+1) + "/" + str(score.state_count()))
            for t in range(0, audio.frame_count()):
                if t > expected_t - width and t < expected_t + width:
                    if i > 0 and len(score.states[i].notes) == 0:
                        costs[t, i] = self.likproc.calculate(ffts[t], score.states[i-1], True)
                    else:
                        costs[t, i] = self.likproc.calculate(ffts[t], score.states[i], False)
                else:
                    costs[t, i] = float('inf')
            expected_t += score.states[i].duration / audio.frame_duration()
            
        self.likproc.post_process(costs)
        return costs
    def align(self, audio, score, const_width=None, rel_width=None):
        score.resize(audio.total_length)

        start_time = time.clock()
        costs = self.get_costs(audio, score, const_width, rel_width)
        logging.log("Calculating best path")
        lik_time = time.clock()
        path = self.pathproc.calculate(costs, score)
        end_time = time.clock()
        a = Alignment(costs, path, self.lik_method, self.path_method)
        
        a.lik_time = lik_time - start_time
        a.path_time = end_time - lik_time
        return a
        
def align(name, lik_method, path_method, const_width=None, rel_width=None):
    a = data.get_alignment(name, lik_method, path_method)
    if a == None:
        audio = data.get_audio(name)
        score = data.get_score(name)
        
        proc = AlignmentProcessor(lik_method, path_method)
        a = proc.align(audio, score, const_width, rel_width)
        truth = data.get_truth(name, score, audio)
        if truth: a.truth_path = truth.get_path()
        a.set_name(name)
        data.save_alignment(a)
    return a
