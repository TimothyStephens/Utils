#!/usr/bin/env python2
DESCRIPTION = '''
blast_hit_coverage - Filters blast output, taking hits which cover > X% of the query and > Y% of the subject sequence.

NOTE:
	- Expects file is sorted, with all subject hits ordered from most to least significant
	- Expects tab delimted file.
	- Expects custom blast outfmt:
		-outfmt "6 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore qlen slen"

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
	parser.add_argument('-i', '--blast_in', metavar='blast.outfmt6', default=sys.stdin, type=lambda x: __parse_file_check_compression(x, 'r'), required=False, help='Input [gzip] blast file (default: stdin)')
	parser.add_argument('-o', '--blast_out', metavar='blast_filtered.outmft6', default=sys.stdout, type=lambda x: __parse_file_check_compression(x, 'w'), required=False, help='Output [gzip] blast file (default: stdout)')
	parser.add_argument('-q', '--query_cov', default=0.0, type=float, required=False, help='Return hits that cover > X%% of the query sequence (default: %(default)s)')
	parser.add_argument('-s', '--subject_cov', default=0.0, type=float, required=False, help='Return hits that cover > Y%% of the subject sequence (default: %(default)s)')
	parser.add_argument('--debug', action='store_true', required=False, help='Print DEBUG info (default: %(default)s)')
	args = parser.parse_args()
	
        # Set up basic debugger
	logFormat = "[%(levelname)s]: %(message)s"
	logging.basicConfig(format=logFormat, stream=sys.stderr, level=logging.INFO)
	if args.debug:
		logging.getLogger().setLevel(logging.DEBUG)
	
	logging.debug('%s', args) ## DEBUG

	query_subject_hit_cov_filter(args.blast_in, args.blast_out, args.query_cov, args.subject_cov)



def query_subject_hit_cov_filter(blast_fh, blast_out_fh, query_cov, subject_cov):
	# Percent to proportion
	query_cov = query_cov/100
	subject_cov = subject_cov/100
	
	for line in blast_fh:
		line = line.strip()
		if not line or line.startswith('#'):
			continue
		
		qseqid, sseqid, pident, length, mismatch, gapopen, qstart, qend, sstart, send, evalue, bitscore, qlen, slen = line.split('\t')
		
		qstart = int(qstart)
		qend = int(qend)
		qlen = int(qlen)
		sstart = int(sstart)
		send = int(send)
		slen = int(slen)
		
		# Invert start and end if the are reversed (happen for blast using nucl sequences)
		qlen_hit = 0
		slen_hit = 0
		# Query
		if qstart < qend:
			qlen_hit = (qend - qstart)+1
		else:
			qlen_hit = (qstart - qend)+1
		# Subject
		if sstart < send:
			slen_hit = (send - sstart)+1
		else:
			slen_hit = (sstart - send)+1
		
		# Filter
		if qlen_hit > (qlen * query_cov) and slen_hit > (slen * subject_cov):
			blast_out_fh.write(line+'\n')
		#else:
		#	print line



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
