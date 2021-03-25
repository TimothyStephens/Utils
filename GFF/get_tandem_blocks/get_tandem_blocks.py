#!/usr/bin/env python2
DESCRIPTION = '''
Clusters target genes (given in a list) based on genome location (clusters are broken by genes not in list).
Can be used to find tandemly repeated blocks.
Only outpust groups with > X members (where X is a user defined parameter)

NOTE:
	The number of times a gene ID appears in --target_genes will be printed (as it is assumed this is significant).
'''
import sys
import argparse
import logging

## Pass arguments.
def main():
	# Pass command line arguments. 
	parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=DESCRIPTION)
	parser.add_argument('-g', '--gff3', metavar='input.txt', type=argparse.FileType('r'), required=True, help='Input gff3 file')
	parser.add_argument('-o', '--out', metavar='output.txt', type=argparse.FileType('w'), required=True, help='Output text file')
	parser.add_argument('-t', '--target_genes', metavar='genes_of_interest.txt', type=argparse.FileType('r'), required=True, help='Input genes of interest')
	parser.add_argument('-c', '--column', default=1, type=int, required=False, help='Column to take gene IDs from (default: %(default)s)')
	parser.add_argument('-s', '--min_group_size', default=1, type=int, required=False, help='Groups below this size will not be returned (default: %(default)s)')
	parser.add_argument('--debug', action='store_true', required=False, help='Print DEBUG info (default: %(default)s)')
	args = parser.parse_args()
	
	# Set up basic debugger
	if args.debug:
		logging.basicConfig(format='#DEBUG: %(message)s', stream=sys.stdout, level=logging.DEBUG)
	else:
		logging.basicConfig(format='#ERROR: %(message)s', stream=sys.stdout, level=logging.ERROR)
	
	logging.debug('%s', args) ## DEBUG
	
	target_genes = load_target_genes(args.target_genes, args.column)
	logging.debug('%s', target_genes) ## DEBUG
	
	gff3_genes = pass_gff3_file(args.gff3)
	
	cluster_by_genomic_location(gff3_genes, target_genes, args.out, args.min_group_size)
	
	

## Load target genes IDs from file. 
## Also counts the number of times an ID is observed in file.
def load_target_genes(target_genes_file, column):
	target_genes = {}
	for line in target_genes_file:
		line = line.strip()
		
		if not line or line.startswith("#"):
			continue
		
		gene_id = line.split()[column-1]
		logging.debug('Gene ID found: %s', gene_id) ## DEBUG
		
		if gene_id not in target_genes.keys():
			target_genes[gene_id] = 1
		else:
			target_genes[gene_id] += 1

	return target_genes



def cluster_by_genomic_location(gff3_genes, target_genes, out_file, min_group_size):
	
	target_genes_set = set(target_genes.keys())
	
	for scaffold in gff3_genes.keys():
		genes = gff3_genes[scaffold] ## Now a dictionary
		logging.debug('%s', genes) ## DEBUG
		
		gene_clusters = []
		last_gene_was_target = False
		
		# Sort by start position
		for gene_id, gene_info in sorted(genes.iteritems(), key=lambda (x, y): y['start']):
			logging.debug('%s\t%s', gene_id, gene_info) ## DEBUG
			
			if gene_id in target_genes_set:
				if last_gene_was_target:
					gene_clusters[-1].append([gene_id, gene_info])
				else:
					gene_clusters.append([[gene_id, gene_info]])
					last_gene_was_target = True
			else:
				last_gene_was_target = False
			
			logging.debug('%s', gene_clusters) ## DEBUG
		
		for group in gene_clusters:
			logging.debug('Group: %s', group) ## DEBUG
			if len(group) >= min_group_size:
				
				# Get info for group header
				Group_Size = len(group)
				Group_Distance = (group[-1][1]['end'] - group[0][1]['start']) + 1
				Number_Changes = get_number_changes(group)
				Number_Single_Exon = 0
				Number_Multi_Exon = 0
				
				for gene_id, gene_info in group:
					if gene_info['num_exons'] == 1:
						Number_Single_Exon += 1
					else:
						Number_Multi_Exon += 1
				
				out_file.write("## Group_Size: {} Group_Distance: {} Number_Changes: {} Number_Single_Exon: {} Number_Multi_Exon: {}\n".format(Group_Size, Group_Distance, Number_Changes, Number_Single_Exon, Number_Multi_Exon))
				for gene_id, gene_info in group:
					
					start_pos = str(gene_info['start'])
					end_pos = str(gene_info['end'])
					strand = gene_info['strand']
					number_exons = str(gene_info['num_exons'])
					
					# scaffold </t> start_pos </t> end_pos </t> strand </t> gene_id </t> number_exons </n>
					out_file.write("\t".join([scaffold, start_pos, end_pos, strand, gene_id, number_exons]) + '\n')




def get_number_changes(genes_subset):
        logging.debug('%s', genes_subset) ## DEBUG
        change_count = 0
        last_strand = genes_subset[0][1]['strand']
        for gene_id, gene_info in genes_subset:
                if gene_info['strand'] != last_strand:
                        change_count += 1
                        last_strand = gene_info['strand']
        return change_count




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




if __name__ == '__main__':
	main()
