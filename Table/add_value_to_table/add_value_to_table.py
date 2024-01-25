#!/usr/bin/env python2
DESCRIPTION = '''
add_value_to_table - Will add values into a table (via a new end column)
		     given key:value pairs. 

NOTE:
	- Ignore comment ('#' by defult; can be turned off) and blank lines	
	- Uses exact string matching. Can not do regex or partial matching
	- Assumes first column is 'key' and collowing column/s are 'value'
	- Assumes key is unique in -a/--add; if not unique will take the last value and print warning.
	- Will always add 'blank' values if target column not in key:value pairs.
'''
import sys
import os
import argparse
import gzip
import logging

VERSION=0.1

## Pass arguments.
def main():
	# Pass command line arguments. 
	parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=DESCRIPTION)
	parser.add_argument('-i', '--input', metavar='data_file.txt', 
		required=False, default=sys.stdin, type=lambda x: File(x, 'r'), 
		help='Input [gzip] file (default: stdin)'
	)
	parser.add_argument('-o', '--output', metavar='data_file_with_extra_column.txt', 
		required=False, default=sys.stdout, type=lambda x: File(x, 'w'), 
		help='Output [gzip] file (default: stdout)'
	)
	parser.add_argument('-a', '--add', metavar='info_to_add.txt', 
		required=True, type=lambda x: File(x, 'r'), 
		help='Input [gzip] key:value pairs'
	)
	parser.add_argument('-c', '--col', 
		required=False, default=1, type=int, 
		help='Column in --input of interest'
	)
	parser.add_argument('-d', '--default', 
		required=False, default='', type=str, 
		help='Value to add if not in -a/--add (default: %(default)s)'
	)
	parser.add_argument('--delim_input', 
		required=False, default='\t', type=str, 
		help='Delimiter for --input (default: \\t)'
	)
	parser.add_argument('--delim_add', 
		required=False, default='\t', type=str, 
		help='Delimiter for --add (default: \\t)'
	)
	parser.add_argument('--keep_comments', 
		required=False, action='store_true', 
		help='Keep comment lines from input file in output file (default: %(default)s)'
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
	
	with args.add as add_file:
		info2add = load_key_value_from_file(add_file, args.delim_add)
	
	with args.input as input_file, args.output as output_file:
		# For each line in input file
		for line in input_file:
			line = line.strip('\n')
			if not line:
				continue
			
			if line.startswith('#'):
				if args.keep_comments:
					output_file.write(line + '\n')
				continue
			
			line_sep = line.split(args.delim_input)
			
			try:
				key = line_sep[args.col-1]
				if key in info2add.keys():
					output_file.write(line + args.delim_input + info2add[key] + '\n')
					logging.debug('Value added: %s:%s', key, info2add[key]) ## DEBUG
				else:
					output_file.write(line + args.delim_input + args.default + '\n')
					logging.debug('Default added: %s', args.default) ## DEBUG
			except IndexError:
				logging.info("[ERROR]: %s", line)
				logging.info("[ERROR]: -c/--col %s out of range for --infile", args.col)
				sys.exit(1)
	



def load_key_value_from_file(keyvalue_file, delim):
	'''
	Loads a dict of key:value pairs to add to table.
	'''
	info2add = {}
	ids_seen = []
	for line in keyvalue_file:
		line = line.strip()
		if not line or line.startswith('#'):
			continue
		line_split = line.split(delim)
		
		key = line_split[0]
		if key in ids_seen:
			logging.info('[WARNING]: %s occurs multiple times - taking latest entry.', key) ## DEBUG
		ids_seen.append(key)
		
		info2add[key] = delim.join(line_split[1:])
	
	
	logging.debug('Pairs: %s', info2add) ## DEBUG
	logging.debug('Number of keys loaded: %s', len(info2add.keys())) ## DEBUG
	return info2add



class File(object):
	'''
	Context Manager class for opening stdin/stdout/normal/gzip files.

	 - Will check that file exists if mode='r'
	 - Will open using either normal open() or gzip.open() if *.gz extension detected.
	 - Designed to be handled by a 'with' statement (other wise __enter__() method wont
	    be run and the file handle wont be returned)

	NOTE:
		- Can't use .close() directly on this class unless you uncomment the close() method
		- Can't use this class with a 'for' loop unless you uncomment the __iter__() method
			- In this case you should also uncomment the close() method as a 'for'
			   loop does not automatically cloase files, so you will have to do this
			   manually.
		- __iter__() and close() are commented out by default as it is better to use a 'with'
		   statement instead as it will automatically close files when finished/an exception
		   occures.
		- Without __iter__() and close() this object will return an error when directly closed
		   or you attempt to use it with a 'for' loop. This is to force the use of a 'with'
		   statement instead.

	Code based off of context manager tutorial from: https://book.pythontips.com/en/latest/context_managers.html
	'''
	def __init__(self, file_name, mode):
		## Upon initializing class open file (using gzip if needed)
		self.file_name = file_name
		self.mode = mode

		## Check file exists if mode='r'
		if not os.path.exists(self.file_name) and mode == 'r':
			raise argparse.ArgumentTypeError("The file %s does not exist!" % self.file_name)

		## Open with gzip if it has the *.gz extension, else open normally (including stdin)
		try:
			if self.file_name.endswith(".gz"):
				#print "Opening gzip compressed file (mode: %s): %s" % (self.mode, self.file_name) ## DEBUG
				self.file_obj = gzip.open(self.file_name, self.mode+'b')
			else:
				#print "Opening normal file (mode: %s): %s" % (self.mode, self.file_name) ## DEBUG
				self.file_obj = open(self.file_name, self.mode)
		except IOError as e:
			raise argparse.ArgumentTypeError('%s' % e)
	def __enter__(self):
		## Run When 'with' statement uses this class.
		#print "__enter__: %s" % (self.file_name) ## DEBUG
		return self.file_obj
	def __exit__(self, type, value, traceback):
		## Run when 'with' statement is done with object. Either because file has been exhausted, we are done writing, or an error has been encountered.
		#print "__exit__: %s" % (self.file_name) ## DEBUG
		self.file_obj.close()
#	def __iter__(self):
#		## iter method need for class to work with 'for' loops
#		#print "__iter__: %s" % (self.file_name) ## DEBUG
#		return self.file_obj
#	def close(self):
#		## method to call .close() directly on object.
#		#print "close: %s" % (self.file_name) ## DEBUG
#		self.file_obj.close()



if __name__ == '__main__':
	main()
