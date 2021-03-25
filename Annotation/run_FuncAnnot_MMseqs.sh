#!/usr/bin/env bash

# Print all info to log file
exec 1> "${0}.log.$(date +%s)" 2>&1

#### Pre-run setup
source ~/scripts/script_setup.sh
set +eu; conda activate py27; set -eu

#### Parameters 
FASTA="" # Protein fasta file to annotate

NPARTS=100       # Number of part to split fasta file into for UniProt search
NPARALLEL=8      # Number of parallel mmseq2 jobs to run at once
NCPUS=10         # Number of cpus to use per mmseq2 job
SENSITIVITY=7.5  # mmseq2 sensitivity (1.0 faster; 4.0 fast; 7.5 sensitive) 

UTILS=""         # Location of the other scripts this file was packaged with

MMSEQS_BIN=""    # mmseq2 bin dir (any version)
HMMER_BIN=""     # HMMER v3.1.b2 bin dir
PFAM_SCAN=""     # pfam_scan intsall dir
KOFAMSCAN=""     # kofamscan 'exec_annotation' script path

SWISSPROT_DB=""  # SwissProt mmseq2 DB files path
TREMBL_DB=""     # TrEMBL mmseq2 DB files path
PFAM_A=""        # PFAM_A data base loaction
GOA_DB="" # GOA sqlite data file (made using Load_GOterms_into_SQLite.py)


####
#### Start annotation
####
PREFIX="$FASTA.FunctionalAnnotation"

#### Split fasta
SPLIT_DIR="$PREFIX.split_fasta"
FILES2RUN="$SPLIT_DIR.files2run.txt"
echo ""
if [ ! -f "$SPLIT_DIR/split_done" ];
then
	log "[Split_fasta] Splitting $FASTA into $NPARTS parts."
	run_cmd "rm -fr $FILES2RUN $SPLIT_DIR"
	
	run_cmd "$UTILS/fasta-splitter.pl --n-parts $NPARTS --out-dir $SPLIT_DIR $FASTA"
	run_cmd "ls -1 --color=none $SPLIT_DIR/* > $FILES2RUN"
	touch "$SPLIT_DIR/split_done"
	
	log "[Split_fasta] Splitting Done!"
else
        log "[Split_fasta] $SPLIT_DIR/split_done already exists!"
	log "[Split_fasta] $FASTA has already been split. Skipping this step!"
fi
echo ""


#### Search UniProt
echo ""
if [ ! -f "$SPLIT_DIR/parallel_done" ];
then
	log "[UniProt_search] Running UniProt search on split fasta file (running $NPARALLEL jobs with $NCPUS cpus each)."
	
	SEARCH="$UTILS/protein_functional_annotation_mmseqs.sh"
	SEARCH="$SEARCH --ncpus $NCPUS"
	SEARCH="$SEARCH --sensitivity $SENSITIVITY"
	SEARCH="$SEARCH --mmseqs $MMSEQS_BIN"
	SEARCH="$SEARCH --hmmer $HMMER_BIN"
	SEARCH="$SEARCH --pfamscan $PFAM_SCAN"
	SEARCH="$SEARCH --swisprot $SWISSPROT_DB"
	SEARCH="$SEARCH --trembl $TREMBL_DB"
	SEARCH="$SEARCH --pfam $PFAM_A"

	parallel -j $NPARALLEL "$SEARCH --fasta {} >> {}.log" :::: $FILES2RUN
	EXITSTATUS=$?
	log "[UniProt_search] Parallel exit status: $EXITSTATUS"

	if [ $EXITSTATUS -gt 0 ]
	then
		log "[UniProt_search] One or more parallel jobs failed. Check log files for possible errors!"
		exit $EXITSTATUS
	else
		touch "$SPLIT_DIR/parallel_done"
		log "[UniProt_search] UniProt search finished without any obvious errors!"
	fi
else
        log "[UniProt_search] $SPLIT_DIR/parallel_done already exists!"
        log "[UniProt_search] UniProt search has already been completed. Skipping this step!"
fi
echo ""


