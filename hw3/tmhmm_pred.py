#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import numpy as np
import pprint
import pickle
import math

MACRO_PRINT = False
MAX_PREV = 48

class Markov:
	NA_TRANS = 1e-4

	def __init__(self, data):
		self.data = data
		self.initial = {}
		self.trans = {}

	def build(self):
		t_len = sum([len(x) for x in self.data])
		step = 1.0/float(t_len)

		for x in self.data:
			for y in x:
				if y in self.initial:
					self.initial[y] += step
				else:
					self.initial[y] = step

		for x in self.data:
			for i in range(0, len(x)-1):
				pre = x[i]
				post = x[i+1]

				if pre in self.trans:
					if post in self.trans[pre]:
						self.trans[pre][post] += 1.0
					else:
						self.trans[pre][post] = 1.0
				else:
					self.trans[pre] = {}
					self.trans[pre][post] = 1.0

		for k in self.trans:
			sm = sum(self.trans[k].values())
			self.trans[k] = {x:y/sm for x,y in self.trans[k].iteritems()}

	def dump(self):
		pp = pprint.PrettyPrinter(indent=4)
		print 'Initial Prob.'
		pp.pprint(self.initial)
		print 'Transition Prob.'
		pp.pprint(self.trans)

	def log_prob(self, string):
		prob = 0.0
		init_prob = self.initial[string[0]]
		prob += (math.log(init_prob) if init_prob >= 1e-10 else float("-inf"))

		for i in range(0, len(string)-1):
			pre = string[i]
			post = string[i+1]
			prob_item = math.log(self.trans[pre][post]) if (pre in self.trans and post in self.trans[pre]) else float("-inf")
			prob += prob_item

		return prob

