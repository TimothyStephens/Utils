library(ggplot2)
library(gridExtra)
# 
# Takes time course data (with condition information) and plots each 
# sequence on a seperate PDF page
# 
#   ## DATA:
# 
#   SeqName | Time Points Treatment |  Time Points Control  | 
#           | 1 | 1 | 2 | 2 | 3 | 3 | 1 | 1 | 2 | 2 | 3 | 3 |
#   --------|-----------------------|-----------------------|
#   Seq1    | 5 | 6 | 0 | 0 | 9 | 9 | 9 | 9 | 0 | 0 | 9 | 9 |
#   Seq2    | 0 | 0 | 1 | 1 | 0 | 1 | 0 | 0 | 1 | 1 | 0 | 1 |
#   
#   
#   ## Expected input format:
# |------|------|------------|-----------|
# | Name | Time | Expression | Condition |
# |------|------|------------|-----------|
# | Seq1 |   1  |      5     |     C     |
# | Seq1 |   1  |      6     |     C     |
# | Seq1 |   2  |      0     |     C     |
# | Seq1 |   2  |      0     |     C     |
# | Seq1 |   3  |      9     |     C     |
# | Seq1 |   3  |      9     |     C     |
# | Seq2 |   1  |      0     |     C     |
# | Seq2 |   1  |      0     |     C     |
# | Seq2 |   2  |      1     |     C     |
# | Seq2 |   3  |      1     |     C     |
# | Seq2 |   3  |      0     |     C     |
# | Seq2 |   3  |      1     |     C     |
# | Seq1 |   1  |      9     |     T     |
# | Seq1 |   1  |      9     |     T     |
# | Seq1 |   2  |      0     |     T     |
# | Seq1 |   2  |      0     |     T     |
# | Seq1 |   3  |      9     |     T     |
# | Seq1 |   3  |      9     |     T     |
# | Seq2 |   1  |      0     |     T     |
# | Seq2 |   1  |      0     |     T     |
# | Seq2 |   2  |      1     |     T     |
# | Seq2 |   3  |      1     |     T     |
# | Seq2 |   3  |      0     |     T     |
# | Seq2 |   3  |      1     |     T     |
# |------|------|------------|-----------|
#   


## Load command line args
args = commandArgs(trailingOnly=TRUE)
# test if there 2 arguments: if not, return an error
if (length(args)<=2) {
  stop("R script requires 2 files: melted_expression_table output.pdf [order2plot].n", call.=FALSE)
}

# args <- c("test.melted", "test.melted.plots.pdf")
# args <- c("test.melted", "test.melted.plots.pdf", "test.order2plot")
melted.expression.table.file <- args[1]
output.pdf.file <- args[2]
order2plot.file <- args[3]
plot.page.nrows <- 2
plot.page.ncols <- 2

melted.expression.table <- read.table(melted.expression.table.file, header = T, sep = '\t')
## Open list of names and order to plot if avaliable.
if (is.na(order2plot.file)) {
  names2plot <- unique(melted.expression.table$Name)
} else {
  names2plot <- unique(readLines(order2plot.file))
  names2plot <- names2plot[names2plot != ""]
}

plots <- list()
for (name in names2plot) {
  tmp <- melted.expression.table[melted.expression.table$Name == name, ]
  plots[[name]] <- ggplot(tmp, aes(x=Time, y=Expression, color=Condition)) + geom_point(alpha=0.7) + 
    stat_summary(fun = mean, geom="line") + theme_light() + 
    scale_color_manual(values=c("#2b83ba", "#d7191c", "#1a9641", "#7b3294", "#a6611a")) +
    theme(legend.position = "bottom", 
          legend.title = element_text(family = "sans", size=6), 
          legend.text = element_text(family = "sans", size=6),
          plot.title = element_text(family = "sans", size=8, face="bold"), 
          axis.text.x = element_text(family = "sans", size=6),
          axis.text.y = element_text(family = "sans", size=6), 
          axis.title.x = element_text(family = "sans", size=8, face="bold"),
          axis.title.y = element_text(family = "sans", size=8, face="bold")) +
    ggtitle(name[[1]])
}

ml <- marrangeGrob(plots, nrow=plot.page.nrows, ncol=plot.page.ncols, layout_matrix=matrix(1:(plot.page.nrows*plot.page.ncols), plot.page.nrows, plot.page.ncols, TRUE))
ggsave(output.pdf.file, ml)

