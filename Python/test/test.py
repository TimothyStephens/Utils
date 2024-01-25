#!/usr/bin/env python3

import sys
import logging
logging.getLogger().setLevel(logging.DEBUG)
 
# setting path
sys.path.append('../')
 
# importing
from src.files import *

## Read files
p = "file.txt"
for file_name in [p, p+".gz"]:
	with File(file_name, 'r') as fh:
		for f in fh:
			print(f)

## Write files
p = "file_out.txt"
for file_name in [p, p+".gz"]:
	with File(file_name, 'w') as fh:
		fh.write('Test text.\n')

## String
p = "file_out.txt"
for file_name in [p, p+".gz"]:
	with File(file_name, 's') as fh:
		print(fh)

## Fails
#with File("File.txt", 'r') as fh:
#	pass
#with File("file.txt", 'R') as fh:
#	pass
#with File("file.txt", 'w', overwrite=False) as fh:
#	pass


