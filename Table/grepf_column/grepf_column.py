#!/usr/bin/env python2
DESCRIPTION = '''
grepf_column - Mimics the functionality of 'grep -f' but with exact string mathcing and 
               the ability to specifiy the column of interest.

NOTE:
	- Ignore comment ('#') and blank lines	
	- Uses exact string matching. Can not do regex or partial matching
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
	parser.add_argument('-o', '--output', metavar='data_filtered.txt', default=sys.stdout, type=argparse.FileType('w'), required=False, help='Output file of filtered values (default: stdout)')
	parser.add_argument('-f', '--file', metavar='ids_to_grepf.txt', type=argparse.FileType('r'), required=True, help='IDs to use for seach/filter (required)')
	parser.add_argument('-v', '--invert_match', action='store_true', required=False, help='Return lines not in --file (default: %(default)s)')
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
	
	ids = load_id_list(args.file) # Load IDs
	
	# For each line in input file
	for i, line in enumerate(args.input):
		line = line.rstrip('\n')
		if not line or line.startswith('#'):
			continue
		
		if i == 0 and args.keep_header:
			args.output.write(line + '\n')
			continue
		
		line_sep = line.split(args.delim)
		try:
			if line_sep[args.col-1] in ids and not args.invert_match:
				logging.debug('Split line: %s - MATCHING', line_sep) ## DEBUG
				args.output.write(line + '\n')
			
			elif line_sep[args.col-1] not in ids and args.invert_match:
				logging.debug('Split line: %s - NOT_MATCHING_INVERTED', line_sep) ## DEBUG
				args.output.write(line + '\n')
			else:
				logging.debug('Split line: %s - SKIPPED', line_sep) ## DEBUG
		except IndexError:
			logging.info("ERROR: %s", line)
			logging.info("ERROR: -c/--col %s out of range for --infile", args.col)
			sys.exit(1)


def load_id_list(id_file):
	'''
	Loads a lit of IDs into a set.
	'''
	ids = []
	for line in id_file:
		line = line.strip()
		if not line or line.startswith('#'):
			continue
		ids.append(line)
	logging.debug('IDS: %s', ids) ## DEBUG
	logging.debug('Number of ids loaded: %s', len(ids)) ## DEBUG
	logging.debug('Number of unique ids: %s', len(set(ids))) ## DEBUG
	return set(ids)


if __name__ == '__main__':
	main()
