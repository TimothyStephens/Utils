#!/usr/bin/python
DESCRIPTION = '''
Cleans a nucl or prot fasta file of non-standard seq and header characters. 
Will print stats of the cleaning process once completed (unless --quiet set).

Script will (in this order):
	. Remove header description
		OR keep description (--keep_descriptions)
	. Replace problematic characters in headers
	. Replace problematic characters in sequences
	. Convert sequence to uppercase (default)
		OR lowercase (--lower_case)
		OR keep case (--keep_case)
	AND/OR
	. Replace internal stop codons
	. Remove terminal stop codons
	. Add prefix to seq header
'''
import sys
import argparse
import logging
from itertools import groupby


# Pass command line arguments. 
def main():
	parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=DESCRIPTION)
	parser.add_argument('-i', '--fasta_in', metavar='in.fasta.txt', type=argparse.FileType('r'), default=sys.stdin, required=False, help='Output file (default: %(default)s)')
	parser.add_argument('-o', '--fasta_out', metavar='out.fasta', type=argparse.FileType('w'), default=sys.stdout, required=False, help='Output file (default: %(default)s)')
	
	parser.add_argument('--seq_type', choices=['nuc', 'nucx', 'prot'], default='nucx', required=True, help='Expected seq type (default: %(default)s)')
	parser.add_argument('--header_type', choices=['normal', 'basic'], default='basic', required=False, help='Expected header type (default: %(default)s)')
	
	parser.add_argument('--prefix', type=str, default='', required=False, help='Prefix add to seq name (default: %(default)s)')
	parser.add_argument('--keep_descriptions', action='store_true', required=False, help='Keep seq description (default: %(default)s)')
	parser.add_argument('--fix_internal', action='store_true', required=False, help='Replace stop codons with X characters (default: %(default)s)')
	parser.add_argument('--remove_stop', action='store_true', required=False, help='Remove stop codons from prot seqs (default: %(default)s)')
	
	parser.add_argument('--keep_case', action='store_true', required=False, help='Keep case of seq characters (default: Convert to uppercase)')
	parser.add_argument('--lower_case', action='store_true', required=False, help='Make seq characters lowercase (default: Convert to uppercase)')
	
	parser.add_argument('--info', action='store_true', required=False, help='Info about the cleaning of each sequence (default: %(default)s)')
	parser.add_argument('-q', '--quiet', action='store_true', required=False, help='Dont print any info (including stats at the end) (default: %(default)s)')
	parser.add_argument('--debug', action='store_true', required=False, help='Print DEBUG info (default: %(default)s)')
	args = parser.parse_args()
	
	 # Set up basic debugger
	logging.basicConfig(format='#[%(levelname)s]: %(message)s', stream=sys.stderr)
	if args.debug:
		logging.getLogger().setLevel(logging.DEBUG)
	elif args.info and not args.quiet:
		logging.getLogger().setLevel(logging.INFO)
	else:
		logging.getLogger().setLevel(logging.WARNING)
	
	logging.debug('%s', args) ## DEBUG
	
	clean_fasta(args.fasta_in, args.fasta_out, args.seq_type, args.header_type, 
			args.prefix, args.keep_descriptions, args.fix_internal, args.remove_stop, 
			args.keep_case, args.lower_case, args.quiet)


# Accepted character lists
CHARACTERS_SEQ_NUCLEOTIDE = 'atgcnATGCN'
CHARACTERS_SEQ_NUCLEOTIDE_X = 'atgcnxATGCNX'
CHARACTERS_SEQ_PROTEIN = '*acdefghiklmnpqrstvwyxACDEFGHIKLMNPQRSTVWYX'
CHARACTERS_HEADER_NORMAL = '.|_- abcdefghijklmnopqrstuvwyxzABCDEFGHIJKLMNOPQRSTUVWYXZ0123456789'
CHARACTERS_HEADER_BASIC = '._-abcdefghijklmnopqrstuvwyxzABCDEFGHIJKLMNOPQRSTUVWYXZ0123456789'

