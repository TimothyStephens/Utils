#!/usr/bin/env Rscript

DESCRIPTION="
##
## Plot read depth (DP) for variants from each sample. File to plot should have *.GT.DP.txt extension (script will auto find these files).
##

# Example:
Rscript plot_DP_scores.R out_prefix cutoff x-lim

# out_prefix:
Prefix to use for output files.

# cutoff:
Position along x-axis to plot red line (helps to pick filtering cutoff)

# x-lim
Max x value to plot. 

"

args = commandArgs(trailingOnly=TRUE)
# Test if there is two arguments: if not, return an error
if (length(args)!=3) {
        cat(DESCRIPTION)
        stop("Three arguments must be supplied (out_prefix, cutoff, x-lim)", call.=FALSE)
}

out <- args[1]
cutoff <- as.double(args[2])
x.lim <- as.double(args[3])

nameList <- Sys.glob("*.GT.DP.txt")
nsamples <- length(nameList)
print("Found DP info files:")
print(nameList)

qlist <- matrix(nrow = nsamples, ncol = 3)
qlist <- data.frame(qlist, row.names=nameList)
colnames(qlist)<-c('5%', '10%', '99%')

pdf(paste(out, ".pdf", sep=''))
par(mar=c(5, 3, 3, 2), cex=1.5, mfrow=c(4,2)) # number of plots per page
for (i in 1:nsamples) {
  DP <- read.table(nameList[i], header = T)
  qlist[i,] <- quantile(DP[,1], c(.05, .1, .99), na.rm=T)
  d <- density(DP[,1], from=0, to=x.lim, bw=1, na.rm =T)
  plot(d, xlim = c(0,x.lim), main=nameList[i], col="blue", xlab = dim(DP)[1], lwd=2)
  abline(v=cutoff, col='red', lwd=0.5)
}
dev.off()

write.table(qlist, paste(out, ".percentiles.txt", sep=''))
