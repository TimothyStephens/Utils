#!/bin/bash
#SBATCH --partition=main 			# Partition (job queue) 
#SBATCH --no-requeue				# Do not re-run job if preempted
#SBATCH --export=ALL 				# Export current environment variables to the launched application
#SBATCH --nodes=1 				# Number of nodes 
#SBATCH --ntasks=1 				# Number of tasks (usually = cores) on each node
#SBATCH --cpus-per-task=2 			# Cores per task (>1 if multithread tasks)
#SBATCH --output=%x.slurm_out.%j-%2t.%a 	# STDOUT output file (will also contain STDERR if --error is not specified)
#SBATCH --mem=48G 				# Real memory (RAM) per node required (MB) 
#SBATCH --time=72:00:00 			# Total run time limit (HH:MM:SS) 
#SBATCH --job-name=FuncAnnot_GOterms		# Replace with your jobname


#### Pre-run setup
set -e -o pipefail
source ~/slurm_config/slurm_config
prerun_info # Print info
cd $SLURM_SUBMIT_DIR


BLAST="Mcap.protein.fa.mmseqs_easysearch_UniProt.outfmt6.top20_combined"
DB="/scratch/ts942/DATABASES/GOA_UniProt_2019_11/GOterms_UniProtKB_Mapping_Release_2019_10.sqlite3"

#### Start Script
run_cmd "srun python /scratch/ts942/GitHub_dev/Utils/scripts/Annotation_Tools/Annotate_GO_From_BLAST_topGO_noLoadBlast.py --mmseq2 --blast $BLAST --out $BLAST.GOtermsAnnot --db $DB"
cat $F.mmseqs_easysearch_UniProt.outfmt6.top20_combined.GOtermsAnnot | sed -e 's/, /,/g' > $F.mmseqs_easysearch_UniProt.outfmt6.top20_combined.GOtermsAnnot.reformated


#### Post-run info
postrun_info # Print info


