library(topGO)


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



#Polarella__vs__AllDinos
topGOwrapper(GOtermsfile = "data_AllDinos.TopGO", idfile = "data_Polarella_IDs.txt", outfile = "data_Polarella__vs__AllDinos_BP.txt", ontologytype = "BP")
topGOwrapper(GOtermsfile = "data_AllDinos.TopGO", idfile = "data_Polarella_IDs.txt", outfile = "data_Polarella__vs__AllDinos_MF.txt", ontologytype = "MF")
topGOwrapper(GOtermsfile = "data_AllDinos.TopGO", idfile = "data_Polarella_IDs.txt", outfile = "data_Polarella__vs__AllDinos_CC.txt", ontologytype = "CC")


