#!/usr/bin/env python2
DESCRIPTION = '''
Description which will be diplayed in the useage.
'''
import sys
import os
import argparse
import logging
import gzip

## Pass arguments.
def main():
	## Pass command line arguments. 
	parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=DESCRIPTION)
	parser.add_argument('-i', '--input', metavar='input.txt', 
		required=False, default=sys.stdin, type=lambda x: File(x, 'r'), 
		help='Input [gzip] file (default: stdin)'
	)
	parser.add_argument('-o', '--out', metavar='output.txt', 
		required=False, default=sys.stdout, type=lambda x: File(x, 'w'), 
		help='Output [gzip] file (default: stdout)'
	)
        parser.add_argument('-b', '--bam', metavar='aligned_reads.bam', 
		required=False, type=argparse.FileType('r'), 
		help='Aligned reads (default: %(default)s)'
	)
	parser.add_argument('-p', '--info', metavar='output.info.txt', 
		required=False, type=argparse.FileType('w'), 
		help='Output info file (default: %(default)s)'
	)
	parser.add_argument('-s', '--str', 
		required=False, default='s', type=str, 
		help='String (default: %(default)s)'
	)
	parser.add_argument('-n', '--num', 
		required=False, default=0, type=int, 
		help='Number (default: %(default)s)'
	)
	parser.add_argument('--debug', 
		required=False, action='store_true', 
		help='Print DEBUG info (default: %(default)s)'
	)
	args = parser.parse_args()
	
	## Set up basic debugger
	#logFormat = "%(asctime)s - %(funcName)s - %(message)s"
	#logFormat = "%(asctime)s [%(levelname)s]: %(message)s"
	logFormat = "[%(levelname)s]: %(message)s"
	logging.basicConfig(format=logFormat, stream=sys.stderr, level=logging.INFO)
	if args.debug:
		logging.getLogger().setLevel(logging.DEBUG)
	
	logging.debug('%s', args) ## DEBUG
	
	
	with args.input as infile, args.out as outfile:
		for line in infile:
			print line.strip()
		print "Done printing"
	
	
	## Best to just use a with statement but if you need to operate on the object directly
	
	## Loop over file (need to uncomment __iter__() and close() in File class)
	# for line in args.input:
	#	print line.strip()
	# args.input.close()
	
	## Close file handles (need to uncomment close() method in File class)
	#args.input.close()
	#args.out.close()
	#if args.bam is not None:
	#	args.bam.close()
	#if args.info is not None:
	#	args.info.close()



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
