#!/usr/bin/env python2
DESCRIPTION = '''
Checks the top 1M lines of a compressed/uncompressed read file for the presence of adapters.
'''
import sys
import argparse
import logging
import os.path
import gzip
from itertools import groupby

## Pass arguments.
def main():
	# Pass command line arguments. 
	parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=DESCRIPTION)
	parser.add_argument('-f', '--fastq', metavar='reads.fastq.gz', type=lambda x: __pass_file_check_compression(parser, x), required=True, nargs='+', help='Input fastq file/s (can be gziped)')
	parser.add_argument('-a', '--adapters', type=argparse.FileType('r'), required=True, help='Adapter sequences to search for in fastq file/s')
	parser.add_argument('-o', '--adapters_out', default=None, type=argparse.FileType('w'), required=False, help='Adapter sequences found in fastq file/s')
	parser.add_argument('-n', '--number_reads', default=200000, type=int, required=False, help='Number of reads to check (default: %(default)s)')
	parser.add_argument('-r', '--report_read_count', default=1, type=int, required=False, help='Number of reads (across all files) with an adapter needed before that adapter is printed to output adapter file (default: %(default)s)')
	parser.add_argument('-q', '--quiet', action='store_true', required=False, help='Dont print any info to stdout (default: %(default)s)')
	parser.add_argument('--debug', action='store_true', required=False, help='Print DEBUG info (default: %(default)s)')
	args = parser.parse_args()
	
	# Set up basic debugger
	logFormat = "[%(levelname)s]: %(message)s"
	logging.basicConfig(format=logFormat, stream=sys.stderr, level=logging.INFO)
	if args.debug:
		logging.getLogger().setLevel(logging.DEBUG)
	elif args.quiet:
		logging.getLogger().setLevel(logging.ERROR)
	
	logging.debug('%s', args) ## DEBUG
	
	# Load adapter seqs into a list. This is just to preserve order.
	adapters = [[x, y] for x, y in fasta_iter(args.adapters)]
	logging.debug('%s', adapters) ## DEBUG
	
	search_fastq_files_for_adapters(args.fastq, adapters, args.number_reads, args.report_read_count, args.adapters_out)
	
	


def search_fastq_files_for_adapters(fastq_fh_list, adapters, number_reads_to_process, report_read_count, adapters_out):
	'''
	Search fo each adapter in the given fastq files.
	Writes the adapters found in the fastq files to a file.
	'''
	
	total_read_count = {x:0 for x, y in adapters}
	
	for fastq_fh in fastq_fh_list:
		logging.info('') ## INFO
		logging.info('Processing file: %s', fastq_fh.name) ## INFO
		
		reads_seen = 0
		read_count = {x:0 for x, y in adapters}
		
		# Take just the 'sequence' from each passed read
		for read_name, read_seq, read_opt, read_qual in fastq_iter(fastq_fh):
			
			# Check for each adapter in read sequence
			for adapter_name, adapter_seq in adapters:
				if adapter_seq in read_seq:
					total_read_count[adapter_name] += 1
					read_count[adapter_name] += 1
			
			# Break bottom loop if we have checked enough reads.
			reads_seen += 1
			if reads_seen == number_reads_to_process:
				break
		
		for adapter_name, adapter_seq in adapters:
			logging.info('\t%s\t%s', read_count[adapter_name], adapter_name) ## INFO
	
	if adapters_out is not None:
		for adapter_name, adapter_seq in adapters:
			if total_read_count[adapter_name] >= report_read_count:
				adapters_out.write('>' + adapter_name + '\n')
				adapters_out.write(adapter_seq + '\n')
	


def __pass_file_check_compression(parser, arg):
	'''
	Check passed file name exists and opens using gzip when needed. 
	'''
	if not os.path.exists(arg):
		parser.error("The file %s does not exist!" % arg)
	else:
		## open with gzip if it has the *.gz extension
		if arg.endswith(".gz"):
			return gzip.open(arg, 'rb')
		else:
			return open(arg, 'r')



def fastq_iter(fh):
	'''
	Given a fastq file handle, yield a list of lines for 
	each read.
	['name', 'sequence', 'optional', 'quality']
	
	Code from: https://www.biostars.org/p/317524/
	'''
	n = 4
	lines = []
	for line in fh:
		lines.append(line.rstrip())
		if len(lines) == n:
			yield lines
			lines = []



def fasta_iter(fh):
        '''
        Given a fasta file handle, yield tuples of header, sequence
        Clears description from seq name.
        
        Code from: https://www.biostars.org/p/710/
        Updated: 07/08/2019
        Version: 0.2
        '''
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
