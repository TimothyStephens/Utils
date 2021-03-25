#!/usr/bin/env bash

#### Pre-run setup
source ~/scripts/script_setup.sh
set +eu; conda activate py27; set -eu

#### Get options
NCPUS=1
SENSITIVITY=7.5

usage() {
    echo -e "Usage: $(basename "$0") [OPTIONS...]
Options:
--fasta        fasta file to search
--sensitivity  mmseq2 sensitivity (default: 7.5)
--mmseqs       path to mmseqs2 bin
--hmmer        path to hmmer-3.1b2 bin
--pfamscan     path to pfanscan bin
--swisprot     SwissProt MMSEQ2 DB
--trembl       TrEMBL MMSEQ2 DB
--pfam         PFAM_A DB
--ncpus        number of threads to use (default: 1)" 1>&2
    exit 1
}

OPT_LIST="fasta:,sensitivity:,mmseqs:,hmmer:,pfamscan:,swisprot:,trembl:,pfam:,ncpus:,debug"

eval set -- "$(getopt -o '' --long "${OPT_LIST}" -- "$@")"

while true; do
    case "$1" in
    --fasta)
        FASTA=$2
        shift 2
        ;;
    --sensitivity)
	SENSITIVITY=$2
	shift 2
	;;
    --mmseqs)
        MMSEQS_BIN=$2
        shift 2
        ;;
    --hmmer)
        HMMER_BIN=$2
        shift 2
        ;;
    --pfamscan)
        PFAMSCAN=$2
        shift 2
        ;;
    --swisprot)
        SWISSPROT_DB=$2
        shift 2
        ;;
    --trembl)
        TREMBL_DB=$2
        shift 2
        ;;
    --pfam)
        PFAM_A=$2
        shift 2
        ;;
    --ncpus)
        NCPUS=$2
        shift 2
        ;;
    --debug)
       	set -x
       	shift
       	;;
    --)
        shift
        break
        ;;
    *)
        usage
        ;;
    esac
done

set +eu
if [ -z "${FASTA}" ] || [ -z "${MMSEQS_BIN}" ] || [ -z "${HMMER_BIN}" ] || [ -z "${PFAMSCAN}" ] ||
    [ -z "${SWISSPROT_DB}" ] || [ -z "${TREMBL_DB}" ] || [ -z "${PFAM_A}" ] || [ -z "${NCPUS}" ]; then
    usage
fi
set -eu

#### Setup env
export PATH=$PATH:"${MMSEQS_BIN}"
export PATH=$PATH:"${HMMER_BIN}"
export PFAM_SCAN="${PFAMSCAN}"
export PERL5LIB=$PFAM_SCAN:$PFAM_SCAN/Bio

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


###############
## SwissProt ##
###############
SWISSPROT_OUT="$FASTA.mmseqs_swissprot.outfmt6"
if [ ! -f $SWISSPROT_OUT ];
then
	run_cmd "rm -fr $SWISSPROT_OUT.WORKING.TMPDIR; mkdir -p $SWISSPROT_OUT.WORKING.TMPDIR"
	OUTFMT="query,target,pident,alnlen,mismatch,gapopen,qstart,qend,tstart,tend,evalue,bits,qlen,tlen,theader"
	run_cmd "mmseqs easy-search $FASTA $SWISSPROT_DB $SWISSPROT_OUT.WORKING $SWISSPROT_OUT.WORKING.TMPDIR -s $SENSITIVITY --format-output $OUTFMT --threads $NCPUS && mv $SWISSPROT_OUT.WORKING $SWISSPROT_OUT"
	run_cmd "rm -fr $SWISSPROT_OUT.WORKING.TMPDIR"
else
	log "$SWISSPROT_OUT already exists!"
fi

############
## TrEMBL ##
############
TREMBL_OUT="$FASTA.mmseqs_trembl.outfmt6"
if [ ! -f $TREMBL_OUT ];
then
	run_cmd "rm -fr $TREMBL_OUT.WORKING.TMPDIR; mkdir -p $TREMBL_OUT.WORKING.TMPDIR"
	OUTFMT="query,target,pident,alnlen,mismatch,gapopen,qstart,qend,tstart,tend,evalue,bits,qlen,tlen,theader"
	run_cmd "mmseqs easy-search $FASTA $TREMBL_DB $TREMBL_OUT.WORKING $TREMBL_OUT.WORKING.TMPDIR -s $SENSITIVITY --format-output $OUTFMT --threads $NCPUS && mv $TREMBL_OUT.WORKING $TREMBL_OUT"
	run_cmd "rm -fr $TREMBL_OUT.WORKING.TMPDIR"
else
	log "$TREMBL_OUT already exists!"
fi

###########
## PfamA ##
###########
PFAM_OUT="$FASTA.pfam_scan.out"
if [ ! -f $PFAM_OUT ];
then
	run_cmd "$PFAM_SCAN/pfam_scan.pl -fasta $FASTA -dir $PFAM_A -outfile $PFAM_OUT.WORKING -cpu $NCPUS && mv $PFAM_OUT.WORKING $PFAM_OUT"
else
	log "$PFAM_OUT already exists!"
fi

## Done
log "Functional annotation done!"


