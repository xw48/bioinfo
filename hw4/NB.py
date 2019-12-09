#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import math

outcome_idx = 0
n_yes = 0
n_no = 0

def help():
	print './NB.py <train_file> <query_file>'
	sys.exit()

def import_train(ifile_name):
	data = []
	with open(ifile_name, 'r') as ifile:
		for x in ifile.readlines():
			x = x.strip()
			if (not x.endswith('No')) and (not x.endswith('Yes')):
				continue
			data.append(x.split(','))

	return data

def import_query(ifile_name):
	data = []
	with open(ifile_name, 'r') as ifile:
		for x in ifile.readlines():
			x = x.strip() + ',?'
			data.append(x.split(','))

	return data

def predict(train_data, query):
	yes_prob = float(n_yes)/float(len(train_data))
	no_prob = float(n_no)/float(len(train_data))

	for x in query:
		if '?' in x:
			break
		num_yes_x = 0
		num_no_x = 0
		for y in train_data:
			if 'Yes' in y and x in y:
				num_yes_x += 1
			if 'No' in y and x in y:
				num_no_x += 1
		yes_prob *= float(num_yes_x)/float(n_yes)
		no_prob *= float(num_no_x)/float(n_no)

	return (yes_prob/(yes_prob + no_prob), no_prob/(yes_prob + no_prob))


if __name__ == "__main__":
	if len(sys.argv) != 3:
		help()

	train_data = import_train(sys.argv[1])
	query_data = import_query(sys.argv[2])

	for x in train_data:
		if 'Yes' in x:
			n_yes += 1
		if 'No' in x:
			n_no += 1

	if len(train_data) > 0:
		outcome_idx = len(train_data[0]) - 1

	print 'prediction results:'
	for x in query_data:
		comp_prob = predict(train_data, x)
		if comp_prob[0] > comp_prob[1]:
			x[outcome_idx] = 'Yes'
			prob = comp_prob[0] 
		else:
			x[outcome_idx] = 'No'
			prob = comp_prob[1]
			 
		print '%s,%.4f' % (x, prob)