def clean_fasta(in_fasta, out_fasta, seq_type, header_type, 
			prefix, keep_descriptions, fix_internal, remove_stop, 
			keep_case, lower_case, quiet):
	fa = fasta_clean_and_track_problems()
	for header, seq in fasta_iter(in_fasta):
		## Load fasta header and seq into cleaning class
		fa.load_fasta_entry(header, seq)
		
		## Remove header description OR keep description (--keep_descriptions)
		if not keep_descriptions:
			fa.remove_description()
		
		## Replace problematic characters in headers
		if header_type == "basic":
			fa.clean_header(CHARACTERS_HEADER_BASIC, '_')
		else:
			fa.clean_header(CHARACTERS_HEADER_NORMAL, '_')
		
		## Replace problematic characters in sequences
		if seq_type == 'prot':
			fa.clean_seq(CHARACTERS_SEQ_PROTEIN, 'X')
		elif seq_type == 'nuc':
			fa.clean_seq(CHARACTERS_SEQ_NUCLEOTIDE, 'N')
		else: #seq_type == 'nucx':
			fa.clean_seq(CHARACTERS_SEQ_NUCLEOTIDE_X, 'N')
		
		## Convert sequence to uppercase (default) OR lowercase (--lower_case) OR keep case (--keep_case)
		if not keep_case:
			if lower_case:
				fa.seq_to_lower()
			else:
				fa.seq_to_upper()
		
		## Replace internal stop codons
		if fix_internal:
			fa.fix_internal_stop('X')
		
		## Remove terminal stop codons
		if remove_stop:
			fa.remove_stop()
		
		## Add prefix to seq header
		fa.add_prefix(prefix)
		
		## Write fasta to output
		out_fasta.write(fa.return_fasta_entry())
		
	## Print stats
	if not quiet:
		logging.getLogger().setLevel(logging.INFO)
	fa.print_cleaning_stats()



