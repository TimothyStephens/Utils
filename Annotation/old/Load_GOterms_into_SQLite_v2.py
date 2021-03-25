#!/usr/bin/env python

DESCRIPTION = """
	Load GO terms from goa_uniprot_all.gaf.gz into a sqlite3 database.	
	Index id column for quick retrival (Used for GO annotation using uniprot annotations).
	
	Will load just the DB_Object_ID and GO_ID columns into the database. As each line is a single GO term 
	(potentially for the same DB_Object_ID) the database will contain duplicate rows for DB_Object_ID column. 
	
	
	*Files:
		wget ftp://ftp.ebi.ac.uk/pub/databases/GO/goa/UNIPROT/goa_uniprot_all.gaf.gz
		wget ftp://ftp.ebi.ac.uk/pub/databases/GO/goa/current_release_numbers.txt
		
		wget ftp://ftp.ebi.ac.uk/pub/databases/GO/goa/UNIPROT/README (For more info)
	
	
	*Example commands:
		python Load_GOterms_into_SQLite.py --db GOterms_UniProtKB_Mapping_Release_xxxx_xx.sqlite3 --goa goa_uniprot_all.gaf
	
		*OR* (to save unzipping file)
	
		gunzip -c test_goa_uniprot_all.gaf.gz | python Load_GOterms_into_SQLite.py --db GOterms_UniProtKB_Mapping_Release_xxxx_xx.sqlite3
	
	
	*Stats:
		~398 million lines @ ~70mins to load (both zipped and unzipped file)
		19Gbp SQLite file
	
	
	Last Modified: 28/05/2019
"""
__version__ = 2

import sys
import argparse
import sqlite3


# Main function
def main():
	parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=DESCRIPTION)
	parser.add_argument('-d', '--db', metavar='GOterms_UniProtKB_Mapping_Release_xxxx_xx.sqlite3', type=str, required=True, help='Sqlite3 database name')
	parser.add_argument('-g', '--goa', metavar='goa_uniprot_all.gaf', type=argparse.FileType('r'), required=False, default=sys.stdin, help='Uncompressed goa data file (default: stdin)')
	args = parser.parse_args()
	
	
	Load_GO_terms(args.db, args.goa)
	
	#for row in goa_db.submit_command('SELECT go_id FROM UniProtGOA WHERE id=?', ('A0A001', )):
	#	print row

def Load_GO_terms(db_file, goa_file):
	"""
	Loads GO terms from goa_uniprot_all.gaf file into SQLite database.
	
	Last Modified: 05/10/2017
	Version: 0.1
	
	Arguments:
		db_file (str): Name of database file
		goa_file (filehandle): GOA file handle (or stdin handle)
	
	Notes:
		ftp://ftp.ebi.ac.uk/pub/databases/GO/goa/UNIPROT/README (For more info)

		GAF2.1 files have the suffix .gaf and contain the following columns:
	
		Column  Contents
		1       DB
		2       DB_Object_ID
		3       DB_Object_Symbol
		4       Qualifier
		5       GO_ID
		6       DB:Reference
		7       Evidence Code
		8       With (or) From
		9       Aspect
		10      DB_Object_Name
		11      DB_Object_Synonym
		12      DB_Object_Type
		13      Taxon and Interacting taxon
		14      Date
		15      Assigned_By
		16      Annotation_Extension
		17      Gene_Product_Form_ID

	"""

	# Open connections and create table.
	db_connection = sqlite3.connect(db_file)
	db_cursor = db_connection.cursor()
	db_cursor.execute('CREATE TABLE GOterm_mappings (id, go_id)')
	db_cursor.execute('CREATE INDEX id_index ON GOterm_mappings (id)')
	db_connection.commit()

	row_count = 0
	row_loaded = 0
	for line in goa_file:
		# Print progress
		if (row_count % 1000000) == 0:
			print "Lines passed/loaded: {:,d}/{:,d}".format(row_count, row_loaded)
		row_count += 1


		# Continue if line is a comment.
		if line.startswith('!'):
			continue
		# Continue if line does not start with UniProtKB
		if not line.startswith('UniProtKB'):
			continue


		line_split = line.rstrip("\n").split('\t')

		# Check line split correctly
		if len(line_split) != 17:
			print "Line split incorrectly: %s" % line_split
			continue

		# Load id and go_id into table
		line_split_unicode = [line_split[1].decode('utf-8'), line_split[4].decode('utf-8')] # Decode for SQLite
		try:
			db_cursor.execute('INSERT INTO GOterm_mappings (id, go_id) VALUES (?, ?)', (line_split_unicode))
		except:
			e = sys.exc_info()
			print e
			print "ERROR:", e[0], e[1]
			print line_split
		row_loaded += 1

	# Print final progress
	print "Total rows passed/loaded: {:,d}/{:,d}".format(row_count, row_loaded)

	# Commit and close database
	db_connection.commit()
	db_connection.close()




if __name__ == '__main__':
	main()
