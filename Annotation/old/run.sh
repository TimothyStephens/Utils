



F=Mcap.protein.fa



ll $F.FunctionalAnnotation/*.part-*.fa.mmseqs_easysearch_swissprot.outfmt6 | wc -l
ll $F.FunctionalAnnotation/*.part-*.fa.mmseqs_easysearch_trembl.outfmt6 | wc -l
ll $F.FunctionalAnnotation/*.part-*.fa.pfam_scan.out | wc -l


run_kofamscan.sh
run_FuncAnnot_MMseqs_array.sh
# Wait till scripts finish
sbatch run_PostProcessing.sh
sbatch run_AnnotGOterms.sh
# Wait till scripts finish
sbatch run_makeBigTable.sh



