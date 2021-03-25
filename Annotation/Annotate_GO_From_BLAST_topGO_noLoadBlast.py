#!/usr/bin/env python2
DESCRIPTION = """
	
	Performs GO term annotation from BLAST output file (-outfmt 6) using only first hit which has GO terms associated with it.
	
	i.e. will group hits by the first column and will check every hit (in order it is found in the blast file) until one
	has a GO terms associated with it or we run out of hits. 
	
	NOTE:
		- Can accept output from MMSeqs2 using --mmseq2 flag. This output is exactly the same as blast but MMSeqs2 already splits UniProit headers.
	
	Outputs in topGO compatible gene2GO format:

	Seq1	GO0001, GO0002, GO0125
	Seq2	GO0048
	Seq3	GO1111, GO1589, GO5497, ....
	..
	..
"""
import sys
import os
import argparse
import gzip
import sqlite3
import logging

# Main
def main():
	parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=DESCRIPTION)
	parser.add_argument('-b', '--blast', type=lambda x: __parse_file_check_compression(x, 'r'), required=True, help='Blast [gzip] output file (outfmt 6)')
	parser.add_argument('-o', '--out', type=lambda x: __parse_file_check_compression(x, 'w'), required=True, help='Output [gzip] annotation file (topGO format)')
	parser.add_argument('-d', '--db', type=str, required=True, help='SQLite3 GOterm database')
	parser.add_argument('-m', '--mmseq2', action='store_true', required=False, help='Input is from MMSEQ2 (default: %(default)s)')
	parser.add_argument('--debug', action='store_true', required=False, help='Print DEBUG info (default: %(default)s)')
	args = parser.parse_args()
	
	# Set up basic debugger
	logFormat = "[%(levelname)s]: %(message)s"
	logging.basicConfig(format=logFormat, stream=sys.stderr, level=logging.INFO)
	if args.debug:
		logging.getLogger().setLevel(logging.DEBUG)
	
	logging.debug('%s', args) ## DEBUG
	
	goa_db = SQLite3_Database(args.db)
	
	qseqid_with_hits = []
	
	# Read BLAST file 
	for line in args.blast:
		line = line.strip()
		if not line or line.startswith('#'):
			continue
		
		line_split = line.split()
		qseqid = line_split[0]
		sseqid = line_split[1]
		
		# Test if we already have GO term annotations for this qseqid
		if qseqid in qseqid_with_hits:
			continue
		
		logging.debug('%s', '') ## DEBUG
		logging.debug('%s - Searching for GO terms using: %s - %s', qseqid, sseqid) ## DEBUG
		
		if args.mmseq2:
			hit_id = sseqid
		else:
			sseqid_split = sseqid.split('|')
			# Check line split correctly.
			if len(sseqid_split) != 3:
				print "UniProt id split incorrectly: %s" % sseqid
				continue
			hit_id = sseqid_split[1]
		
		# Try and get GO terms
		goa_out = goa_db.submit_command('SELECT go_id FROM GOterm_mappings WHERE id=?', (hit_id, ))
		goa_out_set = set([x[0] for x in goa_out]) # Remove duplicate GO terms (Happens in a very small number of cases [because of the goa file])
		
		# If we actually got some GO terms
		if len(goa_out_set) > 0:
			logging.debug('GO terms found: %s', ', '.join(goa_out_set)) ## DEBUG
			
			# If output to be in WEGO format (single line)
			args.out.write(qseqid + '\t' + ', '.join(goa_out_set) + '\n')
			
			# GO term annotations found for qseqid. Add to list of annotated IDs.
			qseqid_with_hits.append(qseqid)
	
	args.blast.close()
	args.out.close()
	



class SQLite3_Database():
        # Open database when creating class. 
        def __init__(self, db_file):
                self.db_connection = sqlite3.connect(db_file)
                self.db_cursor = self.db_connection.cursor()

        # Submit query to database
        # arg (str):            Command to be run.
        # values (tuple):       Values to be safely subbed into arg command. Can be absent if no sub required.
        def submit_command(self, arg, values=()):
                self.db_cursor.execute(arg, values)
                self.db_connection.commit()
                return self.db_cursor

        def __del__(self):
                self.db_connection.close()



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
