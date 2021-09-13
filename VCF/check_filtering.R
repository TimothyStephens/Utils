#!/usr/bin/env Rscript

DESCRIPTION="
##
##
##

# Example:
Rscript check_filtering.R SNP_table INDEL_table SNP_QD_min SNP_MQ_min SNP_FS_max SNP_SOR_max INDEL_QD_min INDEL_MQ_min INDEL_FS_max INDEL_SOR_max

# SNP_table (can be gzipped; tab sep):
CHROM   POS     QUAL    QD      DP      MQ      FS      SOR     MQRankSum       ReadPosRankSum
Seq1    97      83.26   25.36   2       60.00   0.000   0.693   NA      NA
Seq1    150     39.77   19.88   6       60.00   0.000   0.693   NA      NA
Seq1    410     40.29   20.15   5       60.00   0.000   0.693   NA      NA
..
..

# INDEL_table (can be gzipped; tab sep):
CHROM   POS     QUAL    QD      DP      MQ      FS      SOR     MQRankSum       ReadPosRankSum
Seq1    98      83.18   28.73   2       60.00   0.000   0.693   NA      NA
Seq1    1807    83.18   27.51   2       60.00   0.000   0.693   NA      NA
Seq1    2308    677.91  9.68    103     60.00   0.000   0.693   0.00    2.85
..
..
# SNP_QD_min (float)
# SNP_MQ_min (float)
# SNP_FS_max (float)
# SNP_SOR_max (float)
# INDEL_QD_min (float)
# INDEL_MQ_min (float)
# INDEL_FS_max (float)
# INDEL_SOR_max (float)

"

args = commandArgs(trailingOnly=TRUE)
# Test if there is 11 arguments: if not, return an error
if (length(args)!=10) {
  cat(DESCRIPTION)
  stop("10 arguments must be supplied (SNP_table, INDEL_table, SNP_QD_min, SNP_MQ_min, SNP_FS_max, SNP_SOR_max, INDEL_QD_min, INDEL_MQ_min, INDEL_FS_max, INDEL_SOR_max)", call.=FALSE)
}

## Load command line parameters
VCFsnps.file <- args[1]
VCFindel.file <- args[2]

SNP.QD.min <- as.double(args[3])
SNP.MQ.min <- as.double(args[4])
SNP.FS.max <- as.double(args[5])
SNP.SOR.max <- as.double(args[6])

INDEL.QD.min <- as.double(args[7])
INDEL.MQ.min <- as.double(args[8])
INDEL.FS.max <- as.double(args[9])
INDEL.SOR.max <- as.double(args[10])


# SNPs
VCFsnps <- read.csv(VCFsnps.file, header = T, na.strings=c("","NA"), sep = "\t") 
head(VCFsnps)
sum(na.omit(VCFsnps$QD) < SNP.QD.min)
sum(na.omit(VCFsnps$MQ) < SNP.MQ.min)
sum(na.omit(VCFsnps$FS) > SNP.FS.max)
sum(na.omit(VCFsnps$SOR) > SNP.SOR.max)
sum(na.omit(VCFsnps$ReadPosRankSum) < -10)
sum(na.omit(VCFsnps$ReadPosRankSum) > 10)

# Indels
VCFindel <- read.csv(VCFindel.file, header = T, na.strings=c("","NA"), sep = "\t")
head(VCFindel)
sum(na.omit(VCFindel$QD) < INDEL.QD.min)
sum(na.omit(VCFindel$MQ) < INDEL.MQ.min)
sum(na.omit(VCFindel$FS) > INDEL.FS.max)
sum(na.omit(VCFindel$SOR) > INDEL.SOR.max)
sum(na.omit(VCFindel$ReadPosRankSum) < -10)
sum(na.omit(VCFindel$ReadPosRankSum) > 10)

