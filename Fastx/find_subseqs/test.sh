
./find_subseqs.py -q test_data/short.fa -s test_data/long.fa -o test_data/out.bed
diff test_data/out.bed test_data/out.bed.expected

