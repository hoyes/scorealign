#!/usr/bin/env python
from scorealign import alignment, data, likelihood, path
import sys
import pickle

files = ['mozart', 'mozart_2', 'partita_2', 'partita_1', 'deb_clai', 'sarabande_1', 'sarabande_2']
lik_methods = likelihood.factory.keys()
path_methods = path.factory.keys()

for name in files:
    for lik in lik_methods:
        for path in path_methods:
            print name, lik, path
            alignment.align(name, lik, path, rel_width=0.3)

