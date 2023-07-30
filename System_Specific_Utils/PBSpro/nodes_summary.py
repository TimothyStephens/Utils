"""
	
	Gets stats fro each node on the server.
	Will either print in a compact way by default.
	Can also print stats for each node.
	
	UPDATE:
		- Now shows free resources per node in stead of used resources per node. 
			Makes the fill_list more useful when deciding on how many resources to request. 
	
"""
import argparse
import sys
import subprocess
from itertools import groupby

# Parse args
def main():
	parser = argparse.ArgumentParser(description='Get summary of nodes avalible')
	parser.add_argument('-l', '--full_list', action='store_true', required=False, help='Print stats for each node')
	parser.add_argument('-f', '--free', action='store_true', required=False, help='Print stats for free nodes (only if -l used)')
	parser.add_argument('-n', '--pbsnodes', type=str, default='pbsnodes', required=False, help='Location of pbsnodes script')
	args = parser.parse_args()
	#print args

	nodes = pass_pbsnodes(args.pbsnodes)
	#print nodes
	
	#print bytes_2_human_readable('396948936', 'kb', precision = 1)
	
	# Print either full or basic stats
	if args.full_list:
		print_full_stats_for_each_node(nodes, args.free)
	else:
		print_basic_stats_for_each_node(nodes)



# Get basic stats about each node (ncpus + mem + [queue])
def print_basic_stats_for_each_node(nodes):
	basic_stats = []
	for node in nodes:
		ncpus = get_value_if_key_valid(node, 'resources_available.ncpus')
		mem = get_value_if_key_valid(node, 'resources_available.mem')
		queue = get_value_if_key_valid(node, 'queue')
		
		if mem != '?': #If mem value found
			mem = bytes_2_human_readable(mem[:-2], mem[-2:], precision = 0)
		
		if queue == '?':
			basic_stats.append('{:>3} cores and {:>6} memory'.format(ncpus, mem))
		else:
			basic_stats.append('{:>3} cores and {:>6} memory in queue {}'.format(ncpus, mem, queue))

	# Group nodes and print final counts + stats
	for stats in set(basic_stats):
		count = basic_stats.count(stats)
		print 'Found {:>3} nodes with {}'.format(count, stats)



# Get full stats about each node
def print_full_stats_for_each_node(nodes, free):
	full_stats = []
	for node in nodes:
		# Get values
		ncpus = get_value_if_key_valid(node, 'resources_available.ncpus')
		mem = get_value_if_key_valid(node, 'resources_available.mem')
		scratch = get_value_if_key_valid(node, 'resources_available.scratch')
		# 
		ncpus_ass = get_value_if_key_valid(node, 'resources_assigned.ncpus')
		mem_ass = get_value_if_key_valid(node, 'resources_assigned.mem')
		# 
		host = get_value_if_key_valid(node, 'resources_available.host')
		queue = get_value_if_key_valid(node, 'queue')
		state = get_value_if_key_valid(node, 'state')
		
		# Convert values if found
		if mem != '?':
			mem = bytes_2_human_readable(mem[:-2], mem[-2:], precision = 0)
		if mem_ass != '?':
			mem_ass = bytes_2_human_readable(mem_ass[:-2], mem_ass[-2:], precision = 0)
		if scratch != '?':
			scratch = bytes_2_human_readable(scratch[:-2], scratch[-2:], precision = 0)
		
		# Get free resources per node
		ncpus_free = '?'
		mem_free = '?'
		if ncpus_ass != '?' and ncpus != '?':
			ncpus_free = str( int(ncpus) - int(ncpus_ass) )
		if mem_ass != '?' and mem != '?':
			mem_free = str( int(mem[:-3]) - int(data_storage_converter(mem_ass[:-3], mem_ass[-2:], mem[-2:], precision = 0)) ) + ' ' + mem[-2:]
		
		ncpus_str = '{:>3} / {:>3}'.format(ncpus_free, ncpus)
		mem_str = '{:>3} / {:>3}'.format(mem_free, mem)
		
		# If -f flag set return only 'free' nodes, else return all nodes.
		if free and 'free' in state:
			full_stats.append('|  {:>11}  |  {:>26}  |  {:>17}  |  {:>18}  |  {:>9}  |  {:>13}  |'.format(host, state, ncpus_str, mem_str, scratch, queue))
		if not free:
			full_stats.append('|  {:>11}  |  {:>26}  |  {:>17}  |  {:>18}  |  {:>9}  |  {:>13}  |'.format(host, state, ncpus_str, mem_str, scratch, queue))
	
	# Print stats
	print '+---------------------------------------------------------------------------------------------------------------------------+'
	print '|   Node Name   |          Node State          |   NCPUS free/aval   |   Memory free/aval   |   Scratch   |      Queue      |'
	print '+---------------------------------------------------------------------------------------------------------------------------+'
	for stats in full_stats:
		print stats
	print '+---------------------------------------------------------------------------------------------------------------------------+'



