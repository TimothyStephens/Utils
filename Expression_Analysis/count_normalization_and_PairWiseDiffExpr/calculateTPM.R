#!/usr/bin/env Rscript

DESCRIPTION="
## 
## TPM normalize columns in a matrix (needs seq lengths for TPM)
## 

# Example:
Rscript calculateTPM.R in.matrix out.TPM.matrix

# in.matrix (can be gzipped):
Name   TP0   TP1   TP3   Length
g1     15    30    45    10
g2     10    20    5     20
..
..

# out.TPM.matrix (can be gzipped):
Name   TP0   TP1   TP3
g1     0.15  0.3   0.45
g2     0.1   0.2   0.05
..
..

"

args = commandArgs(trailingOnly=TRUE)
# Test if there is two arguments: if not, return an error
if (length(args)!=2) {
	cat(DESCRIPTION)
	stop("Two arguments must be supplied (in_matrix, out_TPM_matrix)", call.=FALSE)
}

## Load matrix
matrix.file <- args[1]
TPM.matrix.file <- args[2]
data.tmp <- read.table(matrix.file, header = T, check.names = FALSE)
data <- as.matrix(data.tmp[,-1])
rownames(data) <- data.tmp[,1]
#data <- round(data)
#mode(data) <- "integer"

if (! all("Length" %in% colnames(data))) {
	stop("in_matrix is missing a 'Length' column", call.=FALSE)
}

## Split Length and Count columns
data.length <- subset(data, select=c(Length))
data.counts <- subset(data, select=-c(Length))

## Code modified from: https://support.bioconductor.org/p/91218/
x <- data.counts / c(data.length)
data.tpm <- t( t(x) * 1e6 / colSums(x) )

## Add extra column to matrix with row names (otherwise the column with row names in it will not have a columns name [problem with the write.table() function])
to.write <- data.frame("Name"=rownames(data.tpm), data.tpm)

## Write
write.table(to.write, file=TPM.matrix.file, sep="\t", quote = FALSE, row.names=FALSE, col.names = TRUE)

