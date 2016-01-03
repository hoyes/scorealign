#!/usr/bin/env python
import data
score = data.get_score("mozart")
audio = data.get_audio("mozart")
truth = data.get_truth("mozart", score, audio)
print truth.get_path()
