import os
import numpy as np

with open('run.dat', 'r') as f:
    lines = f.readlines()

lines = [x for x in lines if 'CLUSTER' in lines]

print(lines)