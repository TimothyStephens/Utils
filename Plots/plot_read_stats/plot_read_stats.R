#!/usr/bin/env Rscript
library(ggplot2)
library(scales)

args = commandArgs(trailingOnly=TRUE)

# test if there is at least one argument: if not, return an error
if (length(args)!=1) {
  stop("A file with read stats must be be supplied [file_name<\\t>no_reads<\\t>bases]", call.=FALSE)
} 
#args <- c("test_data")

df = read.table(args[1], header=FALSE)
names(df) <- c("file.name", "num.reads", "num.bases")

df.p1.median <- median(df$num.reads)
df.p1.mad <- mad(df$num.reads) ## Median Absolute Deviation

p1 <- ggplot(df, aes(x=file.name, y=num.reads)) + geom_point() + 
  xlab("Read File") + ylab("Number Reads") + 
  theme(axis.text.x = element_text(family="Times", color="black", size=12, face="plain", angle = 90, vjust = 0.5)) + ## Set font for axis values
  theme(axis.text.y = element_text(family="Times", color="black", size=12, face="plain")) +
  theme(axis.title.x = element_text(family="Times", color="black", size=12, face="bold")) + ## Set font for axis titles
  theme(axis.title.y = element_text(family="Times", color="black", size=12, face="bold")) + 
  scale_y_continuous(label=comma) +
  geom_hline(yintercept=df.p1.median, linetype="solid", color="black", size=0.1) + ## Add median and deviation lines to plot
  geom_hline(yintercept=df.p1.median+df.p1.mad, linetype="dashed", color="black", size=0.1) +
  geom_hline(yintercept=df.p1.median-df.p1.mad, linetype="dashed", color="black", size=0.1) +
  labs(caption = paste("Median: ", format(df.p1.median, big.mark = ','), 
                       "\nMedian Absolute Deviation: ", format(df.p1.mad, nsmall = 2, big.mark = ','), 
                       " (", round((df.p1.mad/df.p1.median)*100, digits = 2), "%)", sep='')) + ## Add info to plot
  theme(plot.caption=element_text(family="Times", color="black", face="plain", size=8, hjust=0, margin=margin(15,0,0,0)))
#p1

df.p2.median <- median(df$num.bases)
df.p2.mad <- mad(df$num.bases) ## Median Absolute Deviation

p2 <- ggplot(df, aes(x=file.name, y=num.bases)) + geom_point() + 
  xlab("Read File") + ylab("Number Bases") + 
  theme(axis.text.x = element_text(family="Times", color="black", size=12, face="plain", angle = 90, vjust = 0.5)) + ## Set font for axis values
  theme(axis.text.y = element_text(family="Times", color="black", size=12, face="plain")) +
  theme(axis.title.x = element_text(family="Times", color="black", size=12, face="bold")) + ## Set font for axis titles
  theme(axis.title.y = element_text(family="Times", color="black", size=12, face="bold")) + 
  scale_y_continuous(label=comma) +
  geom_hline(yintercept=df.p2.median, linetype="solid", color="black", size=0.1) + ## Add median and deviation lines to plot
  geom_hline(yintercept=df.p2.median+df.p2.mad, linetype="dashed", color="black", size=0.1) +
  geom_hline(yintercept=df.p2.median-df.p2.mad, linetype="dashed", color="black", size=0.1) +
  labs(caption = paste("Median: ", format(df.p2.median, big.mark = ','), 
                       "\nMedian Absolute Deviation: ", format(df.p2.mad, nsmall = 2, big.mark = ','), 
                       " (", round((df.p2.mad/df.p2.median)*100, digits = 2), "%)", sep='')) + ## Add info to plot
  theme(plot.caption=element_text(family="Times", color="black", face="plain", size=8, hjust=0, margin=margin(15,0,0,0)))
#p2


pdf(file=paste(args[1], ".sample_plot.pdf", sep=''), paper = 'a4r')
p1
p2
dev.off() 



