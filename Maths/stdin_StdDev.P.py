#!/usr/bin/env python2
import sys

"""
Returns the standard deviation of a list of numbers pased from stdin.

Code from https://stackoverflow.com/questions/15389768/standard-deviation-of-a-list
"""

def mean(data):
	"""Return the sample arithmetic mean of data."""
	n = len(data)
	if n < 1:
		raise ValueError('mean requires at least one data point')
	return sum(data)/n # in Python 2 use sum(data)/float(n)

def _ss(data):
	"""Return sum of square deviations of sequence data."""
	c = mean(data)
	ss = sum((x-c)**2 for x in data)
	return ss

def stddev(data, ddof=0):
	"""Calculates the population standard deviation
	by default; specify ddof=1 to compute the sample
	standard deviation."""
	n = len(data)
	if n < 2:
		raise ValueError('variance requires at least two data points')
	ss = _ss(data)
	pvar = ss/(n-ddof)
	return pvar**0.5


#assert mean([1, 2, 3]) == 2.0
#assert stddev([1, 2, 3]) == 0.816496580927726
#assert stddev([1, 2, 3], ddof=1) == 0.1


nums = []
for line in sys.stdin :
	try:
		nums.append(float(line))
	except ValueError as e:
		print (e, line)
		#sys.exit(1)
print stddev(nums)

