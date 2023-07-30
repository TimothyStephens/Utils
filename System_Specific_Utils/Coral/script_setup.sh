
##########################
#### Helper Functions ####
##########################
CONFIG_VERSION="0.2"
EXITSTATUS=0


#### Function to help keep track of progress.
function run_cmd(){
        local CMD="$@"
        echo "[`date`]      CMD: $CMD"
        eval $CMD
}

function log(){
        echo "[`date`]      LOG: $@"
}


#### Pre-run info
function prerun_info() {
        STARTDATE=`date`
        echo "====================================================================="
	echo "Slurm config version $CONFIG_VERSION"
        echo "Starting at $STARTDATE"
        echo "Working directory is $PWD"
        echo "====================================================================="
        echo ""
}


#### Post-run info
function postrun_info() {
        EXITSTATUS=$?
        ENDDATE=`date`
        echo ""
        echo "====================================================================="
        echo "Started: at $STARTDATE"
        echo "Finished: at $ENDDATE"
        echo "ExitStatus: $EXITSTATUS"
        echo "====================================================================="
}



###################
#### Run Setup ####
###################
trap postrun_info EXIT # Print job info upon failure
prerun_info # Print job info at start



######################################
#### Initialize conda environment ####
######################################
# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('/home/timothy/miniconda3/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/home/timothy/miniconda3/etc/profile.d/conda.sh" ]; then
        . "/home/timothy/miniconda3/etc/profile.d/conda.sh"
    else
        export PATH="/home/timothy/miniconda3/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<



set -euo pipefail
IFS=$'\n\t'
export TMPDIR="/scratch/$USER/tmp"

