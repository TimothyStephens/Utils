#!/usr/bin/env python2
DESCRIPTION = '''
Returns protein sequences that are 'complete' i.e. contains start 'M' and stop '*' codons.
Can also invert the results i.e. return sequences that are NOT 'complete'.
'''
import sys
import argparse
from itertools import groupby

# Pass command line arguments. 
def main():
	parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=DESCRIPTION)
	parser.add_argument('-i', '--fasta_in', metavar='in.fasta', type=argparse.FileType('r'), default=sys.stdin, required=False, help='Input fasta file (default: stdin)')
	parser.add_argument('-o', '--fasta_out', metavar='out.fasta', type=argparse.FileType('w'), default=sys.stdout, required=False, help='Output fasta file (default: stdout)')
	parser.add_argument('-v', '--invert', action='store_true', required=False, help='Return sequences that are NOT complete (default: %(default)s)')
	args = parser.parse_args()
	
	get_complete_pep_seqs(args.fasta_in, args.fasta_out, args.invert)


'''
Return 'complete' protein sequences.
'''
def get_complete_pep_seqs(in_fasta, out_fasta, invert):
	
	# Pass fasta file
	for header, seq in fasta_iter(in_fasta):
		if seq.startswith('M') and seq.endswith('*') and not invert: ## If seq starts with 'M' (start codon) and '*' (stop codon)
			out_fasta.write('>' + header + '\n')
			out_fasta.write(seq + '\n')
		elif (not seq.startswith('M') or not seq.endswith('*')) and invert:
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
