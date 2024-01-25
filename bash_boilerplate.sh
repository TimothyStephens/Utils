#!/usr/bin/env bash

VERSION="0.1"

## Pre-run setup
set -euo pipefail
IFS=$'\n\t'

# Absolute path to this script, e.g. /home/user/bin/foo.sh
SCRIPT=$(readlink -f "$0")
# Absolute path this script is in, thus /home/user/bin
SCRIPTPATH=$(dirname "$SCRIPT")


## Helper functions
function run_cmd(){
local CMD="$@"
  echo -t "[`date`]\tCMD: $CMD"
  eval $CMD
}

function log(){
  echo -e "[`date`]\tLOG: $@"
}

function err(){
  echo -e "[`date`]\tERROR: $@" >&2
}

function check_empty(){
if [[ ! -s "${1}" ]];
  then
    err "${1} is empty!"
    exit 2
  fi
}


## Set option envs
HITS_IN=/dev/stdin
HITS_OUT=/dev/stdout
TAXID_COL=5
TARGET_TAXA_LEVEL="order"
NUM_TAXIDS_PER_TAXA=1
NUM_SEQS_PER_TAXID=10
LINEAGE="$SCRIPTPATH/lineages.slim.tsv.gz"
LINEAGE_DEFAULT=$'NA\tNA\tNA\tNA\tNA\tNA\tNA\tNA\tNA\tNA\tNA\tNA\tNA\tNA'
ADD_VALUE="$SCRIPTPATH/add_value_to_table_SQLite3.py"

## Useage information
usage() {
echo -e "##
## $(basename ${0}) v${VERSION}
##

<<<DESCRIPTION>>>

Usage: 
./$(basename $0) -i blast_hits.outfmt6 -o blast_hits.downsampled.outfmt6
*OR*
cat blast_hits.outfmt6 | ./$(basename $0) > blast_hits.downsampled.outfmt6

Options (all optional):
-i, --hits_in              File with input BLAST/DIAMOND hits (default: stdin)
-o, --hits_out             File with output downsampled BLAST/DIAMOND hits (default: stdout)
-s, --num_seqs_per_taxid   No of seqs to return per top scoring taxon ID within each '--target_taxa' (default: $NUM_SEQS_PER_TAXID)

-v, --version              Script version (v${VERSION})
-h, --help                 This help message
--debug                    Run debug mode
" 1>&2
exit 1
}


# See https://stackoverflow.com/questions/192249/how-do-i-parse-command-line-arguments-in-bash

POSITIONAL=()
while [[ $# -gt 0 ]]; do
  key="$1"

  case $key in
    -f|--fasta)
      FASTA="$2"
      shift # past argument
      shift # past value
      ;;
    -m|--mmseqs)
      MMSEQS_BIN="$2"
      shift # past argument
      shift # past value
      ;;
    -n|--ncpus)
      NCPUS="$2"
      shift # past argument
      shift # past value
      ;;
    -h|--help)
      usage
      exit 1;
      ;;
    -v|--version)
      echo "v${VERSION}"
      exit 0;
      ;;
    --debug)
      set -x
      shift # past argument
      ;;
    *) # unknown option
      POSITIONAL+=("$1") # save it in an array for later
      shift # past argument
      ;;
  esac
done

set -- "${POSITIONAL[@]}" # restore positional parameters


set +eu
if [ -z "${FASTA}" ] || [ -z "${MMSEQS_BIN}" ] ||
    [ -z "${NCPUS}" ]; then
    usage
fi
set -eu

#### Setup env
export PATH=$PATH:"${MMSEQS_BIN}"

## START: Check options set
if [ -z $FASTA ]; then log "No file name given!"; exit 1; fi
if [ ! -s $FASTA ]; then log "$FASTA does not exist!"; exit 1; fi
## END: Check parsed options

## START: Check execuatble
FAIL_COUNT=0
for PROG in "mmseqs" "$PFAM_SCAN/pfamscan.pl";
do 
	hash $PROG 2>/dev/null || { echo >&2 "[ERROR]: $PROG missing from PATH."; FAIL_COUNT=$((FAIL_COUNT+1)); }
done
if [ $FAIL_COUNT -gt 0 ]; then echo "...Aborting!"; exit 1; fi
## END: Check execuatble


