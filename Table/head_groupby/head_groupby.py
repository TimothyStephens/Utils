#!/usr/bin/env python2
DESCRIPTION = '''
Returns the top X rows for each entry ID in column Y.

NOTE:
	- IDs in column Y do not have to be grouped/sorted together however the top X rows have to be ordered
		i.e. most important/significant at the top to lest important/significant at the bottom. 
'''
import sys
import argparse
import logging

VERSION=0.1

## Pass arguments.
def main():
	# Pass command line arguments. 
	parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=DESCRIPTION)
	parser.add_argument('-i', '--input', metavar='data_to_filter.txt', default=sys.stdin, type=argparse.FileType('r'), required=False, help='Input file to filter (default: stdin)')
	parser.add_argument('-o', '--output', metavar='data_filtered.txt', default=sys.stdout, type=argparse.FileType('w'), required=False, help='Output file of top -n rows (default: stdout)')
	parser.add_argument('-n', '--num_rows', default=10, type=int, required=False, help='Num rows to return for each extry in --col (default: %(default)s)')
	parser.add_argument('-c', '--col', default=1, type=int, required=False, help='Column in --input of interest (default: %(default)s)')
	parser.add_argument('--delim', default='\t', type=str, required=False, help='Delimiter for --input (default: \\t)')
	parser.add_argument('--keep_header', action='store_true', required=False, help='Keep first line as header (default: %(default)s)')
	parser.add_argument('--debug', action='store_true', required=False, help='Print DEBUG info (default: %(default)s)')
	args = parser.parse_args()
	
	# Set up basic debugger
	logFormat = "[%(levelname)s]: %(message)s"
	logging.basicConfig(format=logFormat, stream=sys.stderr, level=logging.INFO)
	if args.debug:
		logging.getLogger().setLevel(logging.DEBUG)
	
	logging.debug('%s', args) ## DEBUG
	
	# For each line in input file
	nrows_seen = {}
	for i, line in enumerate(args.input):
		line = line.strip()
		if not line or line.startswith('#'):
			continue
		
		if i == 0 and args.keep_header:
			args.output.write(line + '\n')
			continue
		
		line_sep = line.split(args.delim)
		try:
			col_id = line_sep[args.col-1] 
			logging.debug('col_id %s; line_sep %s', col_id, line_sep) ## DEBUG
			
			# Check if we have seen this id before (can catch cases where ids are out of order)
			if col_id not in nrows_seen.keys():
				nrows_seen[col_id] = 0
			nrows_seen[col_id] += 1
			
			if nrows_seen[col_id] <= args.num_rows:
				args.output.write(line + '\n')
			
		except IndexError:
			logging.info("ERROR: %s", line)
			logging.info("ERROR: -c/--col %s out of range for --infile", args.col)
			sys.exit(1)




if __name__ == '__main__':
	main()
