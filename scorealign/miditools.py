def fundamental(note):              
    return pow(2, (note-69.0)/12.0)*440.0
    
def all_semitones():
    return [fundamental(n) for n in range(0,128)]
    
def semitone_boundaries():
    boundaries = all_semitones()
    #Adjust boundaries to equal start of bins
    for i in reversed(range(0,len(boundaries))):
        if i==0: 
            boundaries[i] = 0.0
        else:
            boundaries[i] -= (boundaries[i] - boundaries[i-1])/2
    return boundaries
