#!/usr/bin/env bash

#### Pre-run setup
source ~/scripts/script_setup.sh
set +eu; conda activate py27; set -eu

#### Get options
NCPUS=1

usage() {
    echo -e "Usage: $(basename "$0") [OPTIONS...]
Options:
-f, --fasta        fasta file to search
-m, --mmseqs       path to mmseqs2 bin
-n, --ncpus        number of threads to use (default: ${NCPUS})
--debug        run debug mode" 1>&2
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
    --debug)
      set -x
      shift # past argument
      ;;
    *)    # unknown option
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


