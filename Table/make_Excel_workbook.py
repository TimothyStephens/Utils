#!/usr/bin/env python
DESCRIPTION = '''
Takes a set of text files and combines them into a single Excel workbook with each input file as a seperate sheet.

NOTE:
	- if title is more than 31 characters. Some applications may not be able to read the file being loaded.

'''
import sys
import os
import argparse
import logging
import gzip
from pandas import ExcelWriter
import pandas as pd

## Pass arguments.
def main():
	## Pass command line arguments. 
	parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=DESCRIPTION)
	parser.add_argument('-i', '--input', metavar='input_1.tsv', 
		required=True, nargs='+', type=str, 
		help='Input files to load into Excel workbook (required)'
	)
	parser.add_argument('-o', '--out', metavar='output.xlsx', 
		required=True, type=str, 
		help='Output Excel *.xlsx file (required)'
	)
	parser.add_argument('-d', '--delim', 
		required=False, default='\t', type=str, 
		help='String (default: \\t)'
	)
	parser.add_argument('--debug', 
		required=False, action='store_true', 
		help='Print DEBUG info (default: %(default)s)'
	)
	args = parser.parse_args()
	
	## Set up basic debugger
	logFormat = "[%(levelname)s]: %(message)s"
	logging.basicConfig(format=logFormat, stream=sys.stderr, level=logging.INFO)
	if args.debug:
		logging.getLogger().setLevel(logging.DEBUG)
	
	logging.debug('%s', args) ## DEBUG
	
	make_Excel_workbook(args.out, args.input, args.delim)
	



def make_Excel_workbook(outfile, infiles, delim='\t'):
	# Examples: https://xlsxwriter.readthedocs.io/working_with_pandas.html
	writer = ExcelWriter(outfile)
	for filename in infiles:
		logging.info('Loading file %s', filename) ## INFO
		(_, f_name) = os.path.split(filename)
		(f_short_name, _) = os.path.splitext(f_name)
		df = pd.read_csv(filename, sep=delim)
		df.to_excel(writer, sheet_name=f_short_name, index=False)
	writer.save()



if __name__ == '__main__':
	main()
