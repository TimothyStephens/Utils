#!/usr/bin/env python2
DESCRIPTION = '''

Construct contingency table from a list of genes annotations and a list of target genes.

# --annots file should list genes and their associated annotations.
#	- Format gene_id *tab* annot_id
#	- Allows for a gene to be annotated on multiple lines (will append annot_id's into a single list)
#	- annot_id on a single line can be seperated by commas or comma+space
gene1 *tab* annot1
gene1 *tab* annot2, annot3
gene2 *tab* annot4

# NOTE:
#	- Will not collapse duplicate annot_id's for the same gene (i.e. two of the same annot_id will be interpreted as that feature being present twice in the gene)

# --targets
#	- List of gene_id's that are in our test/target set (used for building contingency table)
# 	- Takes only the fist column (ignores other if present; default delimiter: \\t)

'''
import sys
import argparse
import logging

## Pass arguments.
def main():
	# Pass command line arguments. 
	parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=DESCRIPTION)
	parser.add_argument('-a', '--annots', metavar='gene_annots.txt', 
		required=True, type=lambda x: File(x, 'r'),
		help='List of genes and annotated features that we want to test for enrichment'
	)
	parser.add_argument('-t', '--targets', metavar='target_genes.txt', 
		required=True, type=lambda x: File(x, 'r'),
		help='List of genes in our target set'
	)
	parser.add_argument('-o', '--out', metavar='output.txt', 
		required=True, type=lambda x: File(x, 'w'),
		help='Output contingency file'
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
	
	with args.annot as annotFile:
		annots = load_annots(annotFile)
	with args.targets as targetsFile:
		target_IDs = load_ids(targetsFile)
	
	with args.out as outFile:
		make_contingency_table(annots, target_IDs, outFile)


def make_contingency_table(annots, target_IDs, out_fh):
	# Count up the number of annots after we remove or take just the elements in target_IDs
	test_counts, test_total = load_counts({x:y for x, y in annots.items() if x in target_IDs})
	not_test_counts, not_test_total = load_counts({x:y for x, y in annots.items() if x not in target_IDs})
	
	ids = set(test_counts.keys()).union(set(not_test_counts.keys()))
	
	# [ID, DomainTestCount, DomainNotTestCount, NotDomainTestCount, NotDomainNotTestCount]
	out_fh.write('ID\tDomainTestCount\tDomainNotTestCount\tNotDomainTestCount\tNotDomainNotTestCount\n')
	for id in ids:
		DomainTestCount = 0
		DomainNotTestCount = 0
		NotDomainTestCount = test_total
		NotDomainNotTestCount = not_test_total
		
		if id in test_counts.keys():
			DomainTestCount = test_counts[id]
			NotDomainTestCount = test_total - test_counts[id]
		if id in not_test_counts.keys():
			DomainNotTestCount = not_test_counts[id]
			NotDomainNotTestCount = not_test_total - not_test_counts[id]
		
		out_fh.write('\t'.join([id, str(DomainTestCount), str(DomainNotTestCount), str(NotDomainTestCount), str(NotDomainNotTestCount)]) + '\n')
	
	


def load_counts(annots, sep='\t'):
	'''
	Takes a dict of {gene_id:[annot_ids]} pairs and converst it to {annot_id:count} and also counts total annot_id's seen. 
	'''
	combined_annots = []
	for a in annots:
		combined_annots.extend(a)
	counts = {i:combined_annots.count(i) for i in set(combined_annots)}
	total = sum([x for x in counts.values()])
	
	return counts, total



def load_ids(fh, delim='\t', col=0):
	'''
	Load IDs from a given column from a file.
	
	Returns a set() of unique IDs.
	'''
	IDs = []
	for line in fh:
		line = line.strip()
		if not line or line.startswith('#'):
			continue
		
		try:
			line_split = line.split(delim)
			IDs.append(line_split[col])
		except IndexError:
			logging.error("Filed to extract col_num:%s from line: %s", col, line)
			sys.exit(1)
	return set(IDs)



def load_annots(fh, delim='\t'):
	'''
	Load annotations from file.
	
	fh Expected format: 
		gene_id *tab* annot_id
	OR:
		gene_id *tab* annot_id,annot_id, annot_id
	
	Returns:
		dict{gene1:[annot1, annot2, annot2], gene2:[annot1,annot10], ...}
	
	NOTE:
		- Gene IDs across multiple lines have their annotations combined into a single list
		- If a gene_id has multiple of the same annot_id (duplicate annot_id's) then the duplicates are reported.
		  Assumes you want duplicate IDs reported the number of times they are observed. 
	'''
	annots = {}
	for line in fh:
		line = line.strip()
		if not line or line.startswith('#'):
			continue
		
		try:
			gene_id, annots = line.split(delim)
		except ValueError:
			logging.error("Filed to split line into 2 columns: %s", line)
			sys.exit(1)
		
		# Add annots to dict - create key:[value] if we havent seen gene_id before. 
		if gene_id not in annots.keys():
			annots[gene_id] = []
		for annot in annots.split(','):
			annot = annot.strip() # Clean up leading/trailing white space.
			if annot: # If string not empty [True]
				annots[gene_id].append(annot)
	return annots





class File(object):
        '''
        Context Manager class for opening stdin/stdout/normal/gzip files.

         - Will check that file exists if mode='r'
         - Will open using either normal open() or gzip.open() if *.gz extension detected.
         - Designed to be handled by a 'with' statement (other wise __enter__() method wont
            be run and the file handle wont be returned)

        NOTE:
                - Can't use .close() directly on this class unless you uncomment the close() method
                - Can't use this class with a 'for' loop unless you uncomment the __iter__() method
                        - In this case you should also uncomment the close() method as a 'for'
                           loop does not automatically cloase files, so you will have to do this
                           manually.
                - __iter__() and close() are commented out by default as it is better to use a 'with'
                   statement instead as it will automatically close files when finished/an exception
                   occures.
                - Without __iter__() and close() this object will return an error when directly closed
                   or you attempt to use it with a 'for' loop. This is to force the use of a 'with'
                   statement instead.

        Code based off of context manager tutorial from: https://book.pythontips.com/en/latest/context_managers.html
        '''
        def __init__(self, file_name, mode):
                ## Upon initializing class open file (using gzip if needed)
                self.file_name = file_name
                self.mode = mode

                ## Check file exists if mode='r'
                if not os.path.exists(self.file_name) and mode == 'r':
                        raise argparse.ArgumentTypeError("The file %s does not exist!" % self.file_name)

                ## Open with gzip if it has the *.gz extension, else open normally (including stdin)
                try:
                        if self.file_name.endswith(".gz"):
                                #print "Opening gzip compressed file (mode: %s): %s" % (self.mode, self.file_name) ## DEBUG
                                self.file_obj = gzip.open(self.file_name, self.mode+'b')
                        else:
                                #print "Opening normal file (mode: %s): %s" % (self.mode, self.file_name) ## DEBUG
                                self.file_obj = open(self.file_name, self.mode)
                except IOError as e:
                        raise argparse.ArgumentTypeError('%s' % e)
        def __enter__(self):
                ## Run When 'with' statement uses this class.
                #print "__enter__: %s" % (self.file_name) ## DEBUG
                return self.file_obj
        def __exit__(self, type, value, traceback):
                ## Run when 'with' statement is done with object. Either because file has been exhausted, we are done writing, or an error has been encountered.
                #print "__exit__: %s" % (self.file_name) ## DEBUG
                self.file_obj.close()
#       def __iter__(self):
#               ## iter method need for class to work with 'for' loops
#               #print "__iter__: %s" % (self.file_name) ## DEBUG
#               return self.file_obj
#       def close(self):
#               ## method to call .close() directly on object.
#               #print "close: %s" % (self.file_name) ## DEBUG
#               self.file_obj.close()



if __name__ == '__main__':
	main()
