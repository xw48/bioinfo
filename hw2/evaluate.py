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
import random
import time

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
    return probs.index(max(probs))

def evaluate(sample_no, models):
    model_no = len(models)
    matrix = [[0 for x in range(model_no)] for y in range(model_no)]
    print 'randomly sampling %d testcases ...' % sample_no

    window_size = 1000
    for i in range(sample_no):
        model_idx = random.randint(0, model_no-1)
        seq_idx = random.randint(0, len(models[model_idx].seq))
        sample_seq = models[model_idx].seq[seq_idx:]
        if len(sample_seq) > window_size:
            sample_seq = sample_seq[0:window_size]
        if len(sample_seq) < 10:
            continue
        j = most_likely(sample_seq, models)
        matrix[model_idx][j] += 1

    print 'the confusion matrix is:'
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(matrix)

    tp_tn = float(sum([matrix[i][i] for i in range(model_no)]))
    average_accuracy = tp_tn/float(sum(map(sum, matrix)))
    print 'average accuracy is %f' % average_accuracy

def help():
    print './evaluate.py <sampling #> <model #1> <model #2>'
    sys.exit()

if __name__ == "__main__":
    if len(sys.argv) < 4:
        help()

    start_time = time.time()
    models = []
    for ifile in sys.argv[2:]:
        models.append(pickle.load(open(ifile, 'rb')))

    evaluate(int(sys.argv[1]), models)
    print 'time %s seconds' % (time.time()-start_time)
