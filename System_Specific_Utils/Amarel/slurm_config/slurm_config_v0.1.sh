
slurm_config_version=0.1
EXITSTATUS=0

#### Pre-run info
function prerun_info() {
	STARTDATE=`date`
	HN=`hostname`
	echo "====================================================================="
	echo "Slurm config version $slurm_config_version"
	echo "Starting on $HN at $STARTDATE"
	echo "Nodelist $SLURM_JOB_NODELIST"
	echo "Current JOB_ID is $SLURM_JOB_ID"
	echo "Current array index number is $SLURM_ARRAY_TASK_ID"
	echo "Working directory is $SLURM_SUBMIT_DIR"
	echo "====================================================================="
	echo ""
}

#### Post-run info
function postrun_info() {
	ENDDATE=`date`
	echo ""
	echo "====================================================================="
	echo "Started: at $STARTDATE on $HN"
	echo "Finished: at $ENDDATE"
	echo "ExitStatus: $EXITSTATUS"
	echo ""
	## Capture info about this job, including max RAM use (MaxRSS):
	sleep 3
	sacct --format NTasks,AllocCPUs,MaxRSS,AveRSS,AveCPU,Elapsed -j $SLURM_JOBID
	sleep 3
	echo "====================================================================="
}


#### Function to help keep track of progress. 
function run_cmd(){
        local CMD=$@
	echo "`date`      CMD: $CMD"
        eval $CMD
	EXITSTATUS=$?
	if [ $EXITSTATUS -ne 0 ]; 
	then
		postrun_info
		exit $EXITSTATUS
	fi
}



