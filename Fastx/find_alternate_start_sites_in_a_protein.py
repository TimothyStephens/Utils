#!/usr/bin/env python2
DESCRIPTION = '''
Takes a set of input proteins and outputs the positions of alternate in-frame start positions. 
i.e. each methionine in the prot seq is an alternate start position.

Outputs bed coords from each alternative start (methionine) position to the end of the sequence. 
'''
import sys
import argparse
from itertools import groupby
import re


# Pass command line arguments. 
def main():
	parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=DESCRIPTION)
	parser.add_argument('-i', '--input_fasta', metavar='input.fasta', type=argparse.FileType('r'), default=sys.stdin, required=False, help='Input fasta file (default: stdin)')
	parser.add_argument('-o', '--output_bed', metavar='output.bed', type=argparse.FileType('w'), default=sys.stdout, required=False, help='Output bed file. Coords based on fasta file (default: stdout)')
	args = parser.parse_args()
	
	find_alternate_start_sites_in_a_protein(args.input_fasta, args.output_bed)



def find_alternate_start_sites_in_a_protein(fasta_fh, output_fh):
	for header, seq in fasta_iter(fasta_fh):
		alt_start_pos = [m.start() for m in re.finditer('M', seq)]
		for s in alt_start_pos:
			feature_name=header+"_altStart_"+str(s)
			# seq, start, end, name, score, strand
			output_fh.write(header+'\t'+str(s)+'\t'+str(len(seq))+'\t'+feature_name+'\t0\t+\n')




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
