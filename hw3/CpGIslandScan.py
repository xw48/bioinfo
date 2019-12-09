#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import numpy as np
import pprint
import pickle
import math

class HMM:
	def __init__(self, model_path):
		self.model_path = model_path

		with open(model_path, 'r') as ifile:
			line_indicator = ''
			lines = ifile.readlines()

			i = 0
			while i < len(lines):
				x = lines[i].strip()
				i += 1

				if '# Hidden states' in x:
					line_indicator = 'hidden'
				elif '# Observation symbols' in x:
					line_indicator = 'observation'
				elif '# Transition probabilities' in x:
					line_indicator = 'transition'
				elif '# Emission probabilities' in x:
					line_indicator = 'emission'
				else:
					if line_indicator == 'hidden':
						self.hidden_states = x.split()
						line_indicator = ''
					elif line_indicator == 'observation':
						self.observation_symbols = x.split()
						line_indicator = ''
					elif line_indicator == 'transition':
						self.transition_prob = {}
						while lines[i].startswith('#') and i < len(lines):
							i += 1

						while i < len(lines) and (not lines[i].startswith('#')):
							y = lines[i].strip().split()

							if len(y) != len(self.hidden_states)+1:
								print 'malformat of transition prob.'
								sys.exit(1)

							for j in range(1, len(y)):
								self.transition_prob[(y[0], self.hidden_states[j-1])] = float(y[j])

							i += 1
					elif line_indicator == 'emission':
						self.emission_prob = {}
						while lines[i].startswith('#') and i < len(lines):
							i += 1

						while i < len(lines) and (not lines[i].startswith('#')):
							y = lines[i].strip().split()

							if len(y) != len(self.observation_symbols)+1:
								print 'malfomat of emission prob.'
								sys.exit(1)

							for j in range(1, len(y)):
								self.emission_prob[(y[0], self.observation_symbols[j-1])] = float(y[j])

							i += 1
	def dump(self):
		pp = pprint.PrettyPrinter(indent=4)
		print '# Hidden states'
		pp.pprint(self.hidden_states)

		print '# Observation symbols'
		pp.pprint(self.observation_symbols)

		print '# Transition probabilities'
		pp.pprint(self.transition_prob)

		print '# Emission probabilities'
		pp.pprint(self.emission_prob)

	# Following the pseudo-code of wikipedia
	def viterbi(self, seq):
		# add leading '0' to seq
		nprob = [{}]
		path = {}
		seq = '0' + seq

		for x in self.hidden_states:
			nprob[0][x] = math.log(1.0) if x == '0' else float("-inf")
			path[x] = ['0']

		seq_len = len(seq)

		for t in range(1, seq_len):
			nprob.append({})
			newpath = {}

			for y in self.hidden_states:
				#(prob, state) = max([(nprob[t-1][k] + math.log(max([self.transition_prob[(k, y)], 1e-20])) + math.log(max([self.emission_prob[(y, seq[t])], 1e-20])), k) for k in self.hidden_states])
				(prob, state) = max([(nprob[t-1][k] + (float("-inf") if self.transition_prob[(k, y)] < 1e-5 else math.log(self.transition_prob[(k, y)])) + (float("-inf") if self.emission_prob[(y, seq[t])] < 1e-5 else math.log(self.emission_prob[(y, seq[t])])), k) for k in self.hidden_states])
				nprob[t][y] = prob
				newpath[y] = path[state] + [y]

			path = newpath

			if t%1000 == 0:
				print "%d / %d" % (t, len(seq))

		(prob, state) = max([(nprob[seq_len - 1][y], y) for y in self.hidden_states])
		return (prob, path[state])

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

def save_object(obj, filename):
	print 'saving object to %s ...' % filename
	with open(filename, 'wb') as output:
		output.write(obj)

def help():
    print './CpGIslandScan.py <hmm model path> <test case>'
    sys.exit()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        help()

    hmm_model = HMM(sys.argv[1])
    #hmm_model.dump()

    seqs = HMM.import_data(sys.argv[2])
    hidden_seq = hmm_model.viterbi(seqs[0])[1]

    i = 0
    starter = -1
    while i<len(hidden_seq):
    	if '+' in hidden_seq[i] and starter < 0:
    		starter = i
    		i += 1
    		while i<len(hidden_seq) and '+' in hidden_seq[i]:
    			i += 1
    		print 'CpGIsland [%d, %d], Len %d' % (starter, i, i-starter)
    		starter = -1
    	else:
    		i += 1

    # export result
    hidden_str = ''.join(hidden_seq)
    save_object(hidden_str, 'output.fasta')