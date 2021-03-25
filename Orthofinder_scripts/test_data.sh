
python Orthogroups_tsv_to_single_line.py -i test_data/Orthogroups.tsv.gz -o test_data/test.Orthogroups.SingleLine.tsv.gz

md5sum <(zcat test_data/orig.Orthogroups.SingleLine.tsv.gz) <(zcat test_data/test.Orthogroups.SingleLine.tsv.gz)

