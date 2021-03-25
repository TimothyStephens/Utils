#!/usr/bin/env python2
DESCRIPTION = '''
Takes a fasta file with long seqs and a fasta file with short sub-seq to search for in the long fasta file.
Returns a bed formateed file with the indentified subseq matches in each long fasta seq.

NOTE:
    - Will search each short seq against each long seq (very intensive and likely will be slow with lots of seqs)
'''
import sys
import os
import argparse
import logging
from itertools import groupby

# Pass command line arguments. 
def main():
	parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=DESCRIPTION)
	parser.add_argument('-q', '--query', metavar='short.fa', type=lambda x: __parse_file_check_compression(x, 'r'), required=True, help='Short (sub-)seqs fasta file (required)')
        parser.add_argument('-s', '--subject', metavar='long.fa', type=lambda x: __parse_file_check_compression(x, 'r'), default=sys.stdin, required=False, help='Long seqs fasta file (default: stdin)')
	parser.add_argument('-o', '--bed', metavar='output.fasta', type=lambda x: __parse_file_check_compression(x, 'w'), default=sys.stdout, required=False, help='Bed formatted matches of short seqs within long seqs (default: stdout)')
	parser.add_argument('--debug', required=False, action='store_true', help='Print DEBUG info (default: %(default)s)')
	args = parser.parse_args()
	
	# Set up basic debugger
	logFormat = "[%(levelname)s]: %(message)s"
	logging.basicConfig(format=logFormat, stream=sys.stderr, level=logging.INFO)
	if args.debug:
		logging.getLogger().setLevel(logging.DEBUG)

	logging.debug('%s', args) ## DEBUG
	
	find_subseq(args.query, args.subject, args.bed)


'''
Find query seqs in long seqs.
'''
def find_subseq(query_fasta, subject_fasta, bed_out):
	
	# Get short query seqs.
	query_seqs = []
        for header, seq in fasta_iter(query_fasta):
                query_seqs.append([header, seq])
	query_fasta.close()
	logging.debug('Query seqs: %s', query_seqs) ## DEBUG
	
	# For each long seq search for each of the short seqs.
	for subject_header, subject_seq in fasta_iter(subject_fasta):
                for query_header, query_seq in query_seqs:
			logging.debug('Finding matches for %s in %s', query_seq, subject_seq) ## DEBUG
			matches = find_matches(query_seq, subject_seq)
			logging.debug('Matches found: %s', matches) ## DEBUG
			for start, end in matches:
				bed_out.write(subject_header+"\t"+str(start)+"\t"+str(end)+"\t"+query_header+"\n")
	subject_fasta.close()
	bed_out.close()


'''
Find all matches between query string and subject string.
Returns start and end index of match (already bed formatted coords)

Based on code from: https://stackoverflow.com/questions/3873361/finding-multiple-occurrences-of-a-string-within-a-string-in-python

NOTE:
        - Allows overlapping hits
'''
def find_matches(query, subject):
	matches = []
	index = 0
	while index < len(subject):
		index = subject.find(query, index)
		if index == -1:
			break
		matches.append([index, index+len(query)])
		index += 1
	return matches



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


def __parse_file_check_compression(fh, mode='r'):
	'''
	Open stdin/normal/gzip files - check file exists (if mode='r') and open using appropriate function.
	
	NOTE: Still need to close file handles after use. Argparse doesnt close automatically.
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
