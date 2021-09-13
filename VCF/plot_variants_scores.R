#!/usr/bin/env Rscript

DESCRIPTION="
##
## 
##

# Example:
Rscript plot_variants_scores.R plot_file SNP_table INDEL_table SNP_QD_min SNP_MQ_min SNP_FS_max SNP_SOR_max INDEL_QD_min INDEL_MQ_min INDEL_FS_max INDEL_SOR_max

# plot_prefix (prefix to use for output plots)

# SNP_table (can be gzipped; tab sep):
CHROM  	POS    	QUAL   	QD     	DP     	MQ     	FS     	SOR    	MQRankSum      	ReadPosRankSum
Seq1   	97     	83.26  	25.36  	2      	60.00  	0.000  	0.693  	NA     	NA
Seq1   	150    	39.77  	19.88  	6      	60.00  	0.000  	0.693  	NA     	NA
Seq1   	410    	40.29  	20.15  	5      	60.00  	0.000  	0.693  	NA     	NA
..
..

# INDEL_table (can be gzipped; tab sep):
CHROM  	POS    	QUAL   	QD     	DP     	MQ     	FS     	SOR    	MQRankSum      	ReadPosRankSum
Seq1   	98     	83.18  	28.73  	2      	60.00  	0.000  	0.693  	NA     	NA
Seq1   	1807   	83.18  	27.51  	2      	60.00  	0.000  	0.693  	NA     	NA
Seq1   	2308   	677.91 	9.68   	103    	60.00  	0.000  	0.693  	0.00   	2.85
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

## NOTE:
Warning messages:
1: Removed X rows containing non-finite values (stat_density). 
#    - These warnings are from the MQRankSum and ReadPosRankSum plots because they contain NA values for many of the SNPs/INDELs.
"
library('gridExtra')
library('ggplot2')

args = commandArgs(trailingOnly=TRUE)
# Test if there is 11 arguments: if not, return an error
if (length(args)!=11) {
  cat(DESCRIPTION)
  stop("11 arguments must be supplied (plot_prefix, SNP_table, INDEL_table, SNP_QD_min, SNP_MQ_min, SNP_FS_max, SNP_SOR_max, INDEL_QD_min, INDEL_MQ_min, INDEL_FS_max, INDEL_SOR_max)", call.=FALSE)
}
#args <- c("GVCFall.variants_scores", "GVCFall_SNPs.table", "GVCFall_INDELs.table", 
#          16, 50, 5, 2.5, 
#          16, 45, 5, 2.5)

## Load command line parameters
plot.prefix <- args[1]
VCFsnps.file <- args[2]
VCFindel.file <- args[3]

SNP.QD.min <- as.double(args[4])
SNP.MQ.min <- as.double(args[5])
SNP.FS.max <- as.double(args[6])
SNP.SOR.max <- as.double(args[7])

INDEL.QD.min <- as.double(args[8])
INDEL.MQ.min <- as.double(args[9])
INDEL.FS.max <- as.double(args[10])
INDEL.SOR.max <- as.double(args[11])

## Plot axis limits
QUAL.xmin <- 0
QUAL.xmax <- 1000
DP.xmin <- 0
DP.xmax <- 1000
FS.xmin <- 0
FS.xmax <- 20
FS.ymin <- 0
FS.ymax <- 1.0
SOR.xmin <- 0
SOR.xmax <- 10
SOR.ymin <- 0
SOR.ymax <- 10

###############
## Main code ##
###############

VCFsnps <- read.csv(VCFsnps.file, header = T, na.strings=c("","NA"), sep = "\t") 
VCFindel <- read.csv(VCFindel.file, header = T, na.strings=c("","NA"), sep = "\t")
print("SNPs dimensions:")
print(dim(VCFsnps))
print("INDELs dimensions:")
print(dim(VCFindel))
VCF <- rbind(VCFsnps, VCFindel)
VCF$Variant <- factor(c(rep("SNPs", dim(VCFsnps)[1]), rep("Indels", dim(VCFindel)[1])))

