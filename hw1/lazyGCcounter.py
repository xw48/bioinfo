#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys, getopt
import numpy as np
import random

def lazyGC(istr, w, t):
    rand_range = len(istr) - w + 1
    if rand_range < 1:
        print 'window size too large'
        sys.exit(-1)

    gc_count = 0
    for i in range(0, t):
        rand_idx = random.randint(0, rand_range-1)
        sample = istr[rand_idx:rand_idx+w]
        gc_count = gc_count + sample.count('G') + sample.count('C')

    return gc_count/float(w*t)
        
def import_data(ifile):
    arr = []
    with open(ifile, 'r') as ifile:
        cur = ''
        for x in ifile.readlines():
            if x.startswith('>'):
                if len(cur) > 0:
                    arr.append(cur)
                    cur = ''
            else:
                cur += x.strip()
        if len(cur) > 0:
            arr.append(cur)
    return arr

def help():
    print './lazyGCcounter.py FILE -w <window> -t <times>'
    sys.exit()

if __name__ == "__main__":
    w = -1
    t = -1
    ifile = sys.argv[1]

    try:
        opts, args = getopt.getopt(sys.argv[2:],"hw:t:")
    except getopt.GetoptError:
        sys.exit()
    for opt, arg in opts:
        if opt == '-h':
            help()
        elif opt == '-w':
            w = int(arg)
        elif opt == '-t':
            t = int(arg)

    if w == -1 or t == -1:
        help()

    arr = import_data(ifile)
    for i in range(len(arr)):
        print 'GC for sequence %d is %f' % (i, lazyGC(arr[i], w, t))
