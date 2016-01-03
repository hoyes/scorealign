import matplotlib.pyplot as plt
import audio
import score
import data
import csv
import numpy as np
np.set_printoptions(threshold=np.nan)
show = True

def stateMatrix(self, rate = 10.7666):
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

def printcosts(a):
    print a.costs
    
def printpath(a):
    print a.path

def processplt(a, plt, name):
    if show:
        plt.show()
    else:
        plt.savefig(name+"-"+a.name+"-"+a.lik_method+"-"+a.path_method+".eps", dpi=300)
        
def fixcosts(a):
    maxval = float('-inf')
    for t in range(0, a.frame_count()):
        for i in range(0, a.state_count()):
            if a.costs[t,i] != float('inf') and a.costs[t,i] > maxval:
                maxval = a.costs[t,i]
                
    for t in range(0, a.frame_count()):
        for i in range(0, a.state_count()):
            if a.costs[t,i] == float('inf'):
                a.costs[t,i] = maxval

def costmap(a):
    plt.clf()
    #plt.figure(figsize=(8,6))
    plt.gray()
    fixcosts(a)
    states = np.arange(0, a.state_count()+1)
    times = np.arange(0, a.frame_count()+1) / audio.sample_rate * audio.nsamples
    #plt.axes([0,0,np.max(times),np.max(states)])
    x, y = np.meshgrid(times, states)
    plt.pcolormesh(x, y, a.costs.transpose())
    plt.ylabel('State number in score sequence')
    plt.xlabel('Time in audio recording (s)')
    processplt(a, plt, "costmap")
    
def costalignment(a):
    plt.clf()
    #plt.figure(figsize=(8,6))
    plt.gray()
    fixcosts(a)
    states = np.arange(0, a.state_count()+1)
    times = np.arange(0, a.frame_count()) / audio.sample_rate * audio.nsamples
    #plt.axes([0,0,np.max(times),np.max(states)])
    x, y = np.meshgrid(times, states)
    plt.pcolormesh(x, y, a.costs.transpose())
    
    test_plot, = plt.plot(times, [s+1 for s in a.path])

    wav = data.get_audio(a.name)
    score = data.get_score(a.name, wav.total_length)
    truth = data.get_truth(a.name, score, wav)

    if truth:
        t = truth_path = truth.get_path()
        truth_plot, = plt.plot(times, [s+1 for s in truth_path])
        bx = plt.legend([test_plot, truth_plot], ("Automatic alignment", "Ground truth"),\
                numpoints=1, handletextpad=0.5, loc="upper left")
        bx.draw_frame(False)
    
    plt.ylabel('State number in score sequence')
    plt.xlabel('Time in audio recording (s)')
    processplt(a, plt, "costmap")
    
def createtruth(a):
    with open('truth.txt', 'wb') as truth:
        for s in a.path:
            truth.write(str(int(s)) + "\n")
            
def timings(a):
    print "Likelihood calculation:", a.lik_time
    print "Path calculation:", a.path_time
