#!/bin/sh

## 
## Checks the top 1M lines of a compressed/uncompressed read file for the presence of adapters (both full and short versions)
## 

## Run with fill adapter seqs 
check_reads (){
	process_fastq_file $1 "${ADAPTERS[@]}"
}


## Run with short adapter seqs (+10/-10 from the index)
check_reads_short (){
        process_fastq_file $1 "${ADAPTERS_SHORT[@]}"
}



## Process read file.
process_fastq_file (){
	local FASTQ_FILE="$1" 		# Save first argument in a variable
	shift 				# Shift all arguments to the left (original $1 gets lost)
	local ADAPTERS_2_USE=("$@") 	# Rebuild the array with rest of arguments
	
        # If file compressed use zcat.
	CAT=cat
        if [[ "${FASTQ_FILE##*.}" = "gz" ]]; then
                CAT=zcat
        fi
	
        # Check file for adapters
        for ((n=0; n<((${#ADAPTERS_2_USE[@]}-1)); n+=2));
        do
                echo -e "${ADAPTERS_2_USE[$n]}:\t" `$CAT $FASTQ_FILE | head -n 1000000 | grep ${ADAPTERS_2_USE[$n+1]} | wc -l`
        done
}


## Adapters to check for
ADAPTERS=(
	"TruSeq_Universal_Adapter" "AATGATACGGCGACCACCGAGATCTACACTCTTTCCCTACACGACGCTCTTCCGATCT"
	"RC_TruSeq_Universal_Adapter" "AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGTAGATCTCGGTGGTCGCCGTATCATT"
	"TruSeq_Adapter_Index_1" "GATCGGAAGAGCACACGTCTGAACTCCAGTCACATCACGATCTCGTATGCCGTCTTCTGCTTG"
	"TruSeq_Adapter_Index_2" "GATCGGAAGAGCACACGTCTGAACTCCAGTCACCGATGTATCTCGTATGCCGTCTTCTGCTTG"
	"TruSeq_Adapter_Index_3" "GATCGGAAGAGCACACGTCTGAACTCCAGTCACTTAGGCATCTCGTATGCCGTCTTCTGCTTG"
	"TruSeq_Adapter_Index_4" "GATCGGAAGAGCACACGTCTGAACTCCAGTCACTGACCAATCTCGTATGCCGTCTTCTGCTTG"
	"TruSeq_Adapter_Index_5" "GATCGGAAGAGCACACGTCTGAACTCCAGTCACACAGTGATCTCGTATGCCGTCTTCTGCTTG"
	"TruSeq_Adapter_Index_6" "GATCGGAAGAGCACACGTCTGAACTCCAGTCACGCCAATATCTCGTATGCCGTCTTCTGCTTG"
	"TruSeq_Adapter_Index_7" "GATCGGAAGAGCACACGTCTGAACTCCAGTCACCAGATCATCTCGTATGCCGTCTTCTGCTTG"
	"TruSeq_Adapter_Index_8" "GATCGGAAGAGCACACGTCTGAACTCCAGTCACACTTGAATCTCGTATGCCGTCTTCTGCTTG"
	"TruSeq_Adapter_Index_9" "GATCGGAAGAGCACACGTCTGAACTCCAGTCACGATCAGATCTCGTATGCCGTCTTCTGCTTG"
	"TruSeq_Adapter_Index_10" "GATCGGAAGAGCACACGTCTGAACTCCAGTCACTAGCTTATCTCGTATGCCGTCTTCTGCTTG"
	"TruSeq_Adapter_Index_11" "GATCGGAAGAGCACACGTCTGAACTCCAGTCACGGCTACATCTCGTATGCCGTCTTCTGCTTG"
	"TruSeq_Adapter_Index_12" "GATCGGAAGAGCACACGTCTGAACTCCAGTCACCTTGTAATCTCGTATGCCGTCTTCTGCTTG"
	"TruSeq_Adapter_Index_13" "GATCGGAAGAGCACACGTCTGAACTCCAGTCACAGTCAACAATCTCGTATGCCGTCTTCTGCTTG"
	"TruSeq_Adapter_Index_14" "GATCGGAAGAGCACACGTCTGAACTCCAGTCACAGTTCCGTATCTCGTATGCCGTCTTCTGCTTG"
	"TruSeq_Adapter_Index_15" "GATCGGAAGAGCACACGTCTGAACTCCAGTCACATGTCAGAATCTCGTATGCCGTCTTCTGCTTG"
	"TruSeq_Adapter_Index_16" "GATCGGAAGAGCACACGTCTGAACTCCAGTCACCCGTCCCGATCTCGTATGCCGTCTTCTGCTTG"
	"TruSeq_Adapter_Index_18" "GATCGGAAGAGCACACGTCTGAACTCCAGTCACGTCCGCACATCTCGTATGCCGTCTTCTGCTTG"
	"TruSeq_Adapter_Index_19" "GATCGGAAGAGCACACGTCTGAACTCCAGTCACGTGAAACGATCTCGTATGCCGTCTTCTGCTTG"
	"TruSeq_Adapter_Index_20" "GATCGGAAGAGCACACGTCTGAACTCCAGTCACGTGGCCTTATCTCGTATGCCGTCTTCTGCTTG"
	"TruSeq_Adapter_Index_21" "GATCGGAAGAGCACACGTCTGAACTCCAGTCACGTTTCGGAATCTCGTATGCCGTCTTCTGCTTG"
	"TruSeq_Adapter_Index_22" "GATCGGAAGAGCACACGTCTGAACTCCAGTCACCGTACGTAATCTCGTATGCCGTCTTCTGCTTG"
	"TruSeq_Adapter_Index_23" "GATCGGAAGAGCACACGTCTGAACTCCAGTCACGAGTGGATATCTCGTATGCCGTCTTCTGCTTG"
	"TruSeq_Adapter_Index_25" "GATCGGAAGAGCACACGTCTGAACTCCAGTCACACTGATATATCTCGTATGCCGTCTTCTGCTTG"
	"TruSeq_Adapter_Index_27" "GATCGGAAGAGCACACGTCTGAACTCCAGTCACATTCCTTTATCTCGTATGCCGTCTTCTGCTTG"
	"I287_CJ_GAGTACG" "GATCGGAAGAGCACACGTCTGAACTCCAGTCACGAGTACGATCTCGTATGCCGTCTTCTGCTTG"
	"I288_CJ_TGCCCAT" "GATCGGAAGAGCACACGTCTGAACTCCAGTCACTGCCCATATCTCGTATGCCGTCTTCTGCTTG"
	"I289_CJ_TGTGCCA" "GATCGGAAGAGCACACGTCTGAACTCCAGTCACTGTGCCAATCTCGTATGCCGTCTTCTGCTTG"
	"I290_CJ_CATTTAG" "GATCGGAAGAGCACACGTCTGAACTCCAGTCACCATTTAGATCTCGTATGCCGTCTTCTGCTTG"
	"I291_CJ_AGGACCT" "GATCGGAAGAGCACACGTCTGAACTCCAGTCACAGGACCTATCTCGTATGCCGTCTTCTGCTTG"
	"I292_CJ_CCAGGCA" "GATCGGAAGAGCACACGTCTGAACTCCAGTCACCCAGGCAATCTCGTATGCCGTCTTCTGCTTG"
	"I293_CJ_TTCGCTG" "GATCGGAAGAGCACACGTCTGAACTCCAGTCACTTCGCTGATCTCGTATGCCGTCTTCTGCTTG"
	"I294_CJ_AGACTGA" "GATCGGAAGAGCACACGTCTGAACTCCAGTCACAGACTGAATCTCGTATGCCGTCTTCTGCTTG"
	"I295_CJ_ACAGATA" "GATCGGAAGAGCACACGTCTGAACTCCAGTCACACAGATAATCTCGTATGCCGTCTTCTGCTTG"
	"I296_CJ_AAACCTT" "GATCGGAAGAGCACACGTCTGAACTCCAGTCACAAACCTTATCTCGTATGCCGTCTTCTGCTTG"
	"I297_CJ_AACGGAG" "GATCGGAAGAGCACACGTCTGAACTCCAGTCACAACGGAGATCTCGTATGCCGTCTTCTGCTTG"
	"I298_CJ_TCCGGGA" "GATCGGAAGAGCACACGTCTGAACTCCAGTCACTCCGGGAATCTCGTATGCCGTCTTCTGCTTG"
)


## Adapters to check for
ADAPTERS_SHORT=(
        "TruSeq_Universal_Adapter_Short" "CCGAGATCTACACTCTTTCCCTACAC"
        "RC_TruSeq_Universal_Adapter_Short" "GTGTAGGGAAAGAGTGTAGATCTCGG"
        "TruSeq_Adapter_Index_1_Short" "CTCCAGTCACATCACGATCTCGTATG"
        "TruSeq_Adapter_Index_2_Short" "CTCCAGTCACCGATGTATCTCGTATG"
        "TruSeq_Adapter_Index_3_Short" "CTCCAGTCACTTAGGCATCTCGTATG"
        "TruSeq_Adapter_Index_4_Short" "CTCCAGTCACTGACCAATCTCGTATG"
        "TruSeq_Adapter_Index_5_Short" "CTCCAGTCACACAGTGATCTCGTATG"
        "TruSeq_Adapter_Index_6_Short" "CTCCAGTCACGCCAATATCTCGTATG"
        "TruSeq_Adapter_Index_7_Short" "CTCCAGTCACCAGATCATCTCGTATG"
        "TruSeq_Adapter_Index_8_Short" "CTCCAGTCACACTTGAATCTCGTATG"
        "TruSeq_Adapter_Index_9_Short" "CTCCAGTCACGATCAGATCTCGTATG"
        "TruSeq_Adapter_Index_10_Short" "CTCCAGTCACTAGCTTATCTCGTATG"
        "TruSeq_Adapter_Index_11_Short" "CTCCAGTCACGGCTACATCTCGTATG"
        "TruSeq_Adapter_Index_12_Short" "CTCCAGTCACCTTGTAATCTCGTATG"
        "TruSeq_Adapter_Index_13_Short" "CTCCAGTCACAGTCAACAATCTCGTATG"
        "TruSeq_Adapter_Index_14_Short" "CTCCAGTCACAGTTCCGTATCTCGTATG"
        "TruSeq_Adapter_Index_15_Short" "CTCCAGTCACATGTCAGAATCTCGTATG"
        "TruSeq_Adapter_Index_16_Short" "CTCCAGTCACCCGTCCCGATCTCGTATG"
        "TruSeq_Adapter_Index_18_Short" "CTCCAGTCACGTCCGCACATCTCGTATG"
        "TruSeq_Adapter_Index_19_Short" "CTCCAGTCACGTGAAACGATCTCGTATG"
        "TruSeq_Adapter_Index_20_Short" "CTCCAGTCACGTGGCCTTATCTCGTATG"
        "TruSeq_Adapter_Index_21_Short" "CTCCAGTCACGTTTCGGAATCTCGTATG"
        "TruSeq_Adapter_Index_22_Short" "CTCCAGTCACCGTACGTAATCTCGTATG"
        "TruSeq_Adapter_Index_23_Short" "CTCCAGTCACGAGTGGATATCTCGTATG"
        "TruSeq_Adapter_Index_25_Short" "CTCCAGTCACACTGATATATCTCGTATG"
        "TruSeq_Adapter_Index_27_Short" "CTCCAGTCACATTCCTTTATCTCGTATG"
        "I287_CJ_GAGTACG_Short" "CTCCAGTCACGAGTACGATCTCGTATG"
        "I288_CJ_TGCCCAT_Short" "CTCCAGTCACTGCCCATATCTCGTATG"
        "I289_CJ_TGTGCCA_Short" "CTCCAGTCACTGTGCCAATCTCGTATG"
        "I290_CJ_CATTTAG_Short" "CTCCAGTCACCATTTAGATCTCGTATG"
        "I291_CJ_AGGACCT_Short" "CTCCAGTCACAGGACCTATCTCGTATG"
        "I292_CJ_CCAGGCA_Short" "CTCCAGTCACCCAGGCAATCTCGTATG"
        "I293_CJ_TTCGCTG_Short" "CTCCAGTCACTTCGCTGATCTCGTATG"
        "I294_CJ_AGACTGA_Short" "CTCCAGTCACAGACTGAATCTCGTATG"
        "I295_CJ_ACAGATA_Short" "CTCCAGTCACACAGATAATCTCGTATG"
        "I296_CJ_AAACCTT_Short" "CTCCAGTCACAAACCTTATCTCGTATG"
        "I297_CJ_AACGGAG_Short" "CTCCAGTCACAACGGAGATCTCGTATG"
        "I298_CJ_TCCGGGA_Short" "CTCCAGTCACTCCGGGAATCTCGTATG"
)

