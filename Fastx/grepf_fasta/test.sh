

cat test_data/test.fasta | python grepf_fasta.py -s test_data/test.names | md5sum
2a64664b025bcf339ee4fbac27dce012  -

grep -f test_data/test.names -A 1 test_data/test.fasta | grep -v '\-\-' | awk '{print $1}' | md5sum
2a64664b025bcf339ee4fbac27dce012  -



