"""
	
	Test the functions.
	
"""


from BLAST_Import_Functions import *

"""
blast_fh = open("test__blastp.outfmt6", "r")
blast_list = BLAST_to_list(blast_fh, ret_cols=[1, 2])


print len(blast_list)
for line in blast_list:
	print line


blast_fh = open("test__blastp.outfmt6", "r")
blast_dict = BLAST_to_dict(blast_fh, ret_cols=[1, 2], key_col=2)
print len(blast_dict.keys())
for key in blast_dict.keys():
	print key
        print blast_dict[key]
"""

blast_fh = open("test__blastp.outfmt6", "r")
for hits in BLAST_iter(blast_fh):
	print hits
	for hit in hits:
		print hit


