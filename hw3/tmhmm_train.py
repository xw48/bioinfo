#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import numpy as np
import pprint
import pickle
import math

MACRO_PRINT = True

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


class GHMM:
	def __init__(self, train_data):
		print 'initializing GHMM model ...'
		self.hidden_states = ['H', 'B', 'OH', 'OB', 'IH', 'IB']
		self.transition_prob = {}
		for x in self.hidden_states:
			for y in self.hidden_states:
				self.transition_prob[(x, y)] = 0

		self.transition_prob[('H', 'IH')] = 0.5
		self.transition_prob[('H', 'OH')] = 0.5
		self.transition_prob[('B', 'IB')] = 0.5
		self.transition_prob[('B', 'OB')] = 0.5
		self.transition_prob[('IH', 'H')] = 1.0
		self.transition_prob[('OH', 'H')] = 1.0
		self.transition_prob[('IB', 'B')] = 1.0
		self.transition_prob[('OB', 'B')] = 1.0

		self.length_dist = {}
		for k,v in train_data.iteritems():
			self.length_dist[k] = {}

			for t in v:
				l = len(t)
				if l in self.length_dist[k]:
					self.length_dist[k][l] += 1.0/float(len(v))
				else:
					self.length_dist[k][l] = 1.0/float(len(v))

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

def help():
	print './tmhmm_train.py <train_file>'
	sys.exit()

if __name__ == "__main__":
	if len(sys.argv) != 2:
		help()

	train_data = GHMM.import_train_data(sys.argv[1])
	ghmm = GHMM(train_data)