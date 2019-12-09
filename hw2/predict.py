#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys, getopt
import numpy as np
import random
import pprint
import operator
import math
import pickle

class Model:
    NA_TRANS = 1e-4

    def __init__(self, order, id):
        self.order = order
        self.trans = {}
        self.initial = {}
        self.id = id
        self.seq = Model.import_data(id)[0]

    def build(self):
        print 'building model for %s ...' % self.id
        step = 1.0/float(len(self.seq)-self.order+1)
        for i in range(0, len(self.seq)-self.order+1):
            k = self.seq[i:i+self.order]
            if k in self.initial:
                self.initial[k] += step
            else:
                self.initial[k] = step

        for i in range(0, len(self.seq)-self.order):
            k = self.seq[i:i+self.order]
            v = self.seq[i+self.order]
            if k in self.trans:
                if v in self.trans[k]:
                    self.trans[k][v] += 1.0
                else:
                    self.trans[k][v] = 1.0
            else:
                self.trans[k] = {}
                self.trans[k][v] = 1.0
        for k in self.trans:
            sm = sum(self.trans[k].values())
            self.trans[k] = {x:y/sm for x,y in self.trans[k].iteritems()}

    def predict(self, unknown_seq):
        print 'making prediction based on %s ...' % self.id
        starter = unknown_seq[0:self.order]
        p = math.log(self.initial[starter]) if starter in self.initial else math.log(Model.NA_TRANS)
        for i in range(0, len(unknown_seq)-self.order):
            k = unknown_seq[i:i+self.order]
            v = unknown_seq[i+self.order]
            if k in self.trans and v in self.trans[k]:
                p += math.log(self.trans[k][v])
            else:
                p += math.log(Model.NA_TRANS)
        return p

    def dump(self):
        print 'the markov model of %s is:' % self.id
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(self.initial)
        pp.pprint(self.trans)
    
    @staticmethod
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

    def __hash__(self):
        return hash(self.id + self.seq)

def most_likely(seq, models):
    probs = []
    for idx in range(0, len(models)):
        probs.append(models[idx].predict(seq))
    return probs, probs.index(max(probs))

def help():
    print './predict.py <unknown_file> <model #1> <model #2>'
    sys.exit()

if __name__ == "__main__":
    if len(sys.argv) < 4:
        help()

    unknown_file = sys.argv[1]
    unknown_seq = Model.import_data(unknown_file)[0]
        
    models = []
    for ifile in sys.argv[2:]:
        models.append(pickle.load(open(ifile, 'rb')))

    probs, idx = most_likely(unknown_seq, models)
    print 'the sequence comes from %s with prob. p=%f [log(p)=%f]' % (models[idx].id, math.exp(probs[idx]), probs[idx])