class fasta_clean_and_track_problems:
	'''
	Class that acts to perform the cleaning of the fasta entry and also keep track
	of the actions taken. Easy way to compile stats for printing at the end. 
	'''
	def __init__(self):
		# Current fasta entry
		self.entry_count = 0
		self.header = ''
		self.seq = ''
		
		# Keep track of seq and header character replacement.
		# Counts start as 'None' type so we know at the end if this step has been run. 
		
		# Check header
		self.bad_header_headers = []
		self.bad_header_chars = []
		self.replaced_header_count = None
		self.replaced_header_chars_count = None
		
		# Check seq
		self.bad_seq_headers = []
		self.bad_seq_chars = []
		self.replaced_seq_count = None
		self.replaced_seq_chars_count = None
		
		# Fasta descriptions
		self.cleaned_descriptions_count = None
		
		# Internal stop codons
		self.internal_stop_headers = []
		self.internal_stop_count = None
		self.internal_stop_seq_count = None
		
	def load_fasta_entry(self, header, seq):
		self.entry_count += 1
		self.header = header
		self.seq = seq
	
	def return_fasta_entry(self):
		return '>{}\n{}\n'.format(self.header, self.seq)
	
	
	########################
	## Cleaning functions ##
	########################
	def clean_header(self, allowed_chars, replace_with):
		if self.replaced_header_count is None: # If this is the first time we have run this function
			self.replaced_header_count = 0
			self.replaced_header_chars_count = 0
		
		# for each character in header
		self.t_header = ''
		self.replaced_header_chars = []
		
		for i, h in enumerate(self.header):
			if h not in allowed_chars:
				self.t_header += replace_with
				self.replaced_header_chars.append(replace_with)
				self.found_bad_header_char(self.header, h)
			else:
				self.t_header += h
		self.header = self.t_header
		
		# Print info
		if len(self.replaced_header_chars) > 0:
			logging.info('Found problematic header chracters %s in %s', ' '.join(set(self.replaced_header_chars)), self.header)
	
	
	def clean_seq(self, allowed_chars, replace_with):
		if self.replaced_seq_count is None: # If this is the first time we have run this function
			self.replaced_seq_count = 0
			self.replaced_seq_chars_count = 0
		
		# For each character in seq
		self.t_seq = ''
		self.replaced_seq_chars = []
		
		for i, s in enumerate(self.seq):
			if s not in allowed_chars:
				self.t_seq += replace_with
				self.replaced_seq_chars.append(s)
				self.found_bad_seq_char(self.header, s)
			else:
				self.t_seq += s
		self.seq = self.t_seq
		
		# Print info
		if len(self.replaced_seq_chars) > 0:
			logging.info('Found problematic sequence chracters %s in %s', ' '.join(set(self.replaced_seq_chars)), self.header)
	
	
	def remove_description(self):
		if self.cleaned_descriptions_count is None: # If this is the first time we have run this function
			self.cleaned_descriptions_count = 0
		
		# Keep count if we actually cleaned something
		if len(self.header.split(' ')) > 1:
			self.cleaned_descriptions()
		
		self.header = self.header.split(' ')[0]
	
	
	def fix_internal_stop(self, replace_with):
		if self.internal_stop_seq_count is None: # If this is the first time we have run this function
			self.internal_stop_seq_count = 0
			self.internal_stop_count = 0
		
		# Track how many internal stop codons we find in this seq
		self.stop_count = 0
		
		self.seq_split = list(self.seq)
		for i in range(len(self.seq_split)-1): # Dont check last pos
			if self.seq_split[i] == '*':
				self.seq_split[i] = replace_with
				self.stop_count += 1
				self.found_internal_stop(self.header)
		self.seq = ''.join(self.seq_split)
		
		# Print info
		if self.stop_count > 0:
			logging.info('Found %s internal stop codon/s in %s', self.stop_count, self.header)
	
	
	def remove_stop(self):
		if self.seq[-1] == '*':
			self.seq = self.seq[:-1]
	
	
	def add_prefix(self, prefix):
		self.header = prefix + self.header
	
	
	def seq_to_upper(self):
		self.seq = self.seq.upper()
	
	
	def seq_to_lower(self):
		self.seq = self.seq.lower()


	
	########################
	## Tracking functions ##
	########################
	def found_bad_header_char(self, header, header_char):
		if header not in self.bad_header_headers:
			self.bad_header_headers.append(header)
			self.replaced_header_count += 1
		self.bad_header_chars.append(header_char)
		self.replaced_header_chars_count += 1
	
	def found_bad_seq_char(self, header, seq_char):
		if header not in self.bad_seq_headers:
			self.bad_seq_headers.append(header)
			self.replaced_seq_count += 1
		self.bad_seq_chars.append(seq_char)
		self.replaced_seq_chars_count += 1
	
	def cleaned_descriptions(self):
		self.cleaned_descriptions_count += 1
	
	def found_internal_stop(self, header):
		if header not in self.internal_stop_headers:
			self.internal_stop_headers.append(header)
                        self.internal_stop_seq_count += 1
                self.internal_stop_count += 1
	
	
	#################
	## Print stats ##
	#################
	def print_cleaning_stats(self):
		logging.info('STATS - Processed %s fasta sequences', self.entry_count)
		if self.replaced_header_count is not None:
			logging.info('STATS - Cleaned %s problematic headers with %s problematic characters - %s', self.replaced_header_count, self.replaced_header_chars_count, set(self.bad_header_chars))
		if self.replaced_seq_count is not None:
			logging.info('STATS - Cleaned %s problematic sequences with %s problematic characters - %s', self.replaced_seq_count, self.replaced_seq_chars_count, set(self.bad_seq_chars))
		if self.cleaned_descriptions_count is not None:
			logging.info('STATS - Cleaned %s descriptions from fasta headers', self.cleaned_descriptions_count)
		if self.internal_stop_seq_count is not None:
			logging.info('STATS - Cleaned %s problematic sequences with %s internal stop codons', self.internal_stop_seq_count, self.internal_stop_count)



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
        	header = header.next()[1:].strip()
        	# join all sequence lines to one.
        	seq = "".join(s.strip() for s in faiter.next())
        	yield header, seq


if __name__ == '__main__':
	main()
