#!/usr/bin/env python2
DESCRIPTION = '''
groupby - Will group and combine lines with the same value in the first column.  

NOTE:
	- Ignore comment and blank lines	
	- Uses exact string matching. Can not do regex or partial matching
	- Will join lines in the order they appear in the file. Will also preserve the oorder of the groups as they appear in the input.
	- Will remove column of interest from lines that are appended.
'''
import sys
import argparse
import logging

VERSION=0.1

## Pass arguments.
def main():
	# Pass command line arguments. 
	parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=DESCRIPTION)
	parser.add_argument('-i', '--input', metavar='data_file.txt', default=sys.stdin, type=argparse.FileType('r'), required=False, help='Input file (default: stdin)')
	parser.add_argument('-o', '--output', metavar='data_file_with_extra_column.txt', default=sys.stdout, type=argparse.FileType('w'), required=False, help='Output file (default: stdout)')
	parser.add_argument('--delim_input', default='\t', type=str, required=False, help='Delimiter for --input (default: \\t)')
	parser.add_argument('--delim_groups', default='\t', type=str, required=False, help='Delimiter for groups in --output (default: \\t)')
	parser.add_argument('--debug', action='store_true', required=False, help='Print DEBUG info (default: %(default)s)')
	args = parser.parse_args()
	
	# Set up basic debugger
	logFormat = "[%(levelname)s]: %(message)s"
	logging.basicConfig(format=logFormat, stream=sys.stderr, level=logging.INFO)
	if args.debug:
		logging.getLogger().setLevel(logging.DEBUG)
	
	logging.debug('%s', args) ## DEBUG
	
	groupby_column(args.input, args.output, args.delim_input, args.delim_groups)
	
def groupby_column(input_fh, output_fh, delim_input, delim_groups, col=1):
	groups = {}
	groups_order = []
	
	# For each line in input file
	for line in input_fh:
		line = line.strip()
		if not line or line.startswith('#'):
			continue
		
		line_sep = line.split(delim_input)
		
		try:
			key = line_sep[col-1]
			if key in groups_order:
				groups[key].append(delim_input.join(line_sep[col:]))
				
			else:
				groups_order.append(key)
				groups[key] = [delim_input.join(line_sep[col:])]
		except IndexError:
			logging.error("[ERROR]: Problem splitting --infile into >=2 columns: %s", line)
			sys.exit(1)
		
	# Print each group
	for key in groups_order:
		output_fh.write(key+'\t'+delim_groups.join(groups[key])+'\n')



if __name__ == '__main__':
	main()
