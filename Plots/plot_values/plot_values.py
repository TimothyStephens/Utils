#!/usr/bin/env python2
"""
	Plots values from file or stdin.n
	
	python plot_values.py --x_min 0 --x_max 30 --bin_size 1 -o plot_min0_max30.pdf -i values2plot.txt
	
	*OR*

	cat values2plot.txt | python Plot_values_v2.py --x_min 0 --x_max 30 --bin_size 1 -o plot_min0_max30.pdf
	
"""
__version__ = 2

import sys
import argparse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Main function.
def main():
	parser = argparse.ArgumentParser(description='Plot values files')
	parser.add_argument('-i', '--infile', metavar='values2plot.txt', type=argparse.FileType('r'), required=False, default=sys.stdin, help='Values to plot (default: stdin)')
	parser.add_argument('-o', '--out', metavar='values.histo.pdf', type=str, required=True, help='Histo plot file')
	parser.add_argument('--x_min', metavar=0, type=float, required=True, help='Min value (x-axis) to plot')
	parser.add_argument('--x_max', metavar=100, type=float, required=True, help='Max value (x-axis) to plot')
	parser.add_argument('--bin_size', metavar=1, type=float, required=True, help='Bin size')
	parser.add_argument('--log', action='store_true', required=False, help='Set y-axis on log scale')
	parser.add_argument('--y_max', metavar=10000, type=int, required=False, default=None, help='Max value (y-axis) to plot (default max value)')
	parser.add_argument('--y_min', metavar=0, type=int, required=False, default=None, help='Mix value (y-axis) to plot')
	args = parser.parse_args()

	# Variable vars
	x_min = args.x_min
	x_max = args.x_max
	bin_size = args.bin_size
	num_bins = int((x_max - x_min) / bin_size)
	
	# Load values from file.
	values = []
	for line in args.infile:
		line_strip = line.rstrip('\n')
		if line_strip != '':
			try:
				values.append(float(line_strip))
			except:
				print "WARNING: Line '%s' can not be converted to float" % line_strip

	# Get seq lengths. limit to bounds (max/min values)
	values_bounded = set_bounds(values, x_min, x_max)

	# Plot seq length histo.
	plot_lengths(values_bounded, x_min, x_max, num_bins, args.out, args.log, args.y_max, args.y_min)





def plot_lengths(values, x_min, x_max, num_bins, out_file, log_check, y_max_user, y_min_user):
	# the histogram of the data
        n, bins, patches = plt.hist(values, num_bins, density=False, facecolor='red', alpha=0.75, range=(x_min, x_max), log=log_check)
	
	y_max = max(n) # Get y-axis limit.
	y_min = 0
	if y_max_user is not None:
		y_max = y_max_user
	if y_min_user is not None:
		y_min = y_min_user

        plt.xlabel('Value')
        plt.ylabel('Count')
        plt.title('Histogram of values')
        plt.axis([x_min, x_max, y_min, y_max])
        plt.grid(True)
	
        plt.savefig(out_file, format='pdf')


def set_bounds(values, x_min, x_max):
	""" Pile up values at the x man/min bounds """
	values_bounded = []
	for value in values:
		if value < x_min:
			values_bounded.append(x_min)
		elif value > x_max:
			values_bounded.append(x_max)
		else:
                       	values_bounded.append(value)
        return values_bounded



if __name__ == '__main__':
	main()
