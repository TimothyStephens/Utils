#!/usr/bin/env Rscript
library(stringr)

DESCRIPTION="
##
## DESCRIPTION
##

# Example:
Rscript Enrichment_Analysis.R contingency_table [Pval]

# contingency_table (can be gzipped; tab delimited):
	- Expects a header row
	- Need the columns to be in the order shown below. 

############################################### Format Example ###############################################
# PfamDomain    DomainTestCount  DomainNotTestCount      NotDomainTestCount  NotDomainNotTestCount     #
# F1            0                5                       10                  30                        #
# F2            1                9                       9                   26                        #
# F3            2                8                       8                   27                        #
# F4            3                7                       7                   28                        #
# F5            4                6                       6                   29                        #
##############################################################################################################

# Pval (float; default 0.05): max p-value (Pval<=X) of domains reported in output:
	- This is an unadjusted p-value, adjusted p-value in results withh br >Pval
"

args = commandArgs(trailingOnly=TRUE)
# test if there is at least one argument: if not, return an error
if (length(args)<1) {
  stop("At least one argument must be supplied (contingency_table [Pval]).n", call.=FALSE)
}
con.file <- args[1]
if (! is.na(args[2])){filter.Pval <- args[2]} else {filter.Pval <- 0.05}



ConTable <- read.table(con.file, header = T)

# Run test for each feature
ConTable_Enrichment <- data.frame(FeatureId = double(), PvalOver = numeric(),  PvalUnder = numeric(),
				  DomainTestCount = numeric(), DomainNotTestCount = numeric()) # Define dataframe for results
for (i in 1:nrow(ConTable)){
    FID <- as.character(ConTable[i, 1])
    ContTable <- matrix(data = c(ConTable[i, 2],ConTable[i, 3], ConTable[i, 4], ConTable[i, 5]), nrow = 2)
    ConTable_Enrichment[i,] <- c(FID, fisher.test(ContTable, alternative = "greater")$p.value, 
				 fisher.test(ContTable, alternative = "less")$p.value,
				 ConTable[i, 2], ConTable[i, 3])
}

# Adjust p-val using FDR for both directions
ConTable_Enrichment$AdjPvalOver <- p.adjust(ConTable_Enrichment$PvalOver, method = "BH")
ConTable_Enrichment$AdjPvalUnder <- p.adjust(ConTable_Enrichment$PvalUnder, method = "BH")

# Print results only for those domains enriched with a Pval <= X (default: 0.05) - the adjusted Pval might be too strict

ConTable_sigOver <- ConTable_Enrichment[as.double(ConTable_Enrichment$PvalOver) <= filter.Pval, c("FeatureId", "PvalOver", "AdjPvalOver", "DomainTestCount", "DomainNotTestCount")]
colnames(ConTable_sigOver) <- c("Id", "Pval", "AdjPval", "DomainTestCount", "DomainNotTestCount")
ConTable_sigOver$Direction <- rep("OVER", length.out = nrow(ConTable_sigOver))

write.table(ConTable_sigOver[order(as.double(ConTable_sigOver$Pval), decreasing = F),], file = paste(con.file, "_sigPvalue_over.txt", sep=''), quote = F,
            sep = "\t", row.names = F)

ConTable_sigUnder <- ConTable_Enrichment[as.double(ConTable_Enrichment$PvalUnder) <= filter.Pval, c("FeatureId", "PvalUnder", "AdjPvalUnder", "DomainTestCount", "DomainNotTestCount")]
colnames(ConTable_sigUnder) <- c("Id", "Pval", "AdjPval", "DomainTestCount", "DomainNotTestCount")
ConTable_sigUnder$Direction <- rep("UNDER", length.out = nrow(ConTable_sigUnder))

write.table(ConTable_sigUnder[order(as.double(ConTable_sigUnder$Pval), decreasing = F),], file = paste(con.file, "_sigPvalue_under.txt", sep=''), quote = F,
            sep = "\t", row.names = F)



