#!/usr/bin/env python2
DESCRIPTION = '''

## Will take an expression table:
-------------------------------------------
Name    0     0     1     1       2       2
g_1     110.228435689309        64.0391285500166        122.567613606863        36.5502485374348        31.4453312587946        50.1473810591819        
g_2     99.6883941607563        51.0636072183567        100.444308424267        31.3542176087311        28.2054047121086        37.7055303795786
..      ....                    ....                    ....                    ....                    ....                    ....
-------------------------------------------


## And will melt the data into:
--------------------------------
Name    Time    Expression
g_1     0       110.228435689309
g_1     0       64.0391285500166
g_1     1       122.567613606863
g_1     1       36.5502485374348
g_1     2       31.4453312587946
g_1     2       50.1473810591819
g_2     0       99.6883941607563
g_2     0       51.0636072183567
g_2     1       100.444308424267
g_2     1       31.3542176087311
..      .       ....
..      .       ....
--------------------------------

## Example (add 4th column with condition info):
python melt_table.py -i matrix.txt.CL | awk '{ if (NR!=1) {print $0"\\tCL"} else {print $0"\\tCondition"} }' > matrix.melted
python melt_table.py -i matrix.txt.HL | awk '{ if (NR!=1) {print $0"\\tHL"} }' >> matrix.melted

'''
import sys
import os
import argparse
import logging
import gzip

## Pass arguments.
def main():
	# Pass command line arguments. 
	parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=DESCRIPTION)
	parser.add_argument('-i', '--input', metavar='input.txt', 
		required=False, default=sys.stdin, type=lambda x: __parse_file_check_compression(x, 'r'), 
		help='Expression matrix [gzip] file (default: stdin)'
	)
	parser.add_argument('-o', '--out', metavar='output.txt', 
		required=False, default=sys.stdout, type=lambda x: __parse_file_check_compression(x, 'w'), 
		help='Melted expression [gzip] file (default: stdout)'
	)
	parser.add_argument('--debug', 
		required=False, action='store_true', 
		help='Print DEBUG info (default: %(default)s)'
	)
	args = parser.parse_args()
	
	# Set up basic debugger
	logFormat = "[%(levelname)s]: %(message)s"
	logging.basicConfig(format=logFormat, stream=sys.stderr, level=logging.INFO)
	if args.debug:
		logging.getLogger().setLevel(logging.DEBUG)
	
	logging.debug('%s', args) ## DEBUG
	
	melt_expression_table(args.input, args.out)



def melt_expression_table(in_table, out_table):
	out_table.write('Name\tTime\tExpression\n')
	
	col_names = in_table.readline().strip().split('\t') # Get column names
	if len(col_names) <= 1:
		logging.error('Need >= 2 columns, only %s found!', len(col_names))
		logging.error('%s', col_names)
		sys.exit(1)
	
	for line in in_table:
		line = line.strip()
		# Ignore blank and comment lines
		if not line or line.startswith('#'):
			continue
		
		row = line.split('\t')
		if len(row) != len(col_names):
			logging.error('Num columns (%s) in row does not match num column (%s) names', len(row), len(col_names))
			logging.error('%s', col_names)
			logging.error('%s', row)
			sys.exit(1)
		
		for i in range(1, len(row)):
			out_table.write('%s\t%s\t%s\n' % (row[0], col_names[i], row[i]))



def __parse_file_check_compression(fh, mode='r'):
	'''
	Open stdin/normal/gzip files - check file exists (if mode='r') and open using appropriate function.
	'''
	# Check file exists if mode='r'
	if not os.path.exists(fh) and mode == 'r':
		raise argparse.ArgumentTypeError("The file %s does not exist!" % fh)
	
	## open with gzip if it has the *.gz extension, else open normally (including stdin)
	try: 
		if fh.endswith(".gz"):
			return gzip.open(fh, mode+'b')
		else:
			return open(fh, mode)
	except IOError as e:
		raise argparse.ArgumentTypeError('%s' % e)



if __name__ == '__main__':
	main()
