#!/usr/bin/env python
DESCRIPTION = '''
Takes a fasta formated alignment with ambiguous characters (which represent the different bi-allelic SNPs)
and converst them back into the possible non-ambiguous characters.

A -> AA
C -> CC
G -> GG
T -> TT
R -> AG (purine)
Y -> CT (pyrimidine)
M -> AC (amino)
K -> GT (keto)
S -> CG (strong)
W -> AT (weak)
N -> NN (unknown)

NOTE:
	- Cant handle ambiguous characters which represent 3 non-ambiguous characters:
		B -> C, G or T (next letter after A)
		H -> A, C or T (next letter after G)
		D -> A, G or T (next letter after C)
		V -> A, G or C (next letter after T)
	- The order of the new non-ambiguous characters has been otimized to reduce the distance between variants.
		i.e. in an alignment R and W would be more similar when represent like AG and AT (only mismatch at G/T)
		rather than GA and AT (mismatch at both positions: G/A and A/T).
		HOWEVER, this cant be done for all combinations so some bi-allelic SNPs with have an inflated distance
		when represented like this. 
	- Also, we dont have any info about linakge between SNPs (phasing), therefor we assume (in the example of R and W)
		that the two A alleles are from the same chromosome, which is likely not true in many cases. This would
		reduce overall distance between samples. Not a problem we can address but something to be aware of. 

'''
import sys
import os
import argparse
import logging
import gzip
from itertools import groupby

## Pass arguments.
def main():
	## Pass command line arguments. 
	parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=DESCRIPTION)
	parser.add_argument('-i', '--input', metavar='input.fasta', 
		required=False, default=sys.stdin, type=lambda x: File(x, 'r'), 
		help='Input [gzip] fasta file (default: stdin)'
	)
	parser.add_argument('-o', '--out', metavar='in.expandedChar.fasta', 
		required=False, default=sys.stdout, type=lambda x: File(x, 'w'), 
		help='Output [gzip] fasta file with converted ambiguous characters (default: stdout)'
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
	
	
	with args.input as infasta, args.out as outfasta:
		expand_one_character_genotype_fasta(infasta, outfasta)
	


nt_char_conv = {'A':'AA', 'C':'CC', 'G':'GG', 'T':'TT', 'R':'AG', 'Y':'CT', 'M':'AC', 'K':'GT', 'S':'CG', 'W':'AT', 'N':'NN'}



def expand_one_character_genotype_fasta(infasta, outfasta):
	for header, seq in fasta_iter(infasta):
		new_seq = ''
		for nt in seq:
			new_seq += nt_char_conv[nt] # TODO: Catch IndexError's from other ambiguous characters
		outfasta.write(">"+header+'\n'+new_seq+'\n')


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



def fasta_iter(fh):
	"""
	Given a fasta file. yield tuples of header, sequence
	Clears description from seq name.
	
	From: https://www.biostars.org/p/710/
	Updated: 11/09/2018
	Version: 0.2
	"""
	# ditch the boolean (x[0]) and just keep the header or sequence since
	# we know they alternate.
	faiter = (x[1] for x in groupby(fh, lambda line: line[0] == ">"))
	for header in faiter:
		# drop the ">" and description
		header = header.next()[1:].strip().split(' ')[0]
		# join all sequence lines to one.
		seq = "".join(s.strip() for s in faiter.next())
		yield header, seq


if __name__ == '__main__':
	main()
