#!/usr/bin/env Rscript

### Some constants


UTR_offset = 0
plot.dir <- "read_covergae_wiggle_plots"
dir.create(plot.dir, showWarnings = F)


### Load program arguments


assert = function(expr, errmsg) {
  if (!expr) {
    cat(errmsg, "\n", sep = "", file = stderr())
    quit(save = "no", status = 1)
  }
}


args = commandArgs(TRUE)
#args <- c("test/HL-6h-3.transcript.readdepth", "test/HL-6h-3.uniq.transcript.readdepth", "new_HLI_genes.names.txt") # TEST
args <- c("All_combined.transcript.readdepth", "All_combined.uniq.transcript.readdepth", "new_HLI_genes.names.txt")
assert(length(args) == 3, "Usage: rsem-gen-transcript-plots-EDIT.R total_readdepth uniq_readdepth input_list")

readdepth_total.file = args[1]
readdepth_uniq.file = args[2]
input_list = args[3]


### Load read depth files


load_read_depth = function(file) {
  depth = read.table(file, sep = "\t", stringsAsFactors = FALSE)
  rownames(depth) = depth[,1]
  return (depth)
}

readdepth_total = load_read_depth(readdepth_total.file)
ord_depth_total = order(readdepth_total[,1])

readdepth_uniq = load_read_depth(readdepth_uniq.file)
ord_uniq_depth = order(readdepth_uniq[,1])

assert(sum(readdepth_total[ord_depth_total,1] != readdepth_uniq[ord_uniq_depth,1]) == 0, "transcript IDS in read depth and unique read depth files are not the same!")
assert(sum(readdepth_total[ord_depth_total,2] != readdepth_uniq[ord_uniq_depth,2]) == 0, "transcript lengths in read depth and unique read depth files are not the same!")


cat("Loading read depth files is done!\n")


### Load and transfer IDs


ids = scan(file = input_list, what = "", sep = "\n", strip.white = T)
assert(length(ids) > 0, "You should provide at least one ID.")


### Generate plots

# pos is a number indexing the position in readdepth/readdepth_uniq
make_a_plot = function(pos) {
  ## Length of transcript
  len = readdepth_total[pos, 2]
  
  ## Get depth at each pos in transcript (if depth is NA assume zero coverage)
  # Total
  depths = readdepth_total[pos, 3]
  if (is.na(depths)) {
    wiggle = rep(0, len)
  } else {
      wiggle = as.numeric(unlist(strsplit(depths, split = " ")))
  }
  # Uniq
  depths = readdepth_uniq[pos, 3]
  if (is.na(depths)) {
    wiggle_uniq = rep(0, len)
  } else {
    wiggle_uniq = as.numeric(unlist(strsplit(depths, split = " ")))
  }
  
  ## Check that all positions along readdepth_total is >= all positions along readdepth_uniq
  if (len != sum(wiggle >= wiggle_uniq)) {
    cat("Warning: transcript ", id, " has position(s) that read covarege with multireads is smaller than read covarge without multireads.\n", "         The 1-based position(s) is(are) : ", which(wiggle < wiggle_uniq), ".\n", "         This may be due to floating point arithmetics.\n", sep = "") 
  }
  heights = rbind(wiggle_uniq, wiggle - wiggle_uniq)
  barplot(heights, space = 0, border = NA, names.arg = 1:len, col = c("black", "red")) 
  abline(v=UTR_offset, col="blue")
  abline(v=len-UTR_offset, col="blue")
  
  title(main = readdepth_total[pos, 1])
}




for (id in ids) {
  #print (id)
  pdf(paste(plot.dir, "/", id, ".plot.pdf", sep=''), width = 14, height = 7)
  make_a_plot(id)
  dev.off.output = dev.off()
}


cat("Plots are generated!\n")


