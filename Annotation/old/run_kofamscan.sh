#!/bin/bash
#SBATCH --partition=main 			# Partition (job queue) 
#SBATCH --no-requeue				# Do not re-run job if preempted
#SBATCH --export=ALL 				# Export current environment variables to the launched application
#SBATCH --nodes=1 				# Number of nodes 
#SBATCH --ntasks=1 				# Number of tasks (usually = cores) on each node
#SBATCH --cpus-per-task=12 			# Cores per task (>1 if multithread tasks)
#SBATCH --output=%x.slurm_out.%j-%2t.%a 	# STDOUT output file (will also contain STDERR if --error is not specified)
#SBATCH --mem=48G 				# Real memory (RAM) per node required (MB) 
#SBATCH --time=72:00:00 			# Total run time limit (HH:MM:SS) 
#SBATCH --job-name=FuncAnnot_kofamscan		# Replace with your jobname


#### Pre-run setup
source ~/slurm_config/slurm_config
prerun_info # Print info
source ~/.bashrc
conda activate kofamscan
cd $SLURM_SUBMIT_DIR

#### Start Script
F=Mcap.protein.fa
run_cmd "~/PROGRAMS/kofamscan-1.1.0/exec_annotation --tmp-dir kofamscan_tmpdir --cpu $SLURM_CPUS_PER_TASK -f detail -o $F.kofamscan_results.detail.txt $F"
run_cmd "~/PROGRAMS/kofamscan-1.1.0/exec_annotation --tmp-dir kofamscan_tmpdir --cpu $SLURM_CPUS_PER_TASK -f mapper -o $F.kofamscan_results.mapper.txt --reannotate $F"
run_cmd "tar -cf kofamscan_tmpdir.tar kofamscan_tmpdir && rm -r kofamscan_tmpdir"

#### Post-run info
postrun_info # Print info


