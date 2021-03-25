library(genefilter)
library(edgeR)


## 
## Modified from: https://seqqc.wordpress.com/2020/02/17/removing-low-count-genes-for-rna-seq-downstream-analysis/
## 
## 
## Removes sequecnes that do NOT have >= min.count in >= min.samples. 
## Converts the count parsed by the user into a CPM like value 
## [ cutoff=(min.count/median_LibSize)*1e6 ] and uses that for filtering. 
##


## Load command line args
args = commandArgs(trailingOnly=TRUE)
# test if there 4 arguments: if not, return an error
if (length(args)!=4) {
  stop("R script requires 4 files: count_table filtered_count_table min_count min_samples.n", call.=FALSE)
}

# args <- c("test_10x10.matrix", "test_10x10.matrix.filtered", 5, 2)
count.table.file <- args[1]
count.table.file.out <- args[2]
min.count <- as.integer(args[3])
min.samples <- as.integer(args[4])

## Load matrix file
count.table = read.table(count.table.file, header=T, com='', row.names=1, check.names=F, sep='\t')
count.table = as.matrix(count.table)

## Convert matrix to CPM
lib.size <- colSums(count.table)
MedianLibSize <- median(lib.size)
CPM.Cutoff <- (min.count / MedianLibSize) * 1e6
CPM <- edgeR::cpm(count.table, lib.size=lib.size)

## Returns a filter function with bindings for k and A. 
## Function returns TRUE if at least k of the arguments elements are larger than A.
f1 <- genefilter::kOverA(min.samples, CPM.Cutoff)
flist <- genefilter::filterfun(f1)
keep <- genefilter::genefilter(CPM, flist)
myFilt <- count.table[keep,]
# dim(myFilt)

## Add extra row to matrix with column names (otherwise the column with row names in it will not have a columns name [problem with the write.table() function])
to.write <- data.frame("Name"=rownames(myFilt),myFilt)
## Write
write.table(to.write, file=count.table.file.out, sep="\t", quote = FALSE, row.names=FALSE, col.names = TRUE)

