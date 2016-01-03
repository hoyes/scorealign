import score, audio
import os, pickle
import truth
import alignment
import sys
import logging
sys.path.append('./scorealign')

directory = "/home/pah58/public_html/scorealign/data"
               
def names():
        filenames = os.listdir(directory)
        names = []
        for filename in filenames:
                if filename[-4:] == ".mid":
                        names.append(filename[:-4])
        names.sort()
        return names
        
def get_path(name):
        return os.path.realpath(os.path.join(directory, name))
        
def get_dir():
        return os.path.realpath(directory)
        
def get_score(name, total_length = None, seconds = None):
    path = get_path(name)
    return score.Score(path + '.mid', total_length, seconds)

def get_audio(name, seconds = None):
    path = get_path(name)
    return audio.AudioFile(path + '.wav', seconds)

def get_truth(name, score, audio):
    path = get_path(name+".txt")
    if os.path.isfile(path):
        return truth.Truth(path, score, audio)
    
def get_alignment(name, lik, path):
    path = get_path("alignments/"+name+"-"+lik+"-"+path)
    if os.path.isfile(path):
        try:
            f = open(path,"rb")
            a = pickle.load(f)
            f.close()
            return a
        except EOFError:
            pass
            
def save_alignment(a):
    path = get_path("alignments/"+a.name+"-"+a.lik_method+"-"+a.path_method)
    logging.log(path)
    with open(path, "wb") as afile:
        pickle.dump(a, afile)
