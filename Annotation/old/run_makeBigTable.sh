#!/bin/bash
#SBATCH --partition=main 			# Partition (job queue) 
#SBATCH --no-requeue				# Do not re-run job if preempted
#SBATCH --export=ALL 				# Export current environment variables to the launched application
#SBATCH --nodes=1 				# Number of nodes 
#SBATCH --ntasks=1 				# Number of tasks (usually = cores) on each node
#SBATCH --cpus-per-task=2 			# Cores per task (>1 if multithread tasks)
#SBATCH --output=%x.slurm_out.%j-%2t.%a 	# STDOUT output file (will also contain STDERR if --error is not specified)
#SBATCH --mem=60G 				# Real memory (RAM) per node required (MB) 
#SBATCH --time=72:00:00 			# Total run time limit (HH:MM:SS) 
#SBATCH --job-name=FuncAnnot_makeBigTable 	# Replace with your jobname


#### Pre-run setup
set -e -o pipefail
source ~/slurm_config/slurm_config
prerun_info # Print info
cd $SLURM_SUBMIT_DIR


#### Start Script
F=Mcap.protein.fa

# Big table
grep '>' $F | sed -e 's/>//' | awk 'BEGIN{print "#Seq_ID\tUniProt_TopHit\tGO_terms\tPFAM_Domains\tKEGG_IDs"} {print}' | \
python ~/SCRIPTS/add_value_to_table.py -a $F.mmseqs_easysearch_UniProt.sorted.outfmt6.top1.desc_annot -c 1 -d NA --keep_comments | \
python ~/SCRIPTS/add_value_to_table.py -a $F.mmseqs_easysearch_UniProt.outfmt6.top20_combined.GOtermsAnnot.reformated -c 1 -d NA --keep_comments | \
python ~/SCRIPTS/add_value_to_table.py -a $F.pfam_annotations.2col -c 1 -d NA --keep_comments | \
python ~/SCRIPTS/add_value_to_table.py -a $F.kofamscan_results.mapper.txt.filtered.2col -c 1 -d NA --keep_comments -o $F.annotation_table.txt


#### Post-run info
postrun_info # Print info


