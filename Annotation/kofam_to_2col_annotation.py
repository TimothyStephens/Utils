#!/usr/bin/env python2
DESCRIPTION = '''
Takes the kofam_scan mapper putput file and returns a 2 column annotation file.

NOTE:
	- Ignores seqs with no annotations.
	- Combines multiple hits into a single line.
'''
import sys
import os
import argparse
import gzip
import logging

## Pass arguments.
def main():
	# Pass command line arguments. 
	parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=DESCRIPTION)
	parser.add_argument('-i', '--input', default=sys.stdin, metavar='input.txt', type=lambda x: __parse_file_check_compression(x, 'r'), required=False, help='Input [gzip] file (default: stdin)')
	parser.add_argument('-o', '--output', default=sys.stdout, metavar='output.txt', type=lambda x: __parse_file_check_compression(x, 'w'), required=False, help='Output [gzip] file (default: stdout)')
	parser.add_argument('-d', '--delim', default=',', type=str, required=False, help='Delimiter to use for pfam domain ids in output (default: %(default)s)')
	parser.add_argument('--debug', action='store_true', required=False, help='Print DEBUG info (default: %(default)s)')
	args = parser.parse_args()
	
	# Set up basic debugger
	if args.debug:
		logging.basicConfig(format='#%(levelname)s: %(message)s', stream=sys.stdout, level=logging.DEBUG)
	else:
		logging.basicConfig(format='#%(levelname)s: %(message)s', stream=sys.stdout, level=logging.INFO)
	
	logging.debug('%s', args) ## DEBUG
	
	kofam_to_2col_annotation(args.input, args.output, args.delim)



def kofam_to_2col_annotation(infile, outfile, kofamid_delim):
	kofam_annots = {}
	
	for line in infile:
		line = line.strip()
		if not line or line.startswith('#'): # Ignore blank and comment lines.
			continue
		
		# Kofam output format (tab sep; kofam id might not exist):
		# <seq id> [kofam id]
		line_split = line.split('\t')
		
		if len(line_split) == 1: # Ignore seq_ids that dont have hits.
			continue
		
		seq_id, kofam_id = line_split
		
		if seq_id not in kofam_annots.keys():
			kofam_annots[seq_id] = []
		kofam_annots[seq_id].append(kofam_id)
	
	# Write results
	for seqid, annots in kofam_annots.iteritems():
		outfile.write(seqid + '\t' + kofamid_delim.join(annots) + '\n')
	infile.close()
	outfile.close()



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