## Combined UniProt search output
UNIPROT="$PREFIX.mmseqs"
echo ""
if [ ! -f "${UNIPROT}_UniProt.sorted.outfmt6.top1.desc_annot" ];
then
	log "[Combine_UniProt] Combining UniProt search results."
	run_cmd "rm -fr ${UNIPROT}*"
	
	run_cmd "while read FILE; do cat \$FILE.mmseqs_swissprot.outfmt6; done < $FILES2RUN | awk -F'\t' '\$11<1e-5' | gzip -c > ${UNIPROT}_swissprot.outfmt6.gz"
	run_cmd "while read FILE; do cat \$FILE.mmseqs_trembl.outfmt6; done < $FILES2RUN    | awk -F'\t' '\$11<1e-5' | gzip -c > ${UNIPROT}_trembl.outfmt6.gz"
	
	run_cmd "zcat ${UNIPROT}_swissprot.outfmt6.gz | $UTILS/blast_top_hits.py -s 20 -n 1 -o ${UNIPROT}_swissprot.outfmt6.top20"
	run_cmd "zcat ${UNIPROT}_trembl.outfmt6.gz    | $UTILS/blast_top_hits.py -s 20 -n 1 -o ${UNIPROT}_trembl.outfmt6.top20"
	run_cmd "cat  ${UNIPROT}_swissprot.outfmt6.top20 ${UNIPROT}_trembl.outfmt6.top20 > ${UNIPROT}_UniProt.outfmt6.top20_combined"
	
	run_cmd "zcat ${UNIPROT}_swissprot.outfmt6.gz ${UNIPROT}_trembl.outfmt6.gz | sort -k1,1 -k12,12nr | gzip -c > ${UNIPROT}_UniProt.sorted.outfmt6.gz"
	
	# UniProt TopHit description annots
	run_cmd "zcat ${UNIPROT}_UniProt.sorted.outfmt6.gz | $UTILS/blast_top_hits.py -s 1 -n 1 -o ${UNIPROT}_UniProt.sorted.outfmt6.top1"
	run_cmd "awk -F'\t' '{print \$1\"\t\"\$15}' ${UNIPROT}_UniProt.sorted.outfmt6.top1 > ${UNIPROT}_UniProt.sorted.outfmt6.top1.desc_annot.tmp"
	run_cmd "mv ${UNIPROT}_UniProt.sorted.outfmt6.top1.desc_annot.tmp ${UNIPROT}_UniProt.sorted.outfmt6.top1.desc_annot"

	log "[Combine_UniProt] Finished combining UniProt results without any obvious errors!"
else
	log "[Combine_UniProt] ${UNIPROT}_UniProt.sorted.outfmt6.top1.desc_annot already exists!"
        log "[Combine_UniProt] UniProt results have already been combined. Skipping this step!"
fi
echo ""


## Combine Pfam_scan output
PFAM="$PREFIX.pfam_scan"
echo ""
if [ ! -f "$PFAM.annotations.2col" ];
then
	log "[Combine_Pfamscan] Combining pfam_scan search results."
	run_cmd "rm -fr ${PFAM}*"

	## <seq id> <alignment start> <alignment end> <envelope start> <envelope end> <hmm acc> <hmm name> <type> <hmm start> <hmm end> <hmm length> <bit score> <E-value> <significance> <clan>
	run_cmd "while read FILE; do cat \$FILE.pfam_scan.out; done < $FILES2RUN | awk '\$1!~\"^#\" && \$1!~\"^$\"' | gzip -c > $PFAM.out.gz"
	# Filter by e-value <0.001
	run_cmd "zcat $PFAM.out.gz | python $UTILS/pfam_to_2col_annotation.py -o $PFAM.annotations.2col.tmp"
	run_cmd "mv $PFAM.annotations.2col.tmp $PFAM.annotations.2col"
	
	log "[Combine_Pfamscan] Finished combining pfam_scan results without any obvious errors!"
else
        log "[Combine_Pfamscan] $PFAM.annotations.2col already exists!"
        log "[Combine_Pfamscan] Pfam_scan results have already been combined. Skipping this step!"
fi
echo ""


