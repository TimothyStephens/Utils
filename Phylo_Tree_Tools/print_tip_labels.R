#!/usr/bin/env Rscript
args = commandArgs(trailingOnly=TRUE)

if (length(args)==0) {
  stop("At least one tree file must be supplied (*.tre)", call.=FALSE)
}

library("ape")

for (tree_name in args) {
	tree <- ape::read.tree(tree_name)
	
	for (tip in tree[["tip.label"]]) {
		cat ( paste (tree_name, '\t', tip, '\n', sep='') )
	}
}

