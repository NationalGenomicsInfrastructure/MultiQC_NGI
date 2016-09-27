#!/usr/bin/env Rscript

########################################
##
## dupRadar shell script
## call dupRadar R package from the shell for 
## easy integration into pipelines
##
## Holger Klein & Sergi Sayols
##
## https://sourceforge.net/projects/dupradar/
##
## input:
## - _duplicate marked_ bam file
## - gtf file
## - parameters for duplication counting routine:
##   stranded, paired, outdir, threads.
##
########################################
##
## Modified a lot by Phil Ewels (phil.ewels@scilifelab.se)
##
## Provides different output from original script above, including
## output taylored specifically for MultiQC dupRadar module,
## available in the MultiQC_NGI plugin
## Last updated: 2016-09-27
##
########################################


# Load / install dupRadar package
if (!require("dupRadar")){
    source("http://bioconductor.org/biocLite.R")
    biocLite("dupRadar")
    library("dupRadar")
}

####################
##
## get name patterns from command line
##
args   <- commandArgs(TRUE)

## the bam file to analyse
bam <- args[1]
## usually, same GTF file as used in htseq-count
gtf <- gsub("gtf=","",args[2])
## no|yes|reverse
stranded <- gsub("stranded=","",args[3])
## is a paired end experiment
paired   <- gsub("paired=","",args[4])
## output directory
outdir   <- gsub("outdir=","",args[5])
## number of threads to be used
threads  <- as.integer(gsub("threads=","",args[6]))

if(length(args) != 6) { 
  stop (paste0("Usage: ./dupRadar_NGI.sh <file.bam> <genes.gtf> ",
               "<stranded=[no|yes|reverse]> paired=[yes|no] ",
               "outdir=./ threads=1"))
}

if(!file.exists(bam)) { stop(paste("File",bam,"does NOT exist")) }
if(!file.exists(gtf)) { stop(paste("File",gtf,"does NOT exist")) }
if(!file.exists(outdir)) { stop(paste("Dir",outdir,"does NOT exist")) }
if(is.na(stranded) | !(grepl("no|yes|reverse",stranded))) { stop("Stranded has to be no|yes|reverse") }
if(is.na(paired) | !(grepl("no|yes",paired))) { stop("Paired has to be no|yes") }
if(is.na(threads)) { stop("Threads has to be an integer number") }
stranded <- if(stranded == "no") 0 else if(stranded == "yes") 1 else 2
cat("Processing file ", bam, " with GTF ", gtf, "\n")

dm <- analyzeDuprates(bam, gtf, stranded, (paired == "yes"), threads)
write.table(dm, file=paste(outdir,"/",gsub("(.*)\\.[^.]+","\\1",basename(bam)), "_dupMatrix.txt", sep=""), quote=F, row.name=F, sep="\t")

# 2D density scatter plot
pdf(paste0(outdir,"/",gsub("(.*)\\.[^.]+","\\1",basename(bam)), "_duprateExpDens.pdf"))
duprateExpDensPlot(DupMat=dm)
title("Density scatter plot")
mtext(basename(bam), side=3)
dev.off()
fit <- duprateExpFit(DupMat=dm)
cat(
  paste("- dupRadar Int (duprate at low read counts):", fit$intercept),
  paste("- dupRadar Sl (progression of the duplication rate):", fit$slope),
  fill=TRUE, labels=basename(bam),
  file=paste0(outdir,"/",gsub("(.*)\\.[^.]+","\\1",basename(bam)), "_intercept_slope.txt"), append=FALSE
)

# Get numbers from dupRadar GLM
curve_x <- sort(log10(dm$RPK))
curve_y = 100*predict(fit$glm,data.frame(x=sort(x)),type="response")
# Remove all of the infinite values
infs = which(curve_x %in% c(-Inf,Inf))
curve_x = curve_x[-infs]
curve_y = curve_y[-infs]
# Reduce number of data points
curve_x <- curve_x[seq(1, length(curve_x), 100)]
curve_y <- curve_y[seq(1, length(curve_y), 100)]
# Convert x values back to real counts
curve_x = 10^curve_x
# Write to file
write.table(
  cbind(curve_x, curve_y),
  file=paste0(outdir,"/",gsub("(.*)\\.[^.]+","\\1",basename(bam)), "_duprateExpDensCurve.txt"),
  quote=FALSE, row.names=FALSE
)

# Distribution of expression box plot
pdf(paste0(outdir,"/",gsub("(.*)\\.[^.]+","\\1",basename(bam)), "_duprateExpBoxplot.pdf"))
duprateExpBoxplot(DupMat=dm)
title("Percent Duplication by Expression")
mtext(basename(bam), side=3)
dev.off()

# Distribution of RPK values per gene
pdf(paste0(outdir,"/",gsub("(.*)\\.[^.]+","\\1",basename(bam)), "_expressionHist.pdf"))
expressionHist(DupMat=dm)
title("Distribution of RPK values per gene")
mtext(basename(bam), side=3)
dev.off()

#Printing sessioninfo to standard out
print(basename(bam))
citation("dupRadar")
sessionInfo()
