#!/usr/bin/env bash

# Print all info to log file
exec 1> "${0}.log.$(date +%s)" 2>&1

#### Pre-run setup
source ~/scripts/script_setup.sh
set +eu; conda activate main; set -eu


#### Start Script
rsync -avP ts942@amarel.rutgers.edu:/scratch/ts942/* Amarel/

