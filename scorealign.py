#!/usr/bin/env python
from scorealign import alignment
from scorealign import data
import sys
import pickle

filename = sys.argv[1]
lik_method = sys.argv[2]
path_method = sys.argv[3]

alignment = alignment.align(filename, lik_method, path_method, rel_width=0.3)
alignment.set_name(filename)
print pickle.dumps(alignment)
