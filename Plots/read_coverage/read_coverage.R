#!/usr/bin/env Rscript
library(ggplot2)

DESCRIPTION="
Plot seq read coverage vs. seq length

# Example:
Rscript read_coverage.R in_cov_file out_plot

# in_cov_file (can be gzipped):
seqid  	coverage   length 	group
S1  0.2159 	6619214	Base
S2  0.0699 	3941137	Base
..
..

# out_plot: Output file for generated plot.

"

args = commandArgs(trailingOnly=TRUE)
# Test if there is two arguments: if not, return an error
if (length(args)!=2) {
  cat(DESCRIPTION)
  stop("Two arguments must be supplied (in_cov_file, out_plot)", call.=FALSE)
}
#args <- c("test.txt", "test.txt.plots.pdf")

## Load matrix
data.file <- args[1]
out.file <- args[2]

## Main code
# Refs: 
# - https://stackoverflow.com/questions/52602503/display-an-axis-value-in-millions-in-ggplot 
# - https://5harad.com/mse125/r/visualization_code.html
addUnits <- function(n) {
  labels <- ifelse(n < 1000, n,  # less than thousands
                   ifelse(n < 1e6, paste0(round(n/1e3), 'k'),  # in thousands
                          ifelse(n < 1e9, paste0(round(n/1e6), 'M'),  # in millions
                                 ifelse(n < 1e12, paste0(round(n/1e9), 'B'), # in billions
                                        ifelse(n < 1e15, paste0(round(n/1e12), 'T'), # in trillions
                                               'too big!'
                                        )))))
  return(labels)
}



# Read data and check it has the required headers
df <- read.table(file=data.file, header=TRUE, sep="\t")

if (! all(c("seqid", "coverage", "length", "group") %in% colnames(df))) {
  stop("Input data must have the following column headers: 'seqid [tab] coverage [tab] length [tab] group'", call.=FALSE)
}

# 2d dot plot - length vs. coverage (color by groups given in file)
p <- ggplot(df, aes(x=length, y=coverage, color=group)) + 
  geom_point() +
  scale_x_continuous(labels = addUnits) +
  xlab("Length (bp)") +
  ylab("Read coverage") +
  theme_bw() +
  theme(legend.title = element_blank())
ggsave(out.file, p)



