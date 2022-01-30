from numpy import zeros
from math import log2

def countascii(s):
    count = zeros(256)
    for c in s:
        count[c] +=1
    return count

def calculate_entrophy(data):
    length = len(data)
    count = countascii(data)
    p = count / length
    H = 0.0
    for i in range(256):
        if p[i] > 0.0:
            H += -p[i ]* log2(p[i])
    return H