## kofamscan
KOFAM="$PREFIX.kofamscan"
echo ""
if [ ! -f "${KOFAM}_results.mapper.txt.filtered.2col" ];
then
	log "[kofamscan] Running kofamscan."
	run_cmd "rm -fr ${KOFAM}_tmpdir ${KOFAM}*"

	set +eu; conda activate kofamscan; set -eu
	run_cmd "$KOFAMSCAN --tmp-dir ${KOFAM}_tmpdir --cpu $((NPARALLEL*NCPUS)) -f detail -o ${KOFAM}_results.detail.txt $FASTA"
	run_cmd "$KOFAMSCAN --tmp-dir ${KOFAM}_tmpdir --cpu $((NPARALLEL*NCPUS)) -f mapper -o ${KOFAM}_results.mapper.txt --reannotate $FASTA"
	set +eu; conda deactivate ; set -eu
	
	run_cmd "tar -cf ${KOFAM}_tmpdir.tar ${KOFAM}_tmpdir && rm -r ${KOFAM}_tmpdir"

	run_cmd "awk -F'\t' '\$2!=\"\"' ${KOFAM}_results.mapper.txt > ${KOFAM}_results.mapper.txt.filtered"
	run_cmd "$UTILS/kofam_to_2col_annotation.py -i ${KOFAM}_results.mapper.txt.filtered -o ${KOFAM}_results.mapper.txt.filtered.2col.tmp"
	run_cmd "mv ${KOFAM}_results.mapper.txt.filtered.2col.tmp ${KOFAM}_results.mapper.txt.filtered.2col"

	log "[kofamscan] Finished kofamscan without any obvious errors!"
else
	log "[kofamscan] ${KOFAM}_results.mapper.txt.filtered.2col already exists!"
	log "[kofamscan] kofamscan has already been run. Skipping this step!"
fi
echo ""


## GOterms
BLAST="${UNIPROT}_UniProt.outfmt6.top20_combined"
GOTERMS="$BLAST.GOtermsAnnot"
echo ""
if [ ! -f "$GOTERMS.reformated" ];
then
	log "[Annotate_GOterms] Annotating GO terms."
	run_cmd "rm -fr ${GOTERMS}*"

	run_cmd "$UTILS/Annotate_GO_From_BLAST_topGO_noLoadBlast.py --mmseq2 --blast $BLAST --out $GOTERMS --db $GOA_DB"
	run_cmd "cat $GOTERMS | sed -e 's/, /,/g' > $GOTERMS.reformated.tmp"
	run_cmd "mv $GOTERMS.reformated.tmp $GOTERMS.reformated"

	log "[Annotate_GOterms] Finished annotating GO terms without any obvious errors!"
else
	log "[Annotate_GOterms] $GOTERMS.reformated already exists!"
	log "[Annotate_GOterms] GO term annotation has already been run. Skipping this step!"
fi
echo ""


## Make big annotation table
TABLE="$PREFIX.annotation_table.txt"
echo ""
if [ ! -f $TABLE ];
then
	log "[Make_BigTable] Making big annotation table."
	run_cmd "rm -fr ${TABLE}*"

	run_cmd "awk '\$1~\"^>\" {print \$1}' $FASTA | sed -e 's/>//' | awk -F'\t' 'BEGIN{print \"#Seq_ID\tGO_terms\tPFAM_Domains\tKEGG_IDs\tUniProt_TopHit\"} {print}' | \
	 $UTILS/add_value_to_table.py --keep_comments -c 1 -d NA -a $GOTERMS.reformated | \
	 $UTILS/add_value_to_table.py --keep_comments -c 1 -d NA -a $PFAM.annotations.2col | \
	 $UTILS/add_value_to_table.py --keep_comments -c 1 -d NA -a ${KOFAM}_results.mapper.txt.filtered.2col | \
	 $UTILS/add_value_to_table.py --keep_comments -c 1 -d NA -a ${UNIPROT}_UniProt.sorted.outfmt6.top1.desc_annot -o $TABLE.tmp"
	run_cmd "mv $TABLE.tmp $TABLE"
	
	log "[Make_BigTable] Finished making big annotation table without any obvious errors!"
else
	log "[Make_BigTable] $PREFIX.annotation_table.txt already exists!"
	log "[Make_BigTable] Big annotation table has already been created. Skipping this step!"
fi
echo ""


echo; log "Annotation Done!!!"; echo
