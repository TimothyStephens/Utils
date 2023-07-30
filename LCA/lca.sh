#!/usr/bin/env bash



## Pre-run setup
set -euo pipefail
IFS=$'\n\t'



## Helper functions
function log(){
  echo -e "[`date`]\tLOG: $@"
}


LINEAGE="lineage.tsv"


# Envs to store strat info
BEST_STRATA=""
BEST_STRATA_TAXA=""
BEST_STRATA_COUNT=""
BEST_STRATA_COLUMN=""

log "    - Parsing each strata"
NCOLS=$(awk -F'\t' 'NR==1{print NF}' "${LINEAGE}")
for STRATA_COLUMN_NUMBER in $(seq 3 "${NCOLS}" | tac);
do
  STRATA=$(awk -F'\t' -vS="${STRATA_COLUMN_NUMBER}" 'NR==1{print $S}' "${LINEAGE}")
  log "    - Strata: ${STRATA} (from column number: ${STRATA_COLUMN_NUMBER})"
  #
  CLUSTER_STRATA=$(awk -F'\t' -vC="${STRATA_COLUMN_NUMBER}" 'NR>1{TAXON[$C]++} END{for(T in TAXON){print T"\t"TAXON[T]}}' "${LINEAGE}" | sort -k2,2nr)
  log "      - Cluster strata names at this level"
  echo -e "${CLUSTER_STRATA}"
   # Check we have only one best strata
  if [[ $(echo "${CLUSTER_STRATA}" | wc -l) -eq 1 ]];
  then
    log "      - Single best taxon at this strata"
    BEST_STRATA="${STRATA}"
    BEST_STRATA_TAXA=$(echo "${CLUSTER_STRATA}" | cut -f1)
    BEST_STRATA_COUNT=$(echo "${CLUSTER_STRATA}" | cut -f2)
    BEST_STRATA_COLUMN="${STRATA_COLUMN_NUMBER}"
    log "      - BEST_STRATA=${BEST_STRATA}; BEST_STRATA_TAXA=${BEST_STRATA_TAXA}; BEST_STRATA_COUNT=${BEST_STRATA_COUNT}"
  else
    log "      - Multiple taxon at this strata (stoping here and using the last strata)"
    log "BEST_STRATA=${BEST_STRATA}"
    break
  fi
done