class GHMM:
	def __init__(self, train_data):
		print 'initializing GHMM model ...'
		self.hidden_states = ['H', 'B', 'OH', 'OB', 'IH', 'IB']
		self.initial_prob = {x:math.log(1.0/6.0) for x in self.hidden_states}

		self.emission_prob = {}
		self.transition_prob = {}
		for x in self.hidden_states:
			for y in self.hidden_states:
				self.transition_prob[(x, y)] = float("-inf")

		self.transition_prob[('H', 'IH')] = math.log(0.5)
		self.transition_prob[('H', 'OH')] = math.log(0.5)
		self.transition_prob[('B', 'IB')] = math.log(0.5)
		self.transition_prob[('B', 'OB')] = math.log(0.5)
		self.transition_prob[('IH', 'H')] = math.log(1.0)
		self.transition_prob[('OH', 'H')] = math.log(1.0)
		self.transition_prob[('IB', 'B')] = math.log(1.0)
		self.transition_prob[('OB', 'B')] = math.log(1.0)

		self.length_dist = {}
		for k,v in train_data.iteritems():
			self.length_dist[k] = {}

			for t in v:
				l = len(t)
				if l in self.length_dist[k]:
					self.length_dist[k][l] += 1.0/float(len(v))
				else:
					self.length_dist[k][l] = 1.0/float(len(v))

		for k,v in self.length_dist.iteritems():
			n_v = {a:(math.log(b) if b>1e-10 else float("-inf")) for a,b in v.iteritems()}
			self.length_dist[k] = n_v

		for k in self.length_dist:
			for idx in range(1, MAX_PREV+1):
				if idx not in self.length_dist[k]:
					self.length_dist[k][idx] = float("-inf")

		self.max_length = {k:max(v.keys()) for k, v in self.length_dist.iteritems()}
		if MACRO_PRINT:
			pp = pprint.PrettyPrinter(indent=4)
			print 'length distribution is:'
			pp.pprint(self.length_dist)

		self.markov = {}
		for k,v in train_data.iteritems():
			mkv = Markov(v)
			mkv.build()
			self.markov[k] = mkv

		if MACRO_PRINT:
			for k,v in self.markov.iteritems():
				print 'markov model for hidden state %s:' % k
				v.dump()

	#hidden->observable
	def calc_emission(self, state, string):
		if len(string) > self.max_length[state]:
			return float("-inf")

		if len(string) <= 0:
			return math.log(1.0)

		prob = 0.0
		prob += self.length_dist[state][len(string)]
		prob += self.markov[state].log_prob(string)
		return prob

	@staticmethod
	def import_train_data(train_file):
		train_data = {}
		train_data['H'] = []
		train_data['B'] = []
		train_data['OH'] = []
		train_data['OB'] = []
		train_data['IH'] = []
		train_data['IB'] = []

		tp = ''
		i_o = ''
		with open(train_file) as ifile:
			lines = ifile.readlines()

			i = 0
			while i < len(lines):
				tp = ''
				if lines[i].startswith('>3D_helix;') or lines[i].startswith('>1D_helix;'):
					tp = 'H'
				elif lines[i].startswith('>3D_other;'):
					tp = 'B'

				if len(tp) <= 0:
					i += 1
					continue

				while i < len(lines) and (not lines[i].startswith('N_terminal:')):
					i += 1

				if i >= len(lines):
					break

				x = lines[i].strip()
				i_o = x[len('N_terminal:'):]

				if 'out' in i_o:
					i_o = 'O'+tp
				elif 'in' in i_o:
					i_o = 'I'+tp
				else:
					continue

				while i < len(lines) and (not lines[i].startswith('tm_segments:')):
					i += 1

				if i >= len(lines):
					break

				j = i+1
				if j >= len(lines) or (not lines[j].startswith('sequence:')):
					break

				seq = lines[j].strip()
				seq = seq[len('sequence:'):]

				tm_segs = lines[i].strip()
				tm_segs = tm_segs[len('tm_segments:'):]
				tm_segs = tm_segs.split(';')

				for x in tm_segs:
					if '.' in x:
						x = x[x.find('.')+1:]

					y = x.split(',')
					train_data[tp].append(seq[int(y[0])-1:int(y[1])])
					train_data[i_o].append(seq[int(y[0])-1:int(y[1])])

		return train_data

	# Following the pseudo-code of wikipedia
	def viterbi(self, seq):
		nprob = [{}]*MAX_PREV
		cached_path_ring = [{}]*MAX_PREV
		cached_path_ring[0] = {}

		for i in range(0, MAX_PREV):
			for x in self.hidden_states:
				nprob[i][x] = self.initial_prob[x] + self.calc_emission(x, seq[0:i+1])
				cached_path_ring[i][x] = [(x, i)]

		seq_len = len(seq)
		for t in range(1, seq_len):
			if t >= MAX_PREV:
				nprob.append({})
				newpath = {}
			else:
				newpath = cached_path_ring[t]

			for y in self.hidden_states:
				LAST_STATE = None
				for k in self.hidden_states:
					for prev in range(1, MAX_PREV+1):
						if t-prev < 0 or prev not in self.length_dist[k]:
							continue

						cur_prob = nprob[t-prev][k] + (float("-inf") if self.transition_prob[(k, y)] < math.log(1e-10) else self.transition_prob[(k, y)]) + self.calc_emission(y, seq[t-prev+1:t+1])
						if LAST_STATE == None or cur_prob > LAST_STATE[0]:
							LAST_STATE = (cur_prob, k, t-prev)

				if (t < MAX_PREV and nprob[t][y] < LAST_STATE[0]) or (t >= MAX_PREV):
					nprob[t][y] = LAST_STATE[0]
					newpath[y] = cached_path_ring[LAST_STATE[2]%MAX_PREV][LAST_STATE[1]] + [(y, t)]

			cached_path_ring[t%MAX_PREV] = newpath

		(prob, state) = max([(nprob[seq_len - 1][y], y) for y in self.hidden_states])
		return (prob, cached_path_ring[(seq_len-1)%MAX_PREV][state])

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

def help():
	print './tmhmm_pred.py <train_file> <test_file>'
	sys.exit()

if __name__ == "__main__":
	if len(sys.argv) != 3:
		help()

	train_data = GHMM.import_train_data(sys.argv[1])
	ghmm = GHMM(train_data)

	test_data = GHMM.import_data(sys.argv[2])[0]
	m_states = ghmm.viterbi(test_data)
	print 'log(Prob.) of the state sequence is: %f' % m_states[0]
	print 'the state sequence is:'
	pp = pprint.PrettyPrinter(indent=4)
	pp.pprint(m_states[1])
