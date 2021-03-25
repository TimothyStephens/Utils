#!/usr/bin/env python2
DESCRIPTION = '''
Takes an indexed bam file with aligned reads and check the regions given in a bed formated file for evidence of misassembly. 
Each feature is broken up into windows and any windows with reads that map completely across them are defined as being evidence of misassembly.

Assume misassembled region == no reads alinged across the whole window

Output:
# out (one line per sequence)
seqid\tstart\tend\tclassification\tbad_positions\n

# position_info (if file name provided; one line per window)
seqid\tpos_start\tpos_end\tok_read_counts\tbad_read_counts\n


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
	parser.add_argument('-b', '--bam', metavar='aligned_reads.bam', type=argparse.FileType('r'), required=True, 
		help='Aligned bam file with associated index (Required)')
	parser.add_argument('-r', '--regions', metavar='regions.bed', type=lambda x: __parse_file_check_compression(x, 'r'), default=sys.stdin, required=False, 
		help='Regions to check for misassemblies [can be gzipped] (default: %(default)s)')
	parser.add_argument('-o', '--out', metavar='output.txt', type=lambda x: __parse_file_check_compression(x, 'w'), default=sys.stdout, required=False, 
		help='Output file with info about detected misassemblies [can be gzipped] (default: stdout)')
	parser.add_argument('-p', '--position_info', metavar='output.position_info.txt', type=lambda x: __parse_file_check_compression(x, 'w'), required=False, 
		help='Output info about each position with misassemblies [can be gzipped] (default: stdout)')
	parser.add_argument('--region_size', type=int, default=20, required=False, 
		help='Size of window to check for read mapping coverage (default: %(default)s)')
	parser.add_argument('--min_ok_reads', type=int, default=10, required=False, 
		help='Minimum number of reads for a window to be NOT misassembled (default: %(default)s)')
	parser.add_argument('--debug', action='store_true', required=False, 
		help='Print DEBUG info (default: %(default)s)')
	args = parser.parse_args()
	
	# Set up basic debugger
	logFormat = "[%(levelname)s]: %(message)s"
	logging.basicConfig(format=logFormat, stream=sys.stderr, level=logging.INFO)
	if args.debug:
		logging.getLogger().setLevel(logging.DEBUG)
	
	logging.debug('%s', args) ## DEBUG
	
	check_4_misassemblies_between_two_points(args.bam, args.regions, args.out, args.position_info, args.region_size, args.min_ok_reads)
	


def check_4_misassemblies_between_two_points(bam_file, regions_file, out_file, position_info_file, region_size, min_ok_reads):
	samfile = pysam.AlignmentFile(bam_file, "rb")
	
	# Write output file headers
	out_file.write("seqid\tstart\tend\tclassification\tbad_positions\n")
	if position_info_file is not None:
		position_info_file.write("seqid\tpos_start\tpos_end\tok_read_counts\tbad_read_counts\n")
	
	# FOR each region to check
	for line in regions_file:
		line = line.strip()
		# Ignore blank or comment lines.
		if not line or line.startswith("#"):
			continue
		
		seqid, start, stop = line.split('\t')
		start = int(start)
		stop = int(stop)
		bad_positions = []
		
		# FOR each window within each region
	 	for win_start in range(start, (stop-region_size)+1):
			win_stop = win_start+region_size
			passed_reads = 0
			failed_reads = 0
			
			logging.debug('seqid:%s win_start:%s win_stop:%s', seqid, win_start, win_stop)
			
			# FOR each read within window
			for read in samfile.fetch(seqid, win_start, win_stop):
				#logging.debug('read:%s', read)
				reference_start = read.reference_start # 0-based leftmost coordinate
				reference_end = read.reference_end     # aligned reference position of the read on the reference genome
				                                       # reference_end points to one past the last aligned residue. Returns None if not available (read is unmapped or no cigar alignment present).
				
				# Check if read aligned over whole region or just part of it.
				if reference_start <= win_start and reference_end >= win_stop:
					passed_reads += 1
					logging.debug('PASS reference_start:%s reference_end:%s', reference_start, reference_end)
				else:
					failed_reads += 1
					logging.debug('FAIL reference_start:%s reference_end:%s', reference_start, reference_end)
			
			logging.debug('seqid:%s win_start:%s win_stop:%s passed_read:%s failed_reads:%s', seqid, win_start, win_stop, passed_reads, failed_reads)
			
			# Test if we have enough "good" reads in window to call it not a misassembly. 
			if passed_reads < min_ok_reads:
				bad_positions.append(win_start)
			
			# Write position_info if file given
			if position_info_file is not None:
				position_info_file.write('\t'.join([seqid, str(win_start), str(win_stop), str(passed_reads), str(failed_reads)])+'\n')
		
		# Write results for region
		if len(bad_positions) > 0:
			out_file.write('\t'.join([seqid, str(start), str(stop), "Failed_min_ok_reads", ','.join([str(x) for x in bad_positions])])+'\n')
		else:
			out_file.write('\t'.join([seqid, str(start), str(stop), "Passed_min_ok_reads", "NA"])+'\n')



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