snps <- '#A9E2E4'
indels <- '#F4CCCA'

# NO plot axis limits
QUAL <- ggplot(VCF, aes(x=QUAL, fill=Variant)) + geom_density(alpha=.3)

QD <- ggplot(VCF, aes(x=QD, fill=Variant)) + geom_density(alpha=.3) +
  geom_vline(xintercept=c(SNP.QD.min, INDEL.QD.min), size=0.5, colour = c(snps,indels))

DP <- ggplot(VCF, aes(x=DP, fill=Variant)) + geom_density(alpha=0.3)

MQ <- ggplot(VCF, aes(x=MQ, fill=Variant)) + geom_density(alpha=.3) +
  geom_vline(xintercept=c(SNP.MQ.min, INDEL.MQ.min), size=0.5, colour = c(snps,indels)) +
  xlim(0, 100)

FS <- ggplot(VCF, aes(x=FS, fill=Variant)) + geom_density(alpha=.3) +
  geom_vline(xintercept=c(SNP.FS.max, INDEL.FS.max), size=0.5, colour = c(snps,indels))

SOR <- ggplot(VCF, aes(x=SOR, fill=Variant)) + geom_density(alpha=.3) +
  geom_vline(xintercept=c(SNP.SOR.max, INDEL.SOR.max), size=0.5, colour = c(snps,indels))

MQRankSum <- ggplot(VCF, aes(x=MQRankSum, fill=Variant)) + geom_density(alpha=.3)

ReadPosRankSum <- ggplot(VCF, aes(x=ReadPosRankSum, fill=Variant)) + geom_density(alpha=.3) +
  xlim(-20, 20)

# Save
p <- grid.arrange(QUAL, QD, DP, MQ, FS, SOR, MQRankSum, ReadPosRankSum, nrow=4)
ggsave(paste(plot.prefix, ".pdf", sep=''), p, height=20, width=15)



# WITH plot axis limits
QUAL <- ggplot(VCF, aes(x=QUAL, fill=Variant)) + geom_density(alpha=.3) +
  xlim(QUAL.xmin, QUAL.xmax)

QD <- ggplot(VCF, aes(x=QD, fill=Variant)) + geom_density(alpha=.3) +
  geom_vline(xintercept=c(SNP.QD.min, INDEL.QD.min), size=0.5, colour = c(snps,indels))

DP <- ggplot(VCF, aes(x=DP, fill=Variant)) + geom_density(alpha=0.3) +
  xlim(DP.xmin, DP.xmax)

MQ <- ggplot(VCF, aes(x=MQ, fill=Variant)) + geom_density(alpha=.3) +
  geom_vline(xintercept=c(SNP.MQ.min, INDEL.MQ.min), size=0.5, colour = c(snps,indels)) +
  xlim(40, 80)

FS <- ggplot(VCF, aes(x=FS, fill=Variant)) + geom_density(alpha=.3) +
  geom_vline(xintercept=c(SNP.FS.max, INDEL.FS.max), size=0.5, colour = c(snps,indels)) +
  xlim(FS.xmin, FS.xmax) +
  ylim(FS.ymin, FS.ymax)

SOR <- ggplot(VCF, aes(x=SOR, fill=Variant)) + geom_density(alpha=.3) +
  geom_vline(xintercept=c(SNP.SOR.max, INDEL.SOR.max), size=0.5, colour = c(snps,indels)) +
  xlim(SOR.xmin, SOR.xmax) +
  ylim(SOR.ymin, SOR.ymax)

MQRankSum <- ggplot(VCF, aes(x=MQRankSum, fill=Variant)) + geom_density(alpha=.3)

ReadPosRankSum <- ggplot(VCF, aes(x=ReadPosRankSum, fill=Variant)) + geom_density(alpha=.3) +
  xlim(-20, 20)

# Save
p <- grid.arrange(QUAL, QD, DP, MQ, FS, SOR, MQRankSum, ReadPosRankSum, nrow=4)
ggsave(paste(plot.prefix, ".axisLimits.pdf", sep=''), p, height=20, width=15)

