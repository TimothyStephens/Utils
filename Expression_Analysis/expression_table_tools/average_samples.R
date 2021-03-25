
args = commandArgs(trailingOnly=TRUE)
# test if there is at least one argument: if not, return an error
if (length(args)!=2) {
  stop("Two arguments must be supplied (matrix and sample files).n", call.=FALSE)
}

matrix.file <- args[1]
sample.file <- args[2]
# matrix.file <- "test_data.matrix"
# sample.file <- "test_samples.txt"

## Load matrix file
data = read.table(matrix.file, header=T, com='', row.names=1, check.names=F, sep='\t')
data = as.matrix(data)
data <- round(data)
mode(data) <- "integer"

## Load samples file [sample \t replicate]
samples_data = read.table(sample.file, header=F, check.names=F, fill=T)
samples_data = samples_data[samples_data[,2] != '',]
colnames(samples_data) = c('sample_name', 'replicate_name')
sample_types = as.character(unique(samples_data[,1]))
rep_names = as.character(samples_data[,2])

## Check if all samples are in *.matrix file.
if (all(rep_names %in% colnames(data))) {
  if (length(rep_names) == length(colnames(data))) {
    print("All columns in *.matrix file are in samples.txt")
  } else {
    warning("WARNING: **NOT** all columns in *.matrix file are in samples.txt")
  }
} else {
  stop("ERROR: Not all samples in samples.txt are in the *.matrix file")
}

## Get just the columns specified in samples.txt
data = data[, colnames(data) %in% rep_names, drop=F ] # Get just data columns in samples file
nsamples = length(sample_types)


## Get list of sample<->replicate {S1:[S1R1, S1R2, S1R3], S2:[.....]}
sample_type_list = list()
for (i in 1:nsamples) {
  samples_want = samples_data[samples_data[,1]==sample_types[i], 2]
  sample_type_list[[sample_types[i]]] = as.vector(samples_want)
}

## Get list of sample order [S1, S1, S1, S2, S2, S2, S3, ....]
sample_factoring = colnames(data)
for (i in 1:nsamples) {
  sample_type = sample_types[i]
  replicates_want = sample_type_list[[sample_type]]
  sample_factoring[ colnames(data) %in% replicates_want ] = sample_type
}

## For each sample get the mean of all replicates.
data.sampleMean <- data.frame(row.names = rownames(data))
for (sample_we_want in sample_types) {
  # Get columns which match the sample we want to average
  d1 <- data[,sample_factoring %in% sample_we_want]
  data.sampleMean[[sample_we_want]] <- rowMeans(d1)
}

## Add extra row to matrix with column names (otherwise the column with row names in it will not have a columns name [problem with the write.table() function])
to.write <- data.frame("Name"=rownames(data.sampleMean),data.sampleMean)

## Write
write.table(to.write, file=paste(matrix.file,".sampleMean", sep=''), sep="\t", quote = FALSE, row.names=FALSE, col.names = TRUE)

