#!/usr/bin/env python2
DESCRIPTION = '''
Takes a fasta file (either a file or from stadin) and returns only the sequecnes which match the names provided.
'''
import sys
import argparse
from itertools import groupby

# Pass command line arguments. 
def main():
	parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=DESCRIPTION)
	parser.add_argument('-f', '-s', '--seq_names', metavar='seq_names.txt', type=argparse.FileType('r'), required=True, help='Return sequences from list')
	parser.add_argument('-i', '--fasta_in', metavar='input.fasta', type=argparse.FileType('r'), default=sys.stdin, required=False, help='Input fasta file (default: stdin)')
	parser.add_argument('-o', '--fasta_out', metavar='output.fasta', type=argparse.FileType('w'), default=sys.stdout, required=False, help='Output (filtered) fasta file (default: stdout)')
	parser.add_argument('-v', '--invert', action='store_true', required=False, help='Return sequences not in --seq_names (default: %(default)s)')
	args = parser.parse_args()
	
	get_fasta(args.fasta_in, args.fasta_out, args.seq_names, args.invert)


'''
Write onlt the target sequecnes in 'seq_names'
'''
def get_fasta(in_fasta, out_fasta, seq_names_fh, invert):
	
	# Get seq names
	seq_names = []
	for line in seq_names_fh:
		line = line.strip()
		if not line or line.startswith('#'): # Ignore lines thta are blank or start with '#'
			continue
		seq_names.append(line)
	seq_names = set(seq_names)
	
	# Pass fasta file
	for header, seq in fasta_iter(in_fasta):
		if header in seq_names and not invert: ## If header in seq_names and we arent inverting the search (i.e. we want the seqs in seq_names).
			out_fasta.write('>' + header + '\n')
			out_fasta.write(seq + '\n')
		elif header not in seq_names and invert: ## If header NOT in seq_names and we ARE inverting the search (i.e. we DONT want the seqs in seq_names).
			out_fasta.write('>' + header + '\n')
			out_fasta.write(seq + '\n')



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
