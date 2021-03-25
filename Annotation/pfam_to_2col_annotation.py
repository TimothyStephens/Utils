#!/usr/bin/python
DESCRIPTION = '''
Takes the putput file from pfam_scan.pl, filter hits by evalue and returns a 2 column annotation file (one line per sequence; combines multiple hits into a single line).

NOTE:
	- If a pep has multiple hits to the same domain then that domain will appear multiple times in the annotation column.  
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
	parser.add_argument('-e', '--evalue', default=0.001, type=float, required=False, help='Max evalue (default: %(default)s)')
	parser.add_argument('--debug', action='store_true', required=False, help='Print DEBUG info (default: %(default)s)')
	args = parser.parse_args()
	
	# Set up basic debugger
	if args.debug:
		logging.basicConfig(format='#%(levelname)s: %(message)s', stream=sys.stdout, level=logging.DEBUG)
	else:
		logging.basicConfig(format='#%(levelname)s: %(message)s', stream=sys.stdout, level=logging.INFO)
	
	logging.debug('%s', args) ## DEBUG
	
	pfam_to_2col_annotation(args.input, args.output, args.delim, args.evalue)



def pfam_to_2col_annotation(infile, outfile, pfamid_delim, evalue_threshold):
	pfam_annots = {}
	
	for line in infile:
		line = line.strip()
		if not line or line.startswith('#'): # Ignore blank and comment lines.
			continue
		
		# Prfam output format (space sep):
		# <seq id> <alignment start> <alignment end> <envelope start> <envelope end> <hmm acc> <hmm name> <type> <hmm start> <hmm end> <hmm length> <bit score> <E-value> <significance> <clan>
		seq_id, alignment_start, alignment_end, envelope_start, envelope_end, hmm_acc, hmm_name, domain_type, hmm_start, hmm_end, hmm_length, bitscore, evalue, significance, clan = line.split()
		
		if float(evalue) >= evalue_threshold: # Ignore hits > max evalue threshold.
			continue
		
		if seq_id not in pfam_annots.keys():
			pfam_annots[seq_id] = []
		pfam_annots[seq_id].append(hmm_acc + '___' + hmm_name)
	infile.close()
	
	# Write results
	for seqid, annots in pfam_annots.iteritems():
		outfile.write(seqid + '\t' + pfamid_delim.join(annots) + '\n')
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
