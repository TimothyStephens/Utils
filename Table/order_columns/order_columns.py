#!/usr/bin/env python
DESCRIPTION = '''
order_columns - Takes an ORDERED list of column names (one per line) to return from input file. 
                Columns not in input list will not be in output.
                First column name in input list will be the first column, seconds column name in input list will be the second column, etc
NOTE:
	- Ignore comment ('#') and blank lines	
        - Assume first non-comment line has column headers.
	- Uses exact string matching. Can not do regex or partial matching.
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
	parser.add_argument('-o', '--output', metavar='data_filtered.txt', default=sys.stdout, type=argparse.FileType('w'), required=False, help='Output file of ordered columns (default: stdout)')
	parser.add_argument('-f', '--file', metavar='ordered_col_names.txt', type=argparse.FileType('r'), required=True, help='Ordered column names to keep/reorder (required)')
	parser.add_argument('--delim', default='\t', type=str, required=False, help='Delimiter for --input (default: \\t)')
	parser.add_argument('--debug', action='store_true', required=False, help='Print DEBUG info (default: %(default)s)')
	args = parser.parse_args()
	
	# Set up basic debugger
	logFormat = "[%(levelname)s]: %(message)s"
	logging.basicConfig(format=logFormat, stream=sys.stderr, level=logging.INFO)
	if args.debug:
		logging.getLogger().setLevel(logging.DEBUG)
	
	logging.debug('%s', args) ## DEBUG
	
	ordered_col_names = load_id_list(args.file) # Load column names/ids
	
	# For each line in input file
	is_first_line = True
	for line in args.input:
		line = line.rstrip('\n')
		if not line or line.startswith('#'):
			continue
		
		if is_first_line:
			is_first_line = False
			col_names = line.split(args.delim)
			
			# For each ordered ID figure out its index/position in the avaliable columns
			col_output_order = []
			for name in ordered_col_names:
				try:
					col_output_order.append(col_names.index(name))
				except ValueError:
					logging.error("column name '%s' in ordered list not found in input file!", name)
					sys.exit(1)
			logging.debug('col_output_order: %s', col_output_order) ## DEBUG
			
			# Now output the column names we want in the order we want.
			tmp_write = []
			for i in col_output_order:
				tmp_write.append(col_names[i])
			args.output.write(args.delim.join(tmp_write) + '\n')
			continue
		
		# If line is not header line write columns in the order we established
		line_split = line.split(args.delim)
		tmp_write = []
		for i in col_output_order:
			try:
				tmp_write.append(line_split[i])
			except IndexError:
				logging.error("Column index '%s' does not exist for split line: '%s'", i, line_split)
				sys.exit(1)
		args.output.write(args.delim.join(tmp_write) + '\n')



def load_id_list(id_file):
	'''
	Loads a lit of IDs into a list.
	'''
	ids = []
	for line in id_file:
		line = line.strip()
		if not line or line.startswith('#'):
			continue
		ids.append(line)
	logging.debug('IDS: %s', ids) ## DEBUG
	logging.debug('Number of ids loaded: %s', len(ids)) ## DEBUG
	return ids


if __name__ == '__main__':
	main()
