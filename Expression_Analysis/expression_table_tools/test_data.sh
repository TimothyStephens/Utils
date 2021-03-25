

Rscript filter_low_count_genes_by_minCount_in_minSamples.R test_data/test_10x10.matrix test_data/test_10x10.matrix.out1 5 2
Rscript filter_low_count_genes_by_minCount_in_minSamples.R test_data/test_10x10.matrix test_data/test_10x10.matrix.out2 5 1

Rscript filter_low_count_genes_by_minCPM_in_minSamples.R test_data/test_10x10.matrix test_data/test_10x10.matrix.out3 5 2
Rscript filter_low_count_genes_by_minCPM_in_minSamples.R test_data/test_10x10.matrix test_data/test_10x10.matrix.out4 5 1


diff test_data/test_10x10.matrix.out1 test_data/test_10x10.matrix.expected_output_1
diff test_data/test_10x10.matrix.out2 test_data/test_10x10.matrix.expected_output_2
diff test_data/test_10x10.matrix.out3 test_data/test_10x10.matrix.expected_output_1
diff test_data/test_10x10.matrix.out4 test_data/test_10x10.matrix.expected_output_2


Rscript sum_matrix_rows.R test_data/test_10x10.matrix test_data/test_10x10.matrix.rowSums
Rscript sum_matrix_columns.R test_data/test_10x10.matrix test_data/test_10x10.matrix.columnSums



diff test_data/test_10x10.matrix.rowSums test_data/test_10x10.matrix.expected_rowSums
diff test_data/test_10x10.matrix.columnSums test_data/test_10x10.matrix.expected_columnSums





##
## Melt expression table
##
IN="test_data/normalized_counts"
OUT="test_data/test.normalized_counts.melted.txt"
ORIG="test_data/orig.normalized_counts.melted.txt.gz"
python melt_table.py -i $IN.CL.txt.gz | awk '{ if (NR!=1) {print $0"\tCL"} else {print $0"\tCondition"} }' > $OUT
python melt_table.py -i $IN.HL.txt.gz | awk '{ if (NR!=1) {print $0"\tHL"} }' >> $OUT

md5sum <(zcat $ORIG) <(cat $OUT)


