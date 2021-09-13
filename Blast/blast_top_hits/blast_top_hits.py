#!/usr/bin/env python2
DESCRIPTION = '''
blast_top_hits - Filters blast output, taking top X subjects and top X hits per subject.

NOTE:
	- Expects file is sorted, with all subject hits ordered from most to least significant
	- Expects query to be in column 1
	- Expects tab delimted file (-outfmt 6)

'''
import sys
import os
import argparse
import logging
import gzip
from itertools import groupby

## Pass arguments.
def main():
	# Pass command line arguments. 
	parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=DESCRIPTION)
	parser.add_argument('-i', '--blast_in', default=sys.stdin, metavar='blast.outfmt6', type=lambda x: __parse_file_check_compression(x, 'r'), required=False, help='Input [gzip] blast file (default: stdin)')
	parser.add_argument('-o', '--blast_out', default=sys.stdout, metavar='blast_filtered.outmft6', type=lambda x: __parse_file_check_compression(x, 'w'), required=False, help='Output [gzip] blast file (default: stdout)')
	parser.add_argument('-s', '--num_subjects', default=1, type=int, required=False, help='Number of subjects per query to retain (default: %(default)s)')
	parser.add_argument('-n', '--num_hits', default=1, type=int, required=False, help='Number hits to retain per subject (default: %(default)s)')
	parser.add_argument('--debug', action='store_true', required=False, help='Print DEBUG info (default: %(default)s)')
	args = parser.parse_args()
	
	# Set up basic debugger
	logFormat = "[%(levelname)s]: %(message)s"
	logging.basicConfig(format=logFormat, stream=sys.stderr, level=logging.INFO)
	if args.debug:
		logging.getLogger().setLevel(logging.DEBUG)
	
	logging.debug('%s', args) ## DEBUG

	for query_id, filtered_hits in top_hit_iter(args.blast_in, args.num_subjects, args.num_hits):
		for hit in filtered_hits:
			args.blast_out.write('\t'.join(hit) + '\n')
	args.blast_in.close()
	args.blast_out.close()
	

def top_hit_iter(blast_fh, num_subjects, num_hits):
	"""
	Takes BLAST filehandle and yields lists of hits which have been filtered by num_subjects and num_hits.
	Allows for quick traversal and filtering of very large BLAST output files.
	
	Version: 0.1simple
	Last Modified: 26/11/2019
	
	Arguments:
		blast_fh:       File handle with BLAST output "-outfmt 6".
	
	Yields:
	blast_list:     List of BLAST hits after filtering in appropriate format. 
	
	Note:   - Must be sorted by key_col (all entries with same key_col must be next to each other)
		- Ignores blank lines.
		- Does not transform columns (will not convert str to int e.g. for start/stop/etc.)

	"""
	delim='\t'
	for query_id, hits in groupby(blast_fh, lambda x: x.strip().split(delim)[0]):
		subjects_seen = 0
		filtered_hits = []
		
		for subject_id, hsps in groupby(hits, lambda l: l.strip().split(delim)[1]): # For each query iterate over subject seqs
			
			subjects_seen += 1
			if subjects_seen > num_subjects:
				break
			
			hsps_seen = 0
			for h in hsps: # For each subject iterate over HSPs
				logging.debug('subjects_seen: %s; hsps_seen: %s', subjects_seen, hsps_seen) ## DEBUG
				logging.debug('Query_id: %s - Subject_id: %s - HSP: %s', query_id, subject_id, h.strip()) ## DEBUG
				hsps_seen += 1
				if hsps_seen > num_hits:
					break
				
				filtered_hits.append(h.strip().split(delim))
				
		yield query_id, filtered_hits



def __parse_file_check_compression(fh, mode='r'):
	'''
	Open stdin/normal/gzip files - check file exists (if mode='r') and open using appropriate function.
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
