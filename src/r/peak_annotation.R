rm(list = ls())

library(rtracklayer)
library(tidyverse)
library(GenomicRanges)

gff_file <- "D:/scu/Desktop/shuilian/Nymphaea_Paul.gene.gff"
input_dir <- "D:/scu/Desktop/shuilian/"
output_dir <- "D:/scu/Desktop/shuilian/Annotation_Results/"
dir.create(output_dir, showWarnings = FALSE)

gff_gene_id_column <- "ID" 

gff_data <- rtracklayer::import(gff_file)
genes_gr <- gff_data[gff_data$type == "gene"]
exons_gr <- gff_data[gff_data$type == "exon"]
promoters_gr <- promoters(genes_gr, upstream = 3000, downstream = 0)

comparisons <- c("VL1_vs_VL0", "VL2_vs_VL0", "VL2_vs_VL1")

for (comp in comparisons) {
  
  diff_peaks_file <- file.path(input_dir, paste0("ACCURATE_deseq2_results_", comp, ".csv"))
  diff_peaks_df <- read.csv(diff_peaks_file)
  
  sig_diff_peaks_df <- diff_peaks_df %>% filter(padj < 0.05)
  
  if (nrow(sig_diff_peaks_df) > 0) {
    
    peaks_gr <- GRanges(
      seqnames = Rle(sig_diff_peaks_df$Chr),
      ranges = IRanges(start = sig_diff_peaks_df$Start, end = sig_diff_peaks_df$End),
      peakId = sig_diff_peaks_df$Geneid,
      peak_log2FC = sig_diff_peaks_df$log2FoldChange,
      peak_padj = sig_diff_peaks_df$padj
    )
    
    nearest_hit <- distanceToNearest(peaks_gr, genes_gr)
    distances <- mcols(nearest_hit)$distance
    gene_indices <- subjectHits(nearest_hit)
    nearest_gene_ids <- mcols(genes_gr)[gene_indices, gff_gene_id_column]
    
    annotated_peaks_df <- as.data.frame(peaks_gr) %>%
      select(seqnames, start, end, peakId, peak_log2FC, peak_padj) %>%
      mutate(
        distanceToGene = distances,
        geneId = nearest_gene_ids
      )

    write.csv(
      annotated_peaks_df,
      file = file.path(output_dir, paste0(comp, "_Annotated_Peaks.csv")),
      row.names = FALSE
    )
    
    promoter_count <- sum(countOverlaps(peaks_gr, promoters_gr) > 0)
    exon_count <- sum(countOverlaps(peaks_gr, exons_gr) > 0)
    in_gene_count <- sum(countOverlaps(peaks_gr, genes_gr) > 0)
    intron_count <- in_gene_count - exon_count
    intergenic_count <- length(peaks_gr) - in_gene_count

    plot_data <- data.frame(
      Feature = c("Promoter", "Exon", "Intron", "Intergenic"),
      Count = c(promoter_count, exon_count, intron_count, intergenic_count)
    )
    
    plot_data <- plot_data %>% filter(Count > 0)

    distribution_plot <- ggplot(plot_data, aes(x = reorder(Feature, -Count), y = Count, fill = Feature)) +
      geom_bar(stat = "identity") +
      geom_text(aes(label = Count), vjust = -0.3, size = 4) +
      labs(
        title = paste("Distribution of Significant Peaks for", comp),
        x = "Genomic Feature",
        y = "Number of Peaks"
      ) +
      theme_classic() +
      theme(legend.position = "none")

    ggsave(
      filename = file.path(output_dir, paste0(comp, "_Peak_Distribution_Bar_Chart.png")),
      plot = distribution_plot,
      width = 8,
      height = 6,
      dpi = 300,
      bg = "white"
    )
  }
}