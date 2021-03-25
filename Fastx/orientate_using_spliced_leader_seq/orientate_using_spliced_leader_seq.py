#!/usr/bin/python
DESCRIPTION = '''
Will orientate given sequences using a provided spliced leader seq (i.e. will revcomp seq if needed to get spliced leader seq into correct orientation
Step:
	1. Check if spliced leader sequecne is <= max_from_end along the fwd fasta seq. If it is not,
	2. Check if spliced leader sequecne is <= max_from_end along the RevComp of the fasta seq. If it is not,
	3. Warn the user, do not output fasta seq.
'''
import sys
import argparse
import logging
from itertools import groupby
from Bio.Seq import Seq


# Pass command line arguments. 
def main():
	parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=DESCRIPTION)
	parser.add_argument('-i', '--fasta_in', metavar='in.fasta.txt', type=argparse.FileType('r'), default=sys.stdin, required=False, help='Output file (default: %(default)s)')
	parser.add_argument('-o', '--fasta_out', metavar='out.fasta', type=argparse.FileType('w'), default=sys.stdout, required=False, help='Output file (default: %(default)s)')
	parser.add_argument('-s', '--spliced_leader', metavar='ATGC', type=str, required=True, help='Spliced leader sequence (default: %(default)s)')
	parser.add_argument('-m', '--max_from_end', metavar=50, type=int, required=True, help='Max distance of spliced leader from 5-prime end of sequence (default: %(default)s)')
	parser.add_argument('--debug', action='store_true', required=False, help='Print DEBUG info (default: %(default)s)')
	args = parser.parse_args()
	
	 # Set up basic debugger
	logging.basicConfig(format='#[%(levelname)s]: %(message)s', stream=sys.stderr)
	if args.debug:
		logging.getLogger().setLevel(logging.DEBUG)
	else:
		logging.getLogger().setLevel(logging.INFO)
	
	logging.debug('%s', args) ## DEBUG
	
	orientate_using_spliced_leader_seq(args.fasta_in, args.fasta_out, args.spliced_leader, args.max_from_end)



def orientate_using_spliced_leader_seq(in_fasta, out_fasta, spliced_leader, max_from_end):
	for header, seq in fasta_iter(in_fasta):
		if spliced_leader in seq:
			pos = seq.index(spliced_leader)+1
			if pos <= max_from_end:
				out_fasta.write('>' + header + '\n')
				out_fasta.write(seq + '\n')
				logging.debug('Fwd - Leader seq found at position %s in %s: %s', pos, header, seq) ## DEBUG
				continue
		
		seq_rc = str(Seq(seq).reverse_complement())
		if spliced_leader in seq_rc:
			pos = seq_rc.index(spliced_leader)+1
			if pos <= max_from_end:
				out_fasta.write('>' + header + '\n')
				out_fasta.write(seq_rc + '\n')
				logging.debug('RevComp - Leader seq found at position %s in %s: %s', pos, header, seq_rc) ## DEBUG
				continue
		
		logging.info('No leader seq found in %s: %s', header, seq) ## INFO


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
