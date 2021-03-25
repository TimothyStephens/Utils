#!/bin/bash
#SBATCH --partition=main 			# Partition (job queue) 
#SBATCH --no-requeue				# Do not re-run job if preempted
#SBATCH --export=ALL 				# Export current environment variables to the launched application
#SBATCH --nodes=1 				# Number of nodes 
#SBATCH --ntasks=1 				# Number of tasks (usually = cores) on each node
#SBATCH --cpus-per-task=12 			# Cores per task (>1 if multithread tasks)
#SBATCH --output=%x.slurm_out.%j-%2t.%a 	# STDOUT output file (will also contain STDERR if --error is not specified)
#SBATCH --mem=60G 				# Real memory (RAM) per node required (MB) 
#SBATCH --time=72:00:00 			# Total run time limit (HH:MM:SS) 
#SBATCH --job-name=FuncAnnot_UniProt_MMseqs_EasySearch # Replace with your jobname
#SBATCH --array=1-100				# Specify array range


#### Pre-run setup
set -e -o pipefail
source ~/slurm_config/slurm_config
prerun_info # Print info
cd $SLURM_SUBMIT_DIR

# F=Mcap.protein.fa
# ~/SCRIPTS/fasta-splitter.pl --n-parts 100 --out-dir $F.FunctionalAnnotation $F
# ls -1 --color=none $F.FunctionalAnnotation/* > files2run.txt

#### Load list of commands/files into array
index=0
while read line ; do
	index=$(($index+1))
	filearray[$index]="$line"
done < files2run.txt

FILE=${filearray[$SLURM_ARRAY_TASK_ID]}

#### Start Script
run_cmd "srun ./protein_functional_annotation_mmseqs.sh $SLURM_CPUS_PER_TASK $FILE"

#### Post-run info
postrun_info # Print info


