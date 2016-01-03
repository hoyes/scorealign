import factory
import abc
import numpy as np
from scipy.stats import norm
import logging
import audio

class PathFinder:
    @abc.abstractmethod
    def calculate(self, costs, score):
        """Takes a cost matrix and calculates the most likely
        route through it"""
        return
    
class LinearPathFinder:
    pass
    
class DTWPathFinder:
    def calculate(self, costs, score):
        T, N = np.shape(costs)
        DTW = np.zeros(np.shape(costs))

        DTW[0, 0] = costs[0,0]
        for i in range(1, N):
            DTW[0, i] = float('inf')
        for i in range(1, T):
            DTW[i, 0] = DTW[i-1,0] + costs[i,0]

        for t in range(1, T):
            for i in range(1, N):
                cost = costs[t, i]
                DTW[t, i] = cost + min(DTW[t-1  , i], DTW[t-1, i-1])

        #Trace back the optimal path
        path = np.zeros(T)
        t = T-1
        i = N-1
        path[t] = i
        while i > 0 and t > 0:
            if DTW[t-1, i-1] < DTW[t-1, i]:
                    i -= 1
            t -= 1
            path[t] = i
        return path
    
class HMMPathFinder:
    def calculate(self, costs, score):
        T,N = np.shape(costs)
        trans = np.zeros((N, N))
        frame_rate = (audio.sample_rate / audio.nsamples)
        for i in range(0, N-1):
            frames = score.states[i].duration * frame_rate
            one_frame = 1 / frame_rate    
            prob = 1 - np.exp(- one_frame / frames)
            trans[i, i] = 1 -prob
            trans[i, i+1] = prob
        trans[N-1,N-1] = 1

        V = np.zeros((T, N))
        path = {}
        
        path[0] = [0]
        for y in range(1,N):
            V[0][y] = float('-inf')
            path[y] = [y]

        for t in range(1,T):
            newpath = {}
            logging.log("Calculating best path at time " + str(t) + "/" + str(T))
            for y in range(0, N):
                max_prob =  float("-inf")
                max_state = -1
                for yo in [y-1, y]:
                    prob = V[t-1][yo] + np.log(trans[yo][y])
                    if prob >= max_prob:
                        max_prob = prob
                        max_state = yo
                max_prob -= costs[t, y]
                V[t][y] = max_prob
                newpath[y] = path[max_state] + [y]
            path = newpath
        return path[N-1]
        
    
class HSMMPathFinder:
    width = 2
    def calculate(self, costs, score):
        T,N = np.shape(costs)
        V = np.zeros((T,N))
        path = {}
        frame_rate = (audio.sample_rate / audio.nsamples)
        path[0] = [0]
        for y in range(1,N):
            path[y] = [y]
        
        for t in range(1,T):
            newpath = {}
            logging.log("Calculating best path at time " + str(t+1) + "/" + str(T))
            for y in range(0, N):
                max_prob =  float("-inf")
                max_u = -1

                for u in range(1, min(50,t+1)):
                    if y > 0: prob = V[t-u, y-1]
                    else: prob = 0.0
                    prob += self.duration(u, score.states[y].duration * frame_rate)
                    for v in range(0, u+1):
                        prob -= costs[t-v, y]
                    if prob >= max_prob:
                        max_prob = prob
                        max_u = u
                V[t][y] = max_prob

        path = np.zeros(T)
        t = T-1
        i = N-1
        path[t] = i
        while i > 0 and t>0:
            if V[t-1, i-1] > V[t-1, i]:
                    i -= 1
            t -= 1
            path[t] = i

        return path
    def duration(self, u, d):
        prob = np.log(norm.sf(u-d, d/self.width))
        return prob

factory = factory.Factory({
    "dtw": lambda:DTWPathFinder(),
    "hmm": lambda:HMMPathFinder(),
    "hsmm": lambda:HSMMPathFinder(),
})
