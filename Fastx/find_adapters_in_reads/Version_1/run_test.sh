

## R1: TruSeq_Adapter_Index_4
## R2: RC_TruSeq_Universal_Adapter_Short
source check_reads.sh
check_reads test_R1.fastq
check_reads test_R1.fastq.gz
check_reads test_R2.fastq
check_reads test_R2.fastq.gz

check_reads_short test_R1.fastq
check_reads_short test_R1.fastq.gz
check_reads_short test_R2.fastq
check_reads_short test_R2.fastq.gz 


