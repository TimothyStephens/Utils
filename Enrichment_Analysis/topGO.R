#!/usr/bin/env Rscript
library(topGO)

DESCRIPTION="
##
## DESCRIPTION
##

# Example:
Rscript topGO.R GO_terms target_ids out_prefix

# GO_terms (can be gzipped) - List of GO terms associated with each sequence (topGO format):
Seq1	GO:0005096, GO:0043547, GO:0016021
Seq2	GO:0004822, GO:0006428, GO:0016021, GO:0002161, GO:0106074, GO:0000049, GO:0005524
Seq3	GO:0008234, GO:0006508, GO:0005525
..
..

# target_ids (can be gzipped) - list of seq ids that are in target set (subset of GO_terms)
Seq1
Seq3
..
..

# out_prefix - prefix of output files:

"

args = commandArgs(trailingOnly=TRUE)
# Test if there is two arguments: if not, return an error
if (length(args)!=3) {
        cat(DESCRIPTION)
        stop("Three arguments must be supplied (GO_terms, target_ids, out_prefix)", call.=FALSE)
}

## Load matrix
GO_terms <- args[1]
target_ids <- args[2]
out_prefix <- args[3]

## Main code
topGOwrapper <- function(GOtermsfile, idfile, outfile, ontologytype){
  # Import GF universe with GO mappings
  UniGO <- readMappings(file=GOtermsfile)

  # Extract names into list
  GFnames <- names(UniGO)

  # Import GF test sets and create a factor vector in regard to universe
  ClA_abs_ids <- readLines(idfile)
  ClA_abs_list <- factor(as.integer(GFnames %in% ClA_abs_ids))
  names(ClA_abs_list) <- GFnames

  # Build topGO data objects
  ClA_abs_GOdata <- new("topGOdata", ontology = ontologytype, allGenes = ClA_abs_list,
                      annot = annFUN.gene2GO, gene2GO = UniGO)

  # Run Fisher's Exact test eliminating dependency of hierarchical GO terms

  ClA_abs_res <- runTest(ClA_abs_GOdata, algorithm = "elim", statistic = "fisher")
  sum(score(ClA_abs_res) <= 0.05)
  # Use values above for topNones in next command
  ClA_abs_sigGOs <- GenTable(ClA_abs_GOdata, Fisher = ClA_abs_res, orderBy = "Fisher", topNodes = 165)
  write.table(ClA_abs_sigGOs, outfile, quote = F, sep = "\t", row.names = F)
}


topGOwrapper(GOtermsfile = GO_terms, idfile = target_ids, outfile = paste(out_prefix, "_BP.txt", sep=''), ontologytype = "BP")
topGOwrapper(GOtermsfile = GO_terms, idfile = target_ids, outfile = paste(out_prefix, "_CC.txt", sep=''), ontologytype = "CC")
topGOwrapper(GOtermsfile = GO_terms, idfile = target_ids, outfile = paste(out_prefix, "_MF.txt", sep=''), ontologytype = "MF")


