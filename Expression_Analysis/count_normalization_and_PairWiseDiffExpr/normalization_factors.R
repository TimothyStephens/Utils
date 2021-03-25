#!/usr/bin/env Rscript
library(DESeq2)

## 
## Get normalization factors for each sample using DESeq2
## 

args = commandArgs(trailingOnly=TRUE)
# test if there is at least one argument: if not, return an error
if (length(args)!=1) {
  stop("One argument must be supplied (matrix file).n", call.=FALSE)
}

## Load matrix
matrix.file <- args[1]
# matrix.file <- "salmon_combined_HighLowLight.isoform.numreads.matrix"
data.tmp <- read.table(matrix.file, header = T, check.names = FALSE)
data <- as.matrix(data.tmp[,-1])
rownames(data) <- data.tmp[,1]
data <- round(data)
mode(data) <- "integer"

## Create DESeq2Dataset object and use DESeq2's inbuilt "median of ratios" methods for normalization
## See: https://hbctraining.github.io/DGE_workshop/lessons/02_DGE_count_normalization.html
dds <- DESeqDataSetFromMatrix(countData = data, colData = as.data.frame(colnames(data)), design = ~ 1)
dds <- estimateSizeFactors(dds)
sf <- sizeFactors(dds)

## Write Size Factors
write.table(sf, file=paste(matrix.file,".normalization_factors.txt", sep=''), sep="\t", quote = FALSE, row.names=TRUE, col.names = FALSE)

