library(rtracklayer)
library(GenomicRanges)
peak_dir <- "D:/scu/Desktop/shuilian/sl-calling_peak"
setwd(peak_dir)

peak_files <- list.files(
  path = peak_dir,
  pattern = "\\.narrowPeak$",
  full.names = TRUE
)
all_peaks_list <- lapply(peak_files, rtracklayer::import)
all_peaks_combined <- unlist(GRangesList(all_peaks_list))
consensus_peaks <- GenomicRanges::reduce(all_peaks_combined, min.gapwidth=0)
mcols(consensus_peaks)$peakID <- paste0("peak_", 1:length(consensus_peaks))

saf_annotation <- data.frame(
  GeneID = mcols(consensus_peaks)$peakID,
  Chr = seqnames(consensus_peaks),
  Start = start(consensus_peaks),
  End = end(consensus_peaks),
  Strand = strand(consensus_peaks)
)

write.table(
  saf_annotation,
  file = "consensus_peaks.saf",
  quote = FALSE,
  sep = "\t",
  row.names = FALSE,
  col.names = TRUE
)

message("完成！共识峰已保存到 consensus_peaks.saf")