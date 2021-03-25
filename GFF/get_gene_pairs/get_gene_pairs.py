#!/usr/bin/python
DESCRIPTION = '''
Return pairs of adjacent genes on scaffolds with >1 gene i.e. [A, B] {B, C] [C, D] etc.
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
        parser.add_argument('-g', '--gff3', metavar='input.txt',
                required=False, default=sys.stdin, type=lambda x: __parse_file_check_compression(x, 'r'),
                help='Input [gzip] GFF3 file (default: stdin)'
        )
        parser.add_argument('-o', '--out', metavar='output.txt',
                required=False, default=sys.stdout, type=lambda x: __parse_file_check_compression(x, 'w'),
                help='Output [gzip] file (default: stdout)'
        )
	parser.add_argument('--debug', action='store_true', required=False, help='Print DEBUG info (default: %(default)s)')
	args = parser.parse_args()
	
	# Set up basic debugger
        logFormat = "[%(levelname)s]: %(message)s"
        logging.basicConfig(format=logFormat, stream=sys.stderr, level=logging.INFO)
        if args.debug:
                logging.getLogger().setLevel(logging.DEBUG)
        logging.debug('%s', args) ## DEBUG
	

	gff3_genes = pass_gff3_file(args.gff3)
	
	gene_pairs(gff3_genes, args.out)
	
	


def gene_pairs(gff3_genes, out_file):
	
	for scaffold in gff3_genes.keys():
		genes = gff3_genes[scaffold] ## Now a dictionary
		logging.debug('%s', genes) ## DEBUG
		
                genes_sorted = []
                # Sort by start position
                for gene_id, gene_info in sorted(genes.iteritems(), key=lambda (x, y): y['start']):
                        logging.debug('%s\t%s', gene_id, gene_info) ## DEBUG
                        genes_sorted.append([gene_id, gene_info])

                # Group each gene into adjacent pairs
                if len(genes_sorted) >= 2:
                        for x in range(len(genes_sorted)-1):
                                gene_pair = genes_sorted[x:x+2]
                                gene_id_1, gene_info_1 = gene_pair[0]
                                gene_id_2, gene_info_2 = gene_pair[1]
                                # 'start':10, 'end':30, 'strand':'+', 'num_exons':5
                                out_file.write('\t'.join([scaffold,
                                    gene_id_1, str(gene_info_1['start']), str(gene_info_1['end']), gene_info_1['strand'], str(gene_info_1['num_exons']), 
                                    gene_id_2, str(gene_info_2['start']), str(gene_info_2['end']), gene_info_2['strand'], str(gene_info_2['num_exons'])
                                    ])+'\n')



"""
gff3_dict = {
        scaffold_1 = {
                gene_1 = {'start':10, 'end':30, 'strand':'+', 'num_exons':5},
                gene_2 = {'start':50, 'end':60, 'strand':'+', 'num_exons':1}
        },
        scaffold_2 = {
                ...
                ...
        },
        ...
        ...
}
"""
def pass_gff3_file(gff3_file):

        gff3_dict = {}

        for line in gff3_file:
                line = line.strip()

                if not line:
                        continue
                if line.startswith('#'):
                        continue
                
                logging.debug('%s', line) ## DEBUG

                f = pass_gff3_line(line.rstrip(';'))
                #print f

                seqid = f['seqid']
                if seqid not in gff3_dict.keys():
                        gff3_dict[seqid] = {}

                if f['feat_type'] == 'mRNA':
                        ID = f['attributes']['ID']
                        gff3_dict[seqid][ID] = {'start':f['start'], 'end':f['end'], 'strand':f['strand'], 'num_exons':0}
                elif f['feat_type'] == 'exon':
                        Parent = f['attributes']['Parent']
                        gff3_dict[seqid][Parent]['num_exons'] += 1

        return gff3_dict



"""

"""
def pass_gff3_line(gff3_line):
        seqid, source, feat_type, start, end, score, strand, phase, attributes = gff3_line.strip().split('\t')

        start = int(start)
        end = int(end)

        attributes_split = [x.split('=') for x in attributes.split(';')]
        attributes_passed = {a:b for a, b in attributes_split}

        gff_feat_dict = {'seqid':seqid,
                        'source':source,
                        'feat_type':feat_type,
                        'start':start,
                        'end':end,
                        'score':score,
                        'strand':strand,
                        'phase':phase,
                        'attributes':attributes_passed}

        return gff_feat_dict



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
