
conda activate python-2.7
export PYTHONPATH=~/miniconda2/envs/python-2.7/lib/python2.7:~/miniconda2/envs/python-2.7/lib/python2.7/site-packages

B="test_data_big/aligned_reads.bam"
P="test_data_big/test.SL_from_mapped_reads"
cat test_data_big/seq_names.txt | ./mapped_reads_with_SL_sequences.py -b $B -o $P.txt --info $P.SL_read_info.txt -s CCGGCTTTTCTG 2> $P.debug.log

O="test_data_big/orig.SL_from_mapped_reads"
md5sum <(zcat $O.txt.gz | sort) <(cat $P.txt | sort)
md5sum <(zcat $O.SL_read_info.txt.gz | sort) <(cat $P.SL_read_info.txt | sort)
md5sum <(zcat $O.debug.log.gz | cut -d' ' -f2- | sort) <(cat $P.debug.log | cut -d' ' -f2- | sort)

## Full debug info
cat test_data_big/seq_names.txt | ./mapped_reads_with_SL_sequences.py -b $B -o $P.txt --info $P.SL_read_info.txt -s CCGGCTTTTCTG --debug 2> $P.debug.log_full


