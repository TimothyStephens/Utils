#!/usr/bin/env bash

VERSION="0.1"

## Pre-run setup
set -euo pipefail
IFS=$'\n\t'

# Absolute path to this script, e.g. /home/user/bin/foo.sh
SCRIPT=$(readlink -f "$0")
# Absolute path this script is in, thus /home/user/bin
SCRIPTPATH=$(dirname "$SCRIPT")


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

A script to downsample hits from either BLAST or DIAMOND searches with reported Taxon IDs.

By default, the script will search in column number $TAXID_COL of the input hits file 
for the Taxon ID of each subject sequence. Then for each query, the script will return a 
maximum of $NUM_SEQS_PER_TAXID sequences per Taxon ID, with at most $NUM_TAXIDS_PER_TAXA Taxon IDs returned 
per unique taxa at the $TARGET_TAXA_LEVEL level.
That is, the script will downsample to the $TARGET_TAXA_LEVEL level, returning <=$NUM_SEQS_PER_TAXID sequences per Taxon ID, 
with <=$NUM_TAXIDS_PER_TAXA Taxon IDs returned per unique taxa at the $TARGET_TAXA_LEVEL level.

The output of the script will be the selected hits + the full lineage information used for downsampling.
The new columns added will be (in order): species,genus,subfamily,family,suborder,order,subclass,class,phylum,clade1,kingdom,clade,superkingdom,no rank


Usage: 
./$(basename $0) -i blast_hits.outfmt6 -o blast_hits.downsampled.outfmt6
*OR*
cat blast_hits.outfmt6 | ./$(basename $0) > blast_hits.downsampled.outfmt6
*OR*
cat blast_hits.outfmt6 | ./$(basename $0) --taxid_col 12 --target_taxa class --num_taxids_per_taxa 8 --num_seqs_per_taxid 5 > blast_hits.downsampled.outfmt6
# Last command will use column 12 in 'blast_hits.outfmt6' as Taxon ID and will return max 5 sequences per Taxon ID, with
# a max of 8 Taxon IDs returned per unique taxa at the 'class' level.

Options (all optional):
-i, --hits_in              File with input BLAST/DIAMOND hits (default: stdin)
-o, --hits_out             File with output downsampled BLAST/DIAMOND hits (default: stdout)
-t, --taxid_col            Column ID (1-based index) with taxon IDs in it (default: $TAXID_COL)
-x, --target_taxa          Taxon level to consider (options: 'genus,subfamily,family,suborder,order,subclass,class,phylum,clade1,kingdom,clade,superkingdom,no rank'; default: $TARGET_TAXA_LEVEL)
-n, --num_taxids_per_taxa  No of top scoring taxon IDs to return per '--target_taxa' (default: $NUM_TAXIDS_PER_TAXA)
-s, --num_seqs_per_taxid   No of seqs to return per top scoring taxon ID within each '--target_taxa' (default: $NUM_SEQS_PER_TAXID)

-v, --version              Script version (v${VERSION})
-h, --help                 This help message
--debug                    Run debug mode
" 1>&2
exit 1
}


## Get options
POSITIONAL=()
while [[ $# -gt 0 ]]; do
  key="${1}"
  case $key in
    -h|--help)
      usage
      exit 1;
      ;;
      -v|--version)
      echo "v${VERSION}"
      exit 0;
      ;;
    -i|--hits_in)
      HITS_IN="${2}"
      shift 2;
      ;;
    -o|--hits_out)
      HITS_OUT="${2}"
      shift 2;
      ;;
    -t|--taxid_col)
      TAXID_COL="${2}"
      shift 2;
      ;;
    -x|--target_taxa)
      TARGET_TAXA_LEVEL="${2}"
      shift 2;
      ;;
    -n|--num_taxids_per_taxa)
      NUM_TAXIDS_PER_TAXA="${2}"
      shift 2;
      ;;
    -s|--num_seqs_per_taxid)
      NUM_SEQS_PER_TAXID="${2}"
      shift 2;
      ;;
    --debug)
      set -x
      shift;
      ;;
    *) # unknown option
      POSITIONAL+=("$1") # save an array for later
      shift;
      ;;
  esac
done
#set -- "${POSITIONAL[@]}" # restore positional parameters


## Get columns from lineage file to process
# Since we are going to add the lineage into to this file 
# we need to keep in mind how many columns we are starting with.
#
# COL	NAME		ADJ_COL
# 1	tax_id		ignored
# 2	species		-14
# 3	genus		-13
# 4	subfamily	-12
# 5	family		-11
# 6	suborder	-10
# 7	order		-9
# 8	subclass	-8
# 9	class		-7
# 10	phylum		-6
# 11	clade1		-5
# 12	kingdom		-4
# 13	clade		-3
# 14	superkingdom	-2
# 15	no rank		-1

# Get the column offset (i.e., distance from right of table) of our chosen taxa_col.
TARGET_TAXA_COL=$(zcat "${LINEAGE}" | awk -F'\t' -vTARGET_TAXA_LEVEL="${TARGET_TAXA_LEVEL}" 'NR==1{ COL="NA"; for(i=3; i<=NF; i++){ if(TARGET_TAXA_LEVEL==$i){COL=(NF-i)+1} }; print COL }')
if [[ "$TARGET_TAXA_COL" == "NA" ]]; then
  echo "ERROR: '--target_taxa' ($TARGET_TAXA_LEVEL) was not found in lineage file." 1>&2
  exit 1
fi


## Add lineage info to hits and then filter the hits by lineage info and the info supplied by the user.
cat ${HITS_IN} \
  | "${ADD_VALUE}" \
      -c "${TAXID_COL}" \
      -a <(zcat "${LINEAGE}") \
      -d "${LINEAGE_DEFAULT}" \
  | awk \
      -F'\t' \
      -vTARGET_TAXA_COL="$TARGET_TAXA_COL" \
      -vTAXID_COL="$TAXID_COL" \
      -vNUM_TAXIDS_PER_TAXA="$NUM_TAXIDS_PER_TAXA" \
      -vNUM_SEQS_PER_TAXID="$NUM_SEQS_PER_TAXID" \
    '{
      TAXA_COL=(NF-TARGET_TAXA_COL)+1
      TAXID=$TAXID_COL
      
      TAXA_LINEAGE=$1
      for(i=TAXA_COL; i<=NF; i++){
        TAXA_LINEAGE=TAXA_LINEAGE";"$i
      }
      HIT_LINEAGE=TAXID";"TAXA_LINEAGE
      
      SEEN[TAXA_LINEAGE][TAXID]++
      if(KEEP[HIT_LINEAGE] > 0 || length(SEEN[TAXA_LINEAGE]) <= NUM_TAXIDS_PER_TAXA){
        KEEP[HIT_LINEAGE]++
      }
      
      if(KEEP[HIT_LINEAGE] > 0 && KEEP[HIT_LINEAGE] <= NUM_SEQS_PER_TAXID){
        print $0
      }
    }' \
  > "${HITS_OUT}"



