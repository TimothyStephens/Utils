library(DESeq2)
library(pheatmap)
library(RColorBrewer)
library(ggplot2)

args = commandArgs(trailingOnly=TRUE)
# test if there is at least one argument: if not, return an error
if (length(args)!=2) {
  stop("Two arguments must be supplied (matrix, samples.txt, substring for control replicates).n", call.=FALSE)
}

#matrix.file <- args[1]
#sample.file <- args[2]
#sample.control <- args[3]
matrix.file <- "salmon_combined_HighLowLight.isoform.numreads.matrix"
sample.file <- "samples.txt"
sample.control <- "CL"

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
data = data[, colnames(data) %in% rep_names, drop=F ] # Get just data columns in samples file
nsamples = length(sample_types)

if (length(rep_names) != length(colnames(data))) {
  stop("Columns selected from matrix file do not exactly match those given in samples.txt file")
}

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

## 
## DESeq2
## 

# Object describing conditions of each column - “control” (“c”) or “treatment” (“t”)
# Use matching of sample.control pattern to identify c/t columns.
conditions <- ifelse(grepl(sample.control, colnames(data)), "c", "t")
coldata <- data.frame(row.names=colnames(data), conditions)
print (coldata)

# "dds" object for DESeq2 - contains counts and condition information
dds <- DESeqDataSetFromMatrix(countData=data, colData=coldata, design=~conditions)

# Variance stabilizing transformation
vsd <- vst(dds, blind=FALSE)

##
## Heatmap of the sample-to-sample distances
## 
sampleDists <- dist(t(assay(vsd)))
sampleDistMatrix <- as.matrix(sampleDists)
rownames(sampleDistMatrix) <- colnames(vsd)
colnames(sampleDistMatrix) <- NULL
colors <- colorRampPalette( rev(brewer.pal(9, "Blues")) )(255)
pheatmap(sampleDistMatrix,
         clustering_distance_rows=sampleDists,
         clustering_distance_cols=sampleDists,
         col=colors,
         filename=paste(matrix.file,".heatmap.pdf",sep=''))

## 
## Principal component plot of the samples
## 
colors <- c("CL-0h"="#d73027", 
            "CL-0.5h"="#fc8d59", 
            "CL-6h"="#fee08b", 
            "CL-12h"="#ffffbf", 
            "CL-18h"="#d9ef8b", 
            "CL-30h"="#91cf60", 
            "CL-42h"="#1a9850", 
            "HL-0h"="#d73027", 
            "HL-0.5h"="#fc8d59", 
            "HL-6h"="#fee08b", 
            "HL-12h"="#ffffbf", 
            "HL-18h"="#d9ef8b", 
            "HL-30h"="#91cf60", 
            "HL-42h"="#1a9850"
)

pcaData <- plotPCA(vsd, intgroup=c("conditions", "sample_factoring"), returnData=TRUE)
percentVar <- round(100 * attr(pcaData, "percentVar"))
p <- ggplot(pcaData, aes(PC1, PC2, color=sample_factoring, shape=conditions)) +
  scale_color_manual(name="My classes",values = colors) +
  geom_point(size=3) +
  xlab(paste0("PC1: ",percentVar[1],"% variance")) +
  ylab(paste0("PC2: ",percentVar[2],"% variance")) + 
  coord_fixed()
ggsave(paste(matrix.file,".pca.pdf",sep=''), p)




            

