## 
## Sums the rows of a provided matrix. Assumes the matrix has row and column names. 
## 
options(scipen=999)


## Load command line args
args = commandArgs(trailingOnly=TRUE)
# test if there 2 arguments: if not, return an error
if (length(args)!=2) {
  stop("R script requires 2 files: matrix_infile rowSums_outfile.n", call.=FALSE)
}

# args <- c("test_10x10.matrix", "test_10x10.matrix.rowSums")
matrix.infile <- args[1]
rowSum.outfile <- args[2]

## Load matrix file
m.table = read.table(matrix.infile, header=T, com='', row.names=1, check.names=F, sep='\t')
m.table = as.matrix(m.table)

## Convert matrix to CPM
m.rowSums <- as.matrix(rowSums(m.table))
colnames(m.rowSums) <- "rowSums"

## Add extra row to matrix with column names (otherwise the column with row names in it will not have a columns name [problem with the write.table() function])
to.write <- data.frame("Name"=rownames(m.rowSums),m.rowSums)
## Write
write.table(to.write, file=rowSum.outfile, sep="\t", quote = FALSE, row.names=FALSE, col.names = TRUE)

