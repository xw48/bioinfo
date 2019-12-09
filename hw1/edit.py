#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import numpy as np

def edit(str1, str2):
    l1 = len(str1) + 1
    l2 = len(str2) + 1
    d = [[0 for x in range(l2)] for y in range(l1)]
    for i in range(l2):
        d[0][i] = i
    for j in range(l1):
        d[j][0] = j

    for i in range(1, l1):
        for j in range(1, l2):
            step = 1 if str1[i-1] != str2[j-1] else 0
            d[i][j] = min([d[i-1][j]+1, d[i][j-1]+1, d[i-1][j-1]+step])
    return d[-1][-1]

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
    return arr[0], arr[1]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print 'USAGE: ./edit.py FILE'
        sys.exit()

    str1, str2 = import_data(sys.argv[1])
    e_dist = edit(str1, str2)

    print 'edit distance between %s and %s is %d' % (str1, str2, e_dist)
