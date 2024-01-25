#!/usr/bin/env python3
import sys
import os
import logging
import argparse


class File(object):
	'''
	Context Manager class for opening stdin/stdout/normal/gzip files.

	 - Will check that file exists if mode='r'.
	 - Will check that file exists if mode='s' and return just the string.
	 - Will overwrite file by default in mode='w'.
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
	def __init__(self, file_name, mode, overwrite=True):
		## Upon initializing class open file (using gzip, bz2, or lzma if needed)
		self.file_name = file_name
		self.mode = mode
		self.overwrite = overwrite
		
		## Check that mode in one of the allowed options
		if not self.mode in ['r', 'w', 's']:
			raise argparse.ArgumentTypeError("Mode %s is not one of the allowed options: ['r', 'w', 's']!" % self.mode)
		
		## Check file exists if mode='r'
		if self.mode == 'r' and not os.path.exists(self.file_name):
			raise argparse.ArgumentTypeError("The file %s does not exist!" % self.file_name)
		
		## Check file exists if mode='w' - Stop of overwrite=False
		if self.mode == 'w' and os.path.exists(self.file_name) and not self.overwrite:
			raise argparse.ArgumentTypeError("The file %s already exist and we dont want to overwrite it!" % self.file_name)
		
		## If mode=='s' return just the file name
		if self.mode == 's':
			self.file_obj = self.file_name
		else:
			## Open with gzip if it has the *.gz extension, else open normally (including stdin)
			try:
				if self.file_name.endswith(".gz"):
					logging.debug('Opening gzip compressed file (mode: %s): %s', self.mode, self.file_name) ## DEBUG
					import gzip
					self.file_obj = gzip.open(self.file_name, self.mode+'t')
				elif self.file_name.endswith(".bz2"):
					logging.debug('Opening bz2 compressed file (mode: %s): %s', self.mode, self.file_name) ## DEBUG
					import bz2
					self.file_obj = bz2.open(self.file_name, self.mode+'b')
				elif self.file_name.endswith(".lzma"):
					logging.debug('Opening lzma compressed file (mode: %s): %s', self.mode, self.file_name) ## DEBUG
					import lzma
					self.file_obj = lzma.open(self.file_name, self.mode+'b')
				elif self.file_name.endswith(".xz"):
					logging.debug('Opening xz compressed file (mode: %s): %s', self.mode, self.file_name) ## DEBUG
					import xz
					self.file_obj = xz.open(self.file_name, self.mode+'b')
				else:
					logging.debug('Opening normal file (mode: %s): %s', self.mode, self.file_name) ## DEBUG
					self.file_obj = open(self.file_name, self.mode)
			except IOError as e:
				raise argparse.ArgumentTypeError('%s' % e)
	
	def __enter__(self):
		## Run When 'with' statement uses this class.
		logging.debug('__enter__: %s', self.file_name) ## DEBUG
		return self.file_obj
	def __exit__(self, type, value, traceback):
		## Run when 'with' statement is done with object. Either because file has been exhausted, we are done writing, or an error has been encountered.
		logging.debug('__exit__: %s', self.file_name) ## DEBUG
		if self.mode != 's':
			self.file_obj.close()
#	def __iter__(self):
#		## iter method need for class to work with 'for' loops
#		logging.debug('__iter__: %s', self.file_name) ## DEBUG
#		return self.file_obj
#	def close(self):
#		## method to call .close() directly on object.
#		logging.debug('close: %s', self.file_name) ## DEBUG
#		self.file_obj.close()


