#!/usr/bin/env python2
DESCRIPTION = '''
Parses the Orthogroups.tsv file produced by Orthofinder and output the clusters in a one line per member format. 

# Inout format (Orthogroups.tsv):
Orthogroup	pep_file_1	pep_file_2	pep_file_3
OG00001		seq1, seq2	seq1		seq1
OG00002		seq3				seq2, seq3, seq4
OG00003						seq5

# Output format:
OG00001	pep_file_1	seq1
OG00001	pep_file_1	seq2
OG00001	pep_file_2	seq1
OG00001	pep_file_3	seq1
OG00002	pep_file_1	seq3
OG00002	pep_file_3	seq2
OG00002	pep_file_3	seq3
OG00002	pep_file_3	seq4
OG00003	pep_file_3	seq5

'''
import sys
import os
import argparse
import logging
import gzip

## Pass arguments.
def main():
	# Pass command line arguments. 
	parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=DESCRIPTION)
	parser.add_argument('-i', '--input', metavar='Orthogroups.tsv', 
		required=False, default=sys.stdin, type=lambda x: __parse_file_check_compression(x, 'r'), 
		help='Input Orthogroups.tsv [gzip] file (default: stdin)'
	)
	parser.add_argument('-o', '--out', metavar='output.txt', 
		required=False, default=sys.stdout, type=lambda x: __parse_file_check_compression(x, 'w'), 
		help='Output [gzip] file, one member per line (default: stdout)'
	)
	parser.add_argument('--debug', 
		required=False, action='store_true', 
		help='Print DEBUG info (default: %(default)s)'
	)
	args = parser.parse_args()
	
	# Set up basic debugger
	logFormat = "[%(levelname)s]: %(message)s"
	logging.basicConfig(format=logFormat, stream=sys.stderr, level=logging.INFO)
	if args.debug:
		logging.getLogger().setLevel(logging.DEBUG)
	
	logging.debug('%s', args) ## DEBUG
	
	Orthogroups_tsv_to_single_line(args.input, args.out)



def Orthogroups_tsv_to_single_line(orthogroup_tsv, out_file):
	# Get group names from header
	headers = orthogroup_tsv.readline().strip().split('\t')[1:]
	logging.debug('%s', headers)
	
	for line in orthogroup_tsv:
		line = line.strip() # NOTE: will also remove trailing tabs
		if not line or line.startswith('#'):
			continue
		
		line_split = line.split('\t')
		logging.debug('Processing %s', line_split)
		for i, group in enumerate(headers):
			# Break loop if we have run out of elements in list (i.e. all we had was trailing tabs that .strip() removed)
			if i+1 >= len(line_split):
				break
			# Ignore groups without members in this OG
			if not line_split[i+1]:
				continue
			logging.debug('Subset i:%s group:%s members:%s', i, group, line_split[i+1])
			
			members_split = line_split[i+1].split(', ')
			for member in members_split:
				out_file.write(line_split[0]+'\t'+group+'\t'+member+'\n')
			



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
