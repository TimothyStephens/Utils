#!/usr/bin/env Rscript

DESCRIPTION="
## 
## DESCRIPTION
## 

# Example:
Rscript R_boilerplate.R in_file out_file

# in_file (can be gzipped):
..
..

# out_file (can be gzipped):
..
..

"

args = commandArgs(trailingOnly=TRUE)
# Test if there is two arguments: if not, return an error
if (length(args)!=2) {
	cat(DESCRIPTION)
	stop("Two arguments must be supplied (in_file, out_file)", call.=FALSE)
}

## Load matrix
in.file <- args[1]
out.file <- args[2]

## Main code

# Read data and check it has the required headers
df <- read.table(file=data.file, header=TRUE, sep="\t")

if (! all(c("seqids", "length", "cov") %in% colnames(df))) {
  stop("Input data must have the following column headers: 'seqid [tab] length [tab] cov'", call.=FALSE)
}


