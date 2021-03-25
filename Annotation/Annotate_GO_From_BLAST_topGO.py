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
	
	# Import just the 2n column from the blast file (subject). 
	# All that is needed since the dict key gives us the query name.
	blast_dict = BLAST_to_dict(args.blast, key_col=1, ret_cols=[2])
	args.blast.close()
	#print blast_dict
	
	for key, hits in blast_dict.items():
		logging.debug('%s', '') ## DEBUG
		logging.debug('%s - Finding GO terms from:', key) ## DEBUG
		logging.debug('%s', hits) ## DEBUG
		
		# For each hit in list of hits
		for hit in hits:
			logging.debug('%s - Searching for GO terms with %s', key, hit) ## DEBUG
			hit = hit[0] # Get subject id from hit list
			
			if args.mmseq2:
				hit_id = hit
			else:
				id_split = hit.split('|')
				# Check line split correctly.
				if len(id_split) != 3:
					print "UniProt id split incorrectly: %s" % hit
					continue
				hit_id = id_split[1]
			
			# Try and get GO terms
			goa_out = goa_db.submit_command('SELECT go_id FROM GOterm_mappings WHERE id=?', (hit_id, ))
			goa_out_set = set([x[0] for x in goa_out]) # Remove duplicate GO terms (Happens in a very small number of cases [because of the goa file])
			
			# If we actually got some GO terms
			if len(goa_out_set) > 0:
				logging.debug('GO terms found: %s', ', '.join(goa_out_set)) ## DEBUG
				 
				# If output to be in WEGO format (single line)
				args.out.write(key + '\t' + ', '.join(goa_out_set) + '\n')
				
				# Break loop if hits
				break
	
	args.out.close()



def BLAST_to_dict(blast_fh, key_col=1, ret_cols=range(1, 12)):
        """
        Takes BLAST filehandle and imports it into a dict with the key as whatever the user wishes.
        
        Version: 0.2
        Last Modified: 28/05/2019
        
        Arguments:
                blast_fh:       File handle with BLAST output "-outfmt 6".
                key_col:        Column to make DICT key. 1-based. Must be >0.
                ret_cols:       Columns to retain in output. As LIST, 1-based. Must be >0.
        
        Returns:
                blast_dict:     Dict of BLAST hits imported in appropriate format. 
        
        Note:   - Ignores blank lines.
                - Does not transform columns (will not convert str to int e.g. for start/stop/etc.)

        """

        # Check that ret_cols is within bounds.
        if not (min(ret_cols) > 0):
                print "ret_cols out of bounds!"
                sys.exit()

        # Check that key_col is within bounds.
        if not (key_col > 0):
                print "key_col out of bounds!"
                sys.exit()

        # Import BLAST file.
        blast_dict = {}
        for line in blast_fh:
		line = line.strip()
                # Ignore blank lines.
                if not line:
                        continue
		
                blast_hit_split = line.split("\t")
		
                # Get key value and add key to dict if not present. 
                key_col_value = blast_hit_split[key_col-1] # Get key value (convert to 0-based)
                if key_col_value not in blast_dict.keys():
                        blast_dict[key_col_value] = []

                # Converts ret_cols into 0-base
                blast_dict[key_col_value].append([blast_hit_split[i-1] for i in ret_cols])

        return blast_dict



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
