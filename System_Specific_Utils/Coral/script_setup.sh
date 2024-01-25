
##########################
#### Helper Functions ####
##########################
CONFIG_VERSION="0.4"
EXITSTATUS=0


#### Function to help keep track of progress.
function run_cmd(){
        local CMD="$@"
        echo -e "[`date`]\tCMD: $CMD"
        eval $CMD
}

function log(){
        echo -e "[`date`]\tLOG: $@"
}


#### Pre-run info
function prerun_info() {
        START=`date +%s`
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
        END=`date +%s`
        ENDDATE=`date`
        RUNTIME=$(( END-START ))
        HOURS=$(  printf "%02g" $(( (RUNTIME / 3600)      )) )
        MINUTES=$(printf "%02g" $(( (RUNTIME % 3600) / 60 )) )
        SECONDs=$(printf "%02g" $(( (RUNTIME % 3600) % 60 )) )
        echo ""
        echo "====================================================================="
        echo "Started: at $STARTDATE"
        echo "Finished: at $ENDDATE"
        echo "Runtime (hh:mm:ss): $HOURS:$MINUTES:$SECONDs"
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
__conda_setup="$('/home/timothy/miniforge3/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/home/timothy/miniforge3/etc/profile.d/conda.sh" ]; then
        . "/home/timothy/miniforge3/etc/profile.d/conda.sh"
    else
        export PATH="/home/timothy/miniforge3/bin:$PATH"
    fi
fi
unset __conda_setup

if [ -f "/home/timothy/miniforge3/etc/profile.d/mamba.sh" ]; then
    . "/home/timothy/miniforge3/etc/profile.d/mamba.sh"
fi
# <<< conda initialize <<<



set -euo pipefail
IFS=$'\n\t'
export TMPDIR="/scratch/$USER/tmp"

