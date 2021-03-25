#!/bin/bash
NCPUS="$1"
FILE="$2"

#### Function to help keep track of progress.
function run_cmd(){
        local CMD=$@
        echo "`date`      CMD: $CMD"
        eval $CMD
	# Catch command exit status and react acordingly
	EXIT_STATUS=$?
	if [ $EXIT_STATUS -gt 0 ];
	then
		exit $EXIT_STATUS
	fi	
}


#### Start Script
SWISSPROT_DB=/scratch/ts942/DATABASES/UniProt_2019_10/uniprot_sprot.fasta
TREMBL_DB=/scratch/ts942/DATABASES/UniProt_2019_10/uniprot_trembl.fasta
PFAM_A=/scratch/ts942/DATABASES/PFAM/32.0

export PATH=$PATH:~/PROGRAMS/diamond_v0.9.29-linux64
export PATH=$PATH:~/PROGRAMS/hmmer-3.1b2/bin
export PFAM_SCAN=~/PROGRAMS/PfamScan
export PERL5LIB=$PFAM_SCAN:$PFAM_SCAN/lib/perl5/
export PERL=/usr/bin/perl

## START: Check options set
if [ -z $FILE ]; then echo "No file name given!"; exit 1; fi
if [ -z $NCPUS ]; then echo "No ncpus given!"; exit 1; fi
## END: Check options set

## START: Check parsed options
if [ ! -s $FILE ]; then echo "$FILE does not exist!"; exit 1; fi
if [  $NCPUS -lt 1 ]; then echo "$NCPUS should be a number > zero!"; exit 1; fi
## END: Check parsed options

## START: Check execuatble
FAIL_COUNT=0
for PROG in "diamond" "$PFAM_SCAN/pfamscan.pl";
do 
	hash $PROG 2>/dev/null || { echo >&2 "[ERROR]: $PROG missing from PATH."; FAIL_COUNT=$((FAIL_COUNT+1)); }
done
if [ $FAIL_COUNT -gt 0 ]; then echo "...Aborting!"; exit 1; fi
## END: Check execuatble


## SwissProt
SWISSPROT_OUT=$FILE.diamond_blastp_swissprot.outfmt6
if [ ! -f $SWISSPROT_OUT ];
then
	run_cmd "srun diamond blastp --more-sensitive --query $FILE --db $SWISSPROT_DB --out $SWISSPROT_OUT.WORKING --max-target-seqs 100 --outfmt 6 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore qlen slen --threads $NCPUS && mv $SWISSPROT_OUT.WORKING $SWISSPROT_OUT"
else
	echo "$SWISSPROT_OUT already exists!"
fi

## TrEMBL
TREMBL_OUT=$FILE.diamond_blastp_trembl.outfmt6
if [ ! -f $TREMBL_OUT ];
then
	run_cmd "srun diamond blastp --more-sensitive --query $FILE --db $TREMBL_DB --out $TREMBL_OUT.WORKING --max-target-seqs 100 --outfmt 6 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore qlen slen --threads $NCPUS && mv $TREMBL_OUT.WORKING $TREMBL_OUT"
else
	echo "$TREMBL_OUT already exists!"
fi

## PfamA
PFAM_OUT=$FILE.pfam_scan.out
if [ ! -f $PFAM_OUT ];
then
        run_cmd "srun $PERL $PFAM_SCAN/pfam_scan.pl -fasta $FILE -dir $PFAM_A -outfile $PFAM_OUT.WORKING -cpu $NCPUS && mv $PFAM_OUT.WORKING $PFAM_OUT"
else
        echo "$PFAM_OUT already exists!"
fi

## Done
echo "`date`      Functional annotation done!"


