#!/usr/bin/env Rscript
library(DESeq2)

## 
## Normalize columns in a matrix using DESeq2
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
normalized_counts <- counts(dds, normalized=TRUE)

print (paste("max SizeFactor:", max(sf)))
print (paste("min SizeFactor:", min(sf)))

## Add extra column to matrix with row names (otherwise the column with row names in it will not have a columns name [problem with the write.table() function])
to.write <- data.frame("Name"=rownames(normalized_counts),normalized_counts)
#colnames(to.write) <- colnames(data.tmp)

## Write
write.table(to.write, file=paste(matrix.file,".normalized_counts.txt", sep=''), sep="\t", quote = FALSE, row.names=FALSE, col.names = TRUE)