# Get value from dict if avalible
def get_value_if_key_valid(dict_to_search, key_to_seach, if_absent = '?'):
	try:
		return dict_to_search[key_to_seach]
	except KeyError:
		return if_absent



# Convert values into highest possible
# Modified from: https://stackoverflow.com/questions/12523586/python-format-size-application-converting-b-to-kb-mb-gb-tb/37423778
def bytes_2_human_readable(number_to_convert, unit, precision = 1):
	# Convert to float else return value
	try:
		number_to_convert = float(number_to_convert)
	except ValueError:
		return number_to_convert
	
	# Check value
	if number_to_convert < 0:
		raise ValueError("!!! number_to_convert can't be smaller than 0 !!!")
	
	
    	step_to_greater_unit = 1024.
	unit = unit.upper() #To prevent problems with capitalization
	
	if unit == 'BYTES':
		if (number_to_convert / step_to_greater_unit) >= 1:
        		number_to_convert /= step_to_greater_unit
        		unit = 'KB'
	
	if unit == 'KB':
    		if (number_to_convert / step_to_greater_unit) >= 1:
        		number_to_convert /= step_to_greater_unit
        		unit = 'MB'
	if unit == 'MB':
		if (number_to_convert / step_to_greater_unit) >= 1:
        		number_to_convert /= step_to_greater_unit
        		unit = 'GB'
	if unit == 'GB':
		if (number_to_convert / step_to_greater_unit) >= 1:
        		number_to_convert /= step_to_greater_unit
        		unit = 'TB'
	
    	number_to_convert = round(number_to_convert, precision)
	
	# Removes *.0 from output when no decimals required
	if precision == 0:
		number_to_convert = int(number_to_convert)
	
	return str(number_to_convert) + ' ' + unit



# Data storage conversion tool
# Modified from: https://stackoverflow.com/questions/12523586/python-format-size-application-converting-b-to-kb-mb-gb-tb/37423778
# 
#       number_to_convert:      number in str/int/float
#       start_unit:             unit of number_to_convert ['BYTES', 'KB', 'MB', 'GB', 'TB']
#       end_unit:               output unit ['BYTES', 'KB', 'MB', 'GB', 'TB']
def data_storage_converter(number_to_convert, start_unit, end_unit, precision = 1):
        # Convert to float else return value
        try:
                number_to_convert = float(number_to_convert)
        except ValueError:
                return number_to_convert

        # Check value
        if number_to_convert < 0:
                raise ValueError("!!! number_to_convert can't be smaller than 0 !!!")


        units = ['BYTES', 'KB', 'MB', 'GB', 'TB'] # Units to convert to
        step_to_greater_unit = 1024.
        start_unit = start_unit.upper() #To prevent problems with capitalization
        end_unit = end_unit.upper()

        if units.index(start_unit) < units.index(end_unit): # If end_unit larger then start_unit
                number_to_convert /= (step_to_greater_unit ** (units.index(end_unit) - units.index(start_unit)))
        elif units.index(start_unit) > units.index(end_unit): # If start_unit larger then end_unit
                number_to_convert *= (step_to_greater_unit ** (units.index(start_unit) - units.index(end_unit)))
        # Else if start_unit and end_unit are the same return number_to_convert 
	
	number_to_convert = round(number_to_convert, precision)

        # Removes *.0 from output when no decimals required
        if precision == 0:
                number_to_convert = int(number_to_convert)
	
        return str(number_to_convert)



# Pass stdout from psbnodes -a
def pass_pbsnodes(pbsnodes):
	pbsnodes_stdout = subprocess.check_output([pbsnodes, '-a'])
	nodes = []
	
	# For each line in pbsnodes stdout
	for line in pbsnodes_stdout.split('\n'):
		if line.strip():
			# If node name found (assumes node stats are indented with spaces)
			if line[0] != ' ':
				nodes.append({'node_name' : line.strip()})
			else:
				line = line.strip()
				key, value = line.split(' = ')
				nodes[-1][key] = value
	return nodes



if __name__ == "__main__":
	main()
