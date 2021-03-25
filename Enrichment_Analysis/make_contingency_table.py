#!/usr/bin/env python2
DESCRIPTION = '''

Construct contingency table.

'''
import sys
import argparse
import logging

## Pass arguments.
def main():
	# Pass command line arguments. 
	parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=DESCRIPTION)
	parser.add_argument('-t', '--test', metavar='test.txt', type=argparse.FileType('r'), required=True, help='Input test file')
	parser.add_argument('-n', '--not_test', metavar='not_test.txt', type=argparse.FileType('r'), required=True, help='Input not test file')
	parser.add_argument('-o', '--out', metavar='output.txt', type=argparse.FileType('w'), required=True, help='Output contingency file')
	parser.add_argument('--debug', action='store_true', required=False, help='Print DEBUG info (default: %(default)s)')
	args = parser.parse_args()
	
	# Set up basic debugger
	logFormat = "[%(levelname)s]: %(message)s"
	logging.basicConfig(format=logFormat, stream=sys.stderr, level=logging.INFO)
	if args.debug:
		logging.getLogger().setLevel(logging.DEBUG)
	
	logging.debug('%s', args) ## DEBUG
	
	make_contingency_table(args.test, args.not_test, args.out)


def make_contingency_table(test_fh, not_test_fh, out_fh):
	test_counts, test_total = load_counts(test_fh)
	not_test_counts, not_test_total = load_counts(not_test_fh)
	
	ids = set(test_counts.keys() + not_test_counts.keys())
	
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
	
	



def load_counts(fh, sep='\t'):
	counts = {}
	total = 0
	for line in fh:
		line = line.strip()
		if not line or line.startswith('#'):
			continue
		line_split = line.split(sep)
		counts[line_split[0]] = int(line_split[1])
		total += int(line_split[1])
	return counts, total



if __name__ == '__main__':
	main()
