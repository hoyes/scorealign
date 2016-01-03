#!/usr/bin/env python
import sys
from scorealign import alignment
import pickle
from scorealign import visualisefuncs

if len(sys.argv) > 2:
    f = open(sys.argv[2],"rb")
    a = pickle.load(f)
    f.close()
else:
    a = pickle.load(sys.stdin)

method = sys.argv[1]
getattr(visualisefuncs, method)(a)
