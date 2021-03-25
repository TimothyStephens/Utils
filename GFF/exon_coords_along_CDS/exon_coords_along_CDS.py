#!/usr/bin/env python2
DESCRIPTION = '''
Takes a gff3 file and returns the bed coords of each exon along the CDS (i.e. which parts of the CDS are from the same exon in the genome).

Takes a *.gff3 file with the genes of interest (only used "CDS" features) and return a roughtly *.bed formated file with 
the corrds of each exon as well as some extra intron/exon length information. 

## bed formated-based output (example of 3 exon gene and single-exon gene)
seqid	start	end	previous_exon_length	intron_length	next_exon_length
cds.1	0	10	.			10		100
cds.1	10	25	100			15		250
cds.1	25	100	250			75		.
cds.2	0	100	.			100		.
# '.' in *_exon_length column means that the exon is first or last in the gene, thus do not have previous or next exons. 

## Example (shortened) gene GFF input
CDS.1   1   10   +
CDS.2   20  30   +

CDS:   1                 10                  11                  20 
       |-----------------|                   |-------------------|  
      |A|T G C A T G C A|T|G C A T G C A T G|C|A T G C A T G C A|T|G C A T G C A T G C
      |||               |||                 |||                 ||| 
0:    0|1               9|10               19|20               29|30
1:     1                 10                  20                  30 

See https://www.biostars.org/p/84686

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
	parser.add_argument('-i', '--input', metavar='input.txt', 
		required=False, default=sys.stdin, type=lambda x: __parse_file_check_compression(x, 'r'), 
		help='Input GFF3 [gzip] file (default: stdin)'
	)
	parser.add_argument('-o', '--out', metavar='output.txt', 
		required=False, default=sys.stdout, type=lambda x: __parse_file_check_compression(x, 'w'), 
		help='Output bed file with 0-based coords of exons along CDS (default: stdout)'
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
	
	splice_site_positions_along_CDS(args.input, args.out)
	


def splice_site_positions_along_CDS(gff3_file, out_coords, use_ftype='CDS'):
	gene_dict = {}
	
	for line in gff3_file:
		line = line.strip()
		if not line or line.startswith('#'):
			continue
		logging.debug('%s', line)
		
		seqid, source, ftype, start, end, score, strand, phase, attributes = parse_GFF3_line(line)
		if ftype != use_ftype: # Ignore if not the feature type we want
			continue
		logging.debug('%s', attributes)
		
		Parent_id = attributes["Parent"]
		if Parent_id not in gene_dict.keys():
			gene_dict[Parent_id] = []
		gene_dict[Parent_id].append([seqid, start, end, strand])
		
	# For each gene in GFF3_file loop over list of features (forward for + strand and reverse for - strand) and print splice site positions.
	for gene_id, feat_list in gene_dict.iteritems():
		pos = 0
		if len(feat_list) <= 1: # Ignore single-exon genes
			intron_length = ((feat_list[0][2] - feat_list[0][1]) + 1)
			out_coords.write('%s\t%s\t%s\t%s\t%s\t%s\n' % (gene_id, pos, intron_length, '.', intron_length, '.'))
			continue
		
		if feat_list[0][3] == '+': # '+' strand
			feat_list_sorted = sorted(feat_list, key=lambda x: x[1])
			for i, feat in enumerate(feat_list_sorted):
				intron_length = ( (feat[2] - feat[1]) + 1 )
				
				# Get size of previous exon. Set to '.' if this is the first (or only) exon.
				if i == 0:
					previous_exon_length = '.'
				else:
					previous_exon_length = ((feat[1] - feat_list_sorted[i-1][2]) + 1) # (current exon start) - (previous exon end)
				
				# Get size of next exon. Set to '.' if this is the last (or only) exon.
				if i == (len(feat_list_sorted)-1):
					next_exon_length = '.'
				else:
					next_exon_length = ((feat_list_sorted[i+1][1] - feat[2]) + 1) # (next exon start) - (current exon end)
				
				# Print results and iterate pos count
				out_coords.write('%s\t%s\t%s\t%s\t%s\t%s\n' % (gene_id, pos, pos+intron_length, previous_exon_length, intron_length, next_exon_length))
				pos += intron_length
		else: # '-' strand
			feat_list_sorted = sorted(feat_list, key=lambda x: x[1], reverse=True)
			for i, feat in enumerate(feat_list_sorted):
				intron_length = ( (feat[2] - feat[1]) + 1 )
				
				# Get size of previous exon. Set to '.' if this is the first (or only) exon - Remember order of exons is reversed (as it is '-' strand gene)
				if i == 0:
					previous_exon_length = '.'
				else:
					previous_exon_length = ((feat_list_sorted[i-1][2] - feat[1]) + 1) # (previous exon end) - (current exon start)
				
				# Get size of next exon. Set to '.' if this is the last (or only) exon - Remember order of exons is reversed (as it is '-' strand gene)
				if i == (len(feat_list_sorted)-1):
					next_exon_length = '.'
				else:
					next_exon_length = ((feat[2] - feat_list_sorted[i+1][1]) + 1) # (current exon end) - (next exon start)
				
				# Print results and iterate pos count
				out_coords.write('%s\t%s\t%s\t%s\t%s\t%s\n' % (gene_id, pos, pos+intron_length, previous_exon_length, intron_length, next_exon_length))
				pos += intron_length






def parse_GFF3_line(gff3_line):
	'''
	Parse gff3 formated line from file. Assume line is actually gff3 line and not blank or comment
	'''
	seqid, source, ftype, start, end, score, strand, phase, attributes = gff3_line.split('\t')
	start = int(start)
	end = int(end)
	attributes_split = {x.split('=')[0]:x.split('=')[1] for x in attributes.split(';') if x}
	return seqid, source, ftype, start, end, score, strand, phase, attributes_split



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
