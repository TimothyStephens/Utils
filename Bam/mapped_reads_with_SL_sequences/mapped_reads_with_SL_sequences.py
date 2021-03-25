#!/usr/bin/env python2
DESCRIPTION = '''
Takes a bam file and iterates over each read that aigns to the sequences of interest, checking each read for the provided SL sequence motif.

OUTPUT: 1-based - first base after addition site (i.e. SL is added in from of this position)
DEBUG:  0-based

pysam documentation: https://pysam.readthedocs.io/en/latest/api.html#pysam.AlignedSegment
'''
import sys
import os
import argparse
import logging
import pysam
import gzip

## Pass arguments.
def main():
	# Pass command line arguments. 
	parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=DESCRIPTION)
	parser.add_argument('-b', '--bam', metavar='aligned_reads.bam', 
		required=True, type=argparse.FileType('r'), 
		help='Aligned bam file with associated index (Required)'
	)
	parser.add_argument('-i', '--seq_names', metavar='seq_names.txt', 
		required=False, default=sys.stdin, type=lambda x: __parse_file_check_compression(x, 'r'), 
		help='Sequences to check for SL sequences (default: %(default)s)'
	)
	parser.add_argument('-o', '--out', metavar='output.txt', 
		required=False, default=sys.stdout, type=lambda x: __parse_file_check_compression(x, 'w'), 
		help='Output file with info about detected SL sequences (default: stdout)'
	)
	parser.add_argument('--info', metavar='output.info.txt', 
		required=False, type=lambda x: __parse_file_check_compression(x, 'w'),  
		help='Output file with extra info about detected SL sequences (default: Not output)'
	)
	parser.add_argument('-s', '--sequence', metavar='ATGC',
		required=True, type=str, 
		help='SL sequence to search for (default: %(default)s)'
	)
	parser.add_argument('--debug', action='store_true', 
		required=False, 
		help='Print DEBUG info (default: %(default)s)'
	)
	args = parser.parse_args()
	
	# Set up basic debugger
	logFormat = "[%(levelname)s]: %(message)s"
	logging.basicConfig(format=logFormat, stream=sys.stderr, level=logging.INFO)
	if args.debug:
		logging.getLogger().setLevel(logging.DEBUG)
	
	logging.debug('%s', args) ## DEBUG
	
	mapped_reads_with_SL_sequences(args.bam, args.seq_names, args.out, args.info, args.sequence)
	
	
def mapped_reads_with_SL_sequences(bam_file, seq_names_file, out_file, info_file, sequence):
	samfile = pysam.AlignmentFile(bam_file, "rb")
	
	# Write output file headers
	out_file.write("#ref_id\tpos\tpos_read_coverage\tpos_read_with_SL\n")
	if info_file is not None:
		info_file.write("#query_name\tquery_sequence\tread_group\tref_name\treference_start\treference_end\taligned_pairs\treference_positions\tquery_leader_seq_start\tquery_leader_seq_end\tref_leader_seq_end\tadjusted_query_leader_seq_end\tadjust_query_leader_seq_end_by\n")
	
	# FOR each seq to check
	for line in seq_names_file:
		seqid = line.strip()
		# Ignore blank or comment lines.
		if not seqid or seqid.startswith("#"):
			continue
		
		SL_positions = {}
		
		logging.info('Processing %s', seqid)
		
		# FOR each read aligned to seqid
		for read in samfile.fetch(seqid):
			#logging.debug('read:%s', read)
			
			# Query (read) seq information
			query_name = read.query_name           # the query template name (None if not present)
			query_sequence = read.query_sequence   # read sequence bases, including soft clipped bases (None if not present).
			try:
				read_group = read.get_tag("RG")        # retrieves data from the optional alignment section given a two-letter tag denoting the field.
			except KeyError:
				read_group = None
			
			# Reference seq information
			ref_name = read.reference_name         # reference name
			reference_start = read.reference_start # 0-based leftmost coordinate
			reference_end = read.reference_end     # aligned reference position of the read on the reference genome
			                                       # reference_end points to one past the last aligned residue. Returns None if not available (read is unmapped or no cigar alignment present).
			
			# Get info about where along the reference the query sequence aligns
			aligned_pairs = read.get_aligned_pairs() # a list of aligned read (query) and reference positions.
			reference_positions = read.get_reference_positions() # a list of reference positions that this read aligns to
			
			# Ignore reads without SL sequences in them
			if sequence not in query_sequence:
				continue
			
			# Get position of SL sequence in Query (read)
			query_leader_seq_start = query_sequence.index(sequence)
			query_leader_seq_end = query_leader_seq_start + len(sequence) # 0-based exclusive position (i.e. if taken literally [in a 0-based position index] this will be the position after the last base in 'sequence')
			
			# Get last position of SL sequence in Reference (might have to move further along Reference if Query(read) is softclipped)
			# Iterate over tuple(query_pos, ref_pos) pairs and find a which position along reference we find query_leader_seq_end - keep iterating through list if at query_leader_seq_end query is softmasked
			ref_leader_seq_end = None
			adjusted_query_leader_seq_end = None
			adjust_query_leader_seq_end_by = None
			for pos in aligned_pairs:
				if pos[0] >= query_leader_seq_end and pos[1] is not None:
					ref_leader_seq_end = pos[1]
					adjusted_query_leader_seq_end = pos[0]
					adjust_query_leader_seq_end_by = adjusted_query_leader_seq_end - query_leader_seq_end
					break # We have found first position of query_leader_seq_end OR first position after that isnt softclipped
			
			# query_name, query_sequence, read_group, ref_name, reference_start, reference_end, aligned_pairs, reference_positions, query_leader_seq_start, query_leader_seq_end, ref_leader_seq_end, adjusted_query_leader_seq_end, adjust_query_leader_seq_end_by
			#logging.debug('SL found in read\t%s', 
			#		'\t'.join([str(x) for x in [query_name, query_sequence, read_group, ref_name, reference_start, reference_end, aligned_pairs, reference_positions, query_leader_seq_start, query_leader_seq_end, ref_leader_seq_end, adjusted_query_leader_seq_end, adjust_query_leader_seq_end_by]]))
			
			# Check if we found a position in the Reference sequence
			if ref_leader_seq_end is not None:
				SL_positions[ref_leader_seq_end] = SL_positions.get(ref_leader_seq_end, 0) + 1
			else:
				logging.warning("SL found but has soft clipped 3-prime end. Ignoring these reads for now! - query_name:%s, query_leader_seq_start:%s, query_leader_seq_end:%s, ref_name:%s, ref_leader_seq_end:%s",
					query_name, query_leader_seq_start, query_leader_seq_end, ref_name, ref_leader_seq_end)
			
			# Write this reads (if ref_leader_seq_end != None) into to info file if required.
			if info_file is not None and ref_leader_seq_end is not None:
				info_file.write('\t'.join([str(x) for x in [query_name, query_sequence, read_group, ref_name, reference_start, reference_end, aligned_pairs, reference_positions, query_leader_seq_start, query_leader_seq_end, ref_leader_seq_end, adjusted_query_leader_seq_end, adjust_query_leader_seq_end_by]]) + '\n')
		
		# Write all positions with SL seqs to out file
		for pos in sorted(SL_positions.keys()):
			# Get coverage at pos
			pos_read_coverage = samfile.count(seqid, pos, pos+1)
			
			out_file.write('\t'.join([seqid, str(pos+1), str(pos_read_coverage), str(SL_positions[pos])])+'\n')



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
