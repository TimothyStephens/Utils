


python make_contingency_table.py -o test.contingency_table.txt -t single_exon_genes.txt.pfam_scan.out.hmmacc_count -n single_exon_genes.txt.non_target.pfam_scan.out.hmmacc_count
md5sum test.contingency_table.txt single_exon_genes.txt.contingency_table.txt.example


Rscript ../Pfam_enrichment_test.R test.contingency_table.txt
md5sum *sigPvalue*


