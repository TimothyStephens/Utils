

## Normalize matrix using DESeq2
Rscript normalize_matrix.R test_data/salmon_combined_HighLowLight.isoform.numreads.matrix

## Get list of differentially expressed genes between any two conditions/time points
Rscript diffExprGenes.R test_data/salmon_combined_HighLowLight.isoform.numreads.matrix.normalized_counts.txt.Filtered_2rep_log2FC samples.txt


## Plot PCA and HeatMap for sample-to-sample comparison
Rscript plot_sample2sample_distances.R


# TPM (transcripts per kilobase million)
IN="test_data/count_matrix_with_Length.txt.gz"
OUT="test_data/test.count_matrix.TPM.txt.gz"
ORIG="test_data/orig.count_matrix.TPM.txt.gz"
Rscript calculateTPM.R $IN $OUT

md5sum <(zcat $ORIG) $OUT

