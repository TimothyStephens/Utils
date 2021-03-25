#!/bin/bash
#SBATCH --partition=main 			# Partition (job queue) 
#SBATCH --no-requeue				# Do not re-run job if preempted
#SBATCH --export=ALL 				# Export current environment variables to the launched application
#SBATCH --nodes=1 				# Number of nodes 
#SBATCH --ntasks=1 				# Number of tasks (usually = cores) on each node
#SBATCH --cpus-per-task=2 			# Cores per task (>1 if multithread tasks)
#SBATCH --output=%x.slurm_out.%j-%2t.%a 	# STDOUT output file (will also contain STDERR if --error is not specified)
#SBATCH --mem=100G 				# Real memory (RAM) per node required (MB) 
#SBATCH --time=72:00:00 			# Total run time limit (HH:MM:SS) 
#SBATCH --job-name=FuncAnnot_PostProcessing	# Replace with your jobname


#### Pre-run setup
set -e -o pipefail
source ~/slurm_config/slurm_config
prerun_info # Print info
cd $SLURM_SUBMIT_DIR

#### Start Script
F=Mcap.protein.fa

UTIL=/scratch/ts942/GitHub_dev/Utils/scripts/Annotation_Tools
BLAST_UTILS=~/SCRIPTS

##
## Pfamscan
##
## <seq id> <alignment start> <alignment end> <envelope start> <envelope end> <hmm acc> <hmm name> <type> <hmm start> <hmm end> <hmm length> <bit score> <E-value> <significance> <clan>
cat $F.FunctionalAnnotation/*.part-*.fa.pfam_scan.out | awk '$1!~"^#" && $1!~"^$"' | gzip -c > $F.pfam_scan.out.gz
# Filter by e-value <0.001
zcat $F.pfam_scan.out.gz | python $UTIL/pfam_to_2col_annotation.py -o $F.pfam_annotations.2col



##
## kofamscan
##
awk '$2!=""' $F.kofamscan_results.mapper.txt > $F.kofamscan_results.mapper.txt.filtered
python $UTIL/kofam_to_2col_annotation.py -i $F.kofamscan_results.mapper.txt.filtered -o $F.kofamscan_results.mapper.txt.filtered.2col



##
## UniProt
##
cat $F.FunctionalAnnotation/*.part-*.fa.mmseqs_easysearch_swissprot.outfmt6 | awk -F'\t' '$11<1e-5' | gzip -c > $F.mmseqs_easysearch_swissprot.outfmt6.gz
cat $F.FunctionalAnnotation/*.part-*.fa.mmseqs_easysearch_trembl.outfmt6 | awk -F'\t' '$11<1e-5' | gzip -c > $F.mmseqs_easysearch_trembl.outfmt6.gz

zcat $F.mmseqs_easysearch_swissprot.outfmt6.gz | $BLAST_UTILS/blast_top_hits.py -o $F.mmseqs_easysearch_swissprot.outfmt6.top20 -s 20 -n 1
zcat $F.mmseqs_easysearch_trembl.outfmt6.gz | $BLAST_UTILS/blast_top_hits.py -o $F.mmseqs_easysearch_trembl.outfmt6.top20 -s 20 -n 1
cat $F.mmseqs_easysearch_swissprot.outfmt6.top20 $F.mmseqs_easysearch_trembl.outfmt6.top20 > $F.mmseqs_easysearch_UniProt.outfmt6.top20_combined

zcat $F.mmseqs_easysearch_swissprot.outfmt6.gz $F.mmseqs_easysearch_trembl.outfmt6.gz | sort -k1,1 -k12,12n | gzip -c > $F.mmseqs_easysearch_UniProt.sorted.outfmt6.gz

# UniProt TopHit description annots
zcat $F.mmseqs_easysearch_UniProt.sorted.outfmt6.gz | ~/SCRIPTS/blast_top_hits.py -s 1 -n 1 -o $F.mmseqs_easysearch_UniProt.sorted.outfmt6.top1
cut -f1,15- $F.mmseqs_easysearch_UniProt.sorted.outfmt6.top1 | sed -e 's/\t/ /g' | sed -e 's/ /\t/' > $F.mmseqs_easysearch_UniProt.sorted.outfmt6.top1.desc_annot



#### Post-run info
postrun_info # Print info


