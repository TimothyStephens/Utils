#!/bin/bash
#SBATCH --partition=main 			# Partition (job queue) 
#SBATCH --no-requeue				# Do not re-run job if preempted
#SBATCH --export=ALL 				# Export current environment variables to the launched application
#SBATCH --nodes=1 				# Number of nodes 
#SBATCH --ntasks=1 				# Number of tasks (usually = cores) on each node
#SBATCH --cpus-per-task=24 			# Cores per task (>1 if multithread tasks)
#SBATCH --output=%x.slurm_out.%j-%2t.%a 	# STDOUT output file (will also contain STDERR if --error is not specified)
#SBATCH --mem=10G 				# Real memory (RAM) per node required (MB) 
#SBATCH --time=72:00:00 			# Total run time limit (HH:MM:SS) 
#SBATCH --job-name=test_array 			# Replace with your jobname
#SBATCH --array=1-30				# Specify array range


#### Pre-run setup
source ~/slurm_config/slurm_config_v0.4.sh
set +eu; conda activate base; set -eu


#### Load list of commands/files into array
index=0
while read line ; do
	index=$(($index+1))
	filearray[$index]="$line"
done < files2run.txt
echo "Line selected from list of files is ${filearray[$SLURM_ARRAY_TASK_ID]}"


#### Start Script
run_cmd "srun jobscript.sh ${filearray[$SLURM_ARRAY_TASK_ID]}"
run_cmd "srun jobscript.sh $SLURM_CPUS_PER_TASK"
run_cmd "srun jobscript.sh $SLURM_ARRAY_TASK_ID"


