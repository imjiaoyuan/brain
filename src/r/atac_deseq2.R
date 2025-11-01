rm(list = ls())

library(tidyverse)
library(DESeq2)
library(ggvenn)

raw_counts <- read.table("D:/scu/Desktop/shuilian/counts_matrix.txt", header = TRUE, sep = "\t", comment.char = "#", check.names = FALSE)

peak_coords <- raw_counts[, 1:6]
count_matrix <- as.matrix(raw_counts[, 7:ncol(raw_counts)])
rownames(count_matrix) <- peak_coords$Geneid

colnames(count_matrix) <- gsub("_S99_clean.bam", "", colnames(count_matrix))

sample_info <- data.frame(
  row.names = colnames(count_matrix),
  condition = factor(substr(colnames(count_matrix), 1, 3))
)

dds <- DESeqDataSetFromMatrix(countData = count_matrix,
                              colData = sample_info,
                              design = ~ condition)

keep <- rowSums(counts(dds)) >= 10
dds <- dds[keep,]

dds <- DESeq(dds)

res_vl1_vs_vl0 <- results(dds, contrast=c("condition", "VL1", "VL0"))
res_vl2_vs_vl0 <- results(dds, contrast=c("condition", "VL2", "VL0"))
res_vl2_vs_vl1 <- results(dds, contrast=c("condition", "VL2", "VL1"))

results_final_vl1_vl0 <- merge(peak_coords, as.data.frame(res_vl1_vs_vl0), by.x="Geneid", by.y="row.names")
results_final_vl2_vl0 <- merge(peak_coords, as.data.frame(res_vl2_vs_vl0), by.x="Geneid", by.y="row.names")
results_final_vl2_vl1 <- merge(peak_coords, as.data.frame(res_vl2_vs_vl1), by.x="Geneid", by.y="row.names")

results_final_vl1_vl0 <- results_final_vl1_vl0[order(results_final_vl1_vl0$pvalue), ]
results_final_vl2_vl0 <- results_final_vl2_vl0[order(results_final_vl2_vl0$pvalue), ]
results_final_vl2_vl1 <- results_final_vl2_vl1[order(results_final_vl2_vl1$pvalue), ]

write.csv(results_final_vl1_vl0, "D:/scu/Desktop/shuilian/ACCURATE_deseq2_results_VL1_vs_VL0.csv", row.names = FALSE)
write.csv(results_final_vl2_vl0, "D:/scu/Desktop/shuilian/ACCURATE_deseq2_results_VL2_vs_VL0.csv", row.names = FALSE)
write.csv(results_final_vl2_vl1, "D:/scu/Desktop/shuilian/ACCURATE_deseq2_results_VL2_vs_VL1.csv", row.names = FALSE)

sig_vl1_vs_vl0 <- results_final_vl1_vl0$Geneid[!is.na(results_final_vl1_vl0$padj) & results_final_vl1_vl0$padj < 0.05]
sig_vl2_vs_vl0 <- results_final_vl2_vl0$Geneid[!is.na(results_final_vl2_vl0$padj) & results_final_vl2_vl0$padj < 0.05]
sig_vl2_vs_vl1 <- results_final_vl2_vl1$Geneid[!is.na(results_final_vl2_vl1$padj) & results_final_vl2_vl1$padj < 0.05]

venn_list <- list(
  `VL1 vs VL0` = sig_vl1_vs_vl0,
  `VL2 vs VL0` = sig_vl2_vs_vl0,
  `VL2 vs VL1` = sig_vl2_vs_vl1
)

suppressWarnings({
  venn_plot <- ggvenn(
    venn_list,
    fill_color = c("#0073C2FF", "#EFC000FF", "#CD534CFF"),
    stroke_size = 0.5,
    set_name_size = 4,
    text_size = 3
  )
  
  ggsave(
    "D:/scu/Desktop/shuilian/ACCURATE_Venn_Diagram_Diff_Peaks.png",
    plot = venn_plot,
    width = 8,
    height = 6,
    dpi = 300,
    bg = "white"
  )
})