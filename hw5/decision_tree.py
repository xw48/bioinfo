#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
from sklearn import tree
import random
import numpy as np

labels = ['CYT', 'NUC', 'MIT', 'ME3', 'ME2', 'ME1', 'EXC', 'VAC', 'POX', 'ERL']

def import_data(f_path):
	x = []
	with open(f_path) as ifile:
		lines = ifile.readlines()
		for l in lines:
			l = l.strip()
			splits = l.split()

			if len(splits) != 10:
				continue
			item = map(float, splits[1:9])[:]
			item.append(labels.index(splits[9]))
			x.append(item)
	return x

def help():
	print './decision_tree.py <data_set> <k-fold>'
	sys.exit()

def predict(train, test):
	train_attr = train[:, :8]
	train_label = [x[0] for x in train[:, 8:9]]
	test_attr = test[:, :8]
	test_label = [x[0] for x in test[:, 8:9]]

	clf = tree.DecisionTreeClassifier()
	clf = clf.fit(train_attr, train_label)
	predicted = clf.predict(test_attr)

	return [(int(predicted[i]), int(test_label[i])) for i in range(len(predicted))]

def cross_validatition(data, k_fold):
	splits = []
	step = len(data)/k_fold

	result = []

	idx = 0
	while (idx < k_fold):
		random.shuffle(data[idx*step:])
		splits.append(data[idx*step:(idx+1)*step])
		idx += 1

	for idx in range(k_fold):
		test = np.array(splits[idx])
		train = []
		for j in range(k_fold):
			if j == idx:
				continue
			train.extend(splits[j])
		train = np.array(train)
		result.extend(predict(train, test))

	for idx in range(len(labels)):
		lb = labels[idx]
		tp = 0
		fp = 0
		tn = 0
		fn = 0

		for k in range(len(result)):
			if result[k][0] == idx and result[k][1] == idx:
				tp += 1
			if result[k][0] == idx and result[k][1] != idx:
				fp += 1
			if result[k][0] != idx and result[k][1] == idx:
				fn += 1
			if result[k][0] != idx and result[k][1] != idx:
				tn += 1
		print 'Confusion_Matrix of %s, TP %d, FP %d, TN %d, FN %d' % (lb, tp, fp, tn, fn)

if __name__ == "__main__":
	if len(sys.argv) != 3:
		help()

	data = import_data(sys.argv[1])
	k_fold = int(sys.argv[2])
	cross_validatition(data, k_fold)