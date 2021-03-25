#!/usr/bin/env python2
import sys

def Avg(numlist):
	"""
	Abstract: Returns the Average value of the passed list of numbers. 
	Usage:    Avg(numlist)
	"""
	
	avg = float(sum(numlist))/len(numlist) if len(numlist) > 0 else float('nan')
	
	return avg

## 5 + 10 + 7 + 3 = 25 / 4 = 6.25
assert Avg([5, 10, 7, 3]) == 6.25

lengths = []
for line in sys.stdin :
	try:
		lengths.append(float(line))
	except ValueError as e:
		print (e, line)
		#sys.exit(1)
print Avg(lengths)

