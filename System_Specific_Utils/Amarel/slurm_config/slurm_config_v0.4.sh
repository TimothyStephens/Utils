
SLURM_CONFIG_VERSION=0.4
EXITSTATUS=0

#### Pre-run info
function prerun_info() {
	STARTDATE=`date`
	HN=`hostname`
	echo "====================================================================="
	echo "Slurm config version $SLURM_CONFIG_VERSION"
	echo "Starting on $HN at $STARTDATE"
	echo "Nodelist $SLURM_JOB_NODELIST"
	echo "Current JOB_ID is $SLURM_JOB_ID"
	echo "Current array index number is ${SLURM_ARRAY_TASK_ID:-NA}"
	echo "Working directory is $SLURM_SUBMIT_DIR"
	echo "====================================================================="
	echo ""
}

#### Post-run info
function postrun_info() {
	EXITSTATUS=$?
	ENDDATE=`date`
	echo ""
	echo "====================================================================="
	echo "Started: at $STARTDATE on $HN"
	echo "Finished: at $ENDDATE"
	echo "ExitStatus: $EXITSTATUS"
	echo ""
	## Capture info about this job, including max RAM use (MaxRSS):
	sacct --units=G --format JobName,NTasks,AllocCPUs,ReqMem,MaxRSS,MaxVMSize,MaxDiskRead,MaxDiskWrite,TotalCPU,CPUTime,Elapsed -j $SLURM_JOBID
	echo "====================================================================="
}

#### Exit
function set_exitstatus() {
	exit -1
}

#### Function to help keep track of progress. 
function run_cmd(){
        local CMD=$@
	echo "`date`      CMD: $CMD"
        eval $CMD
}

function log(){
        echo "[`date`] $@"
}



###################
#### Run Setup ####
###################
#trap set_exitstatus SIGTERM
trap postrun_info EXIT
prerun_info # Print job info.



######################################
#### Initialize conda environment ####
######################################
# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('/home/ts942/miniconda2/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
	eval "$__conda_setup"
else
	if [ -f "/home/ts942/miniconda2/etc/profile.d/conda.sh" ]; then
		. "/home/ts942/miniconda2/etc/profile.d/conda.sh"
	else
		export PATH="/home/ts942/miniconda2/bin:$PATH"
	fi
fi
unset __conda_setup
# <<< conda initialize <<<



set -euo pipefail
IFS=$'\n\t'
export TMPDIR="/scratch/ts942/tmp"
cd $SLURM_SUBMIT_DIR



