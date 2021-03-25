"""
	
	Commands for importing BLAST results into a list or dict.
	
	These functions are designed to be cut and pasted into other scripts and used for whatever purpose. 
	
"""
import sys



def BLAST_iter(blast_fh, key_col=1, ret_cols=range(1, 13), no_cols=12):
        """
        Takes BLAST filehandle and yields lists of hits which all have the same key_col.
	Allows for quick traversal of very large BLAST output files.
	 
        Version: 0.1
        Last Modified: 28/09/2017
        
        Arguments:
                blast_fh:       File handle with BLAST output "-outfmt 6".
                key_col:        Column to define sets. 1-based. Must be (>=1 and <= no_cols).
                ret_cols:       Columns to retain in output. As LIST, 1-based. Must be (>0 and <= no_cols).
                no_cols:        Expected number of columns in BLAST output.
        
        Yields:
                blast_list:     List of BLAST hits imported in appropriate format. 
        
        Note:   - Must be sorted by key_col (all entries with same key_col must be next to each other)
		- Ignores blank lines.
                - Does not transform columns (will not convert str to int e.g. for start/stop/etc.)

        """

        # Check that ret_cols is within bounds.
        if not (min(ret_cols) > 0) or not (max(ret_cols) <= no_cols):
                print "ret_cols out of bounds!"
                sys.exit()

        # Check that key_col is within bounds.
        if not (key_col > 0) or not (key_col <= no_cols):
                print "key_col out of bounds!"
                sys.exit()
	
	# Import BLAST file.
	blast_list = []
	current_key_value = ''
	
	# Get first entry (Assumes first line is not blank).
	line = blast_fh.readline()
	blast_hit_split = line.strip("\n").split("\t")
	blast_list.append([blast_hit_split[i-1] for i in ret_cols])
	current_key_value = blast_hit_split[key_col-1] # Get key value (convert to 0-based)
	
        for line in blast_fh:
                # Ignore blank lines.
                if line.strip("\n") == '':
                        continue

                blast_hit_split = line.strip("\n").split("\t")

                # Check if blast hit matches expected size.
                if len(blast_hit_split) != no_cols:
                        print "Line !=", no_cols
                        print line
                        sys.exit()

		# Get current key value.
                key_col_value = blast_hit_split[key_col-1] # Get key value (convert to 0-based)
		
		# Is this hit from a new key_col_value
		if key_col_value != current_key_value:
			yield blast_list
			blast_list = []	# Reset and update
			current_key_value = key_col_value
		blast_list.append([blast_hit_split[i-1] for i in ret_cols])
	# Last set of hits
	yield blast_list





def BLAST_to_list(blast_fh, ret_cols=range(1, 13), no_cols=12):
	"""
	Takes BLAST filehandle and imports it into a list containing the desired columns.
	
	Version: 0.1
	Last Modified: 28/09/2017
	
	Arguments:
		blast_fh:	File handle with BLAST output "-outfmt 6".
		ret_cols:	Columns to retain in output. As LIST, 1-based. Must be (>0 and <= no_cols).
		no_cols:	Expected number of columns in BLAST output.
	
	Returns:
		blast_list:	List of BLAST hits imported in appropriate format. 
	
	Note:	- Ignores blank lines.
	 	- Does not transform columns (will not convert str to int e.g. for start/stop/etc.)
	"""
		
	# Check that ret_cols in within bounds.
        if not (min(ret_cols) > 0) or not (max(ret_cols) <= no_cols):
		print "ret_cols out of bounds!"
		sys.exit()
	
	# Import BLAST file.
	blast_list = []
	for line in blast_fh:
		# Ignore blank lines.
		if line.strip("\n") == '':
			continue
		
		blast_hit_split = line.strip("\n").split("\t")
		
		# Check if blast hit matches expected size.
		if len(blast_hit_split) != no_cols:
			print "Line !=", no_cols
			print line
			sys.exit()
		
		# Converts ret_cols into 0-base
		blast_list.append([blast_hit_split[i-1] for i in ret_cols])
		
	return blast_list






def BLAST_to_dict(blast_fh, key_col=1, ret_cols=range(1, 13), no_cols=12):
	"""
	Takes BLAST filehandle and imports it into a dict with the key as whatever the user wishes.
	
	Version: 0.1
	Last Modified: 28/09/2017
	
	Arguments:
	 	blast_fh:	File handle with BLAST output "-outfmt 6".
		key_col:	Column to make DICT key. 1-based. Must be (>0 and <= no_cols).
		ret_cols:	Columns to retain in output. As LIST, 1-based. Must be (>0 and <= no_cols).
		no_cols:	Expected number of columns in BLAST output.
	
	Returns:
		blast_dict:	Dict of BLAST hits imported in appropriate format. 
	
	Note:	- Ignores blank lines.
		- Does not transform columns (will not convert str to int e.g. for start/stop/etc.)

	"""
	
	# Check that ret_cols is within bounds.
        if not (min(ret_cols) > 0) or not (max(ret_cols) <= no_cols):
                print "ret_cols out of bounds!"
                sys.exit()

	# Check that key_col is within bounds.
        if not (key_col > 0) or not (key_col <= no_cols):
                print "key_col out of bounds!"
                sys.exit()
	
	# Import BLAST file.
	blast_dict = {}
	for line in blast_fh:
		# Ignore blank lines.
		if line.strip("\n") == '':
			continue
		
		blast_hit_split = line.strip("\n").split("\t")
		
		# Check if blast hit matches expected size.
		if len(blast_hit_split) != no_cols:
                        print "Line !=", no_cols
                        print line
                        sys.exit()
		
		# Get key value and add key to dict if not present. 
		key_col_value = blast_hit_split[key_col-1] # Get key value (convert to 0-based)
		if key_col_value not in blast_dict.keys():
			blast_dict[key_col_value] = []
		
		# Converts ret_cols into 0-base
		blast_dict[key_col_value].append([blast_hit_split[i-1] for i in ret_cols])
		
	return blast_dict





