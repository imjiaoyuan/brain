# Integrative_Venn_and_Gene_List_Output.R

rm(list = ls())

library(tidyverse)
library(readxl)
library(ggvenn)

annotation_dir <- "D:/scu/Desktop/shuilian/Annotation_Results/"
rna_seq_dir <- "D:/scu/Desktop/shuilian/dif_genes/"
output_dir <- "D:/scu/Desktop/shuilian/Integrative_Results/"
dir.create(output_dir, showWarnings = FALSE)

rna_gene_id_column <- "gene_name"
rna_log2fc_column <- "log2FoldChange"
rna_padj_column <- "padj"

comparisons <- c("VL1_vs_VL0", "VL2_vs_VL0", "VL2_vs_VL1")

for (comp in comparisons) {
  
  annotated_peaks_file <- file.path(annotation_dir, paste0(comp, "_Annotated_Peaks.csv"))
  rna_seq_file <- file.path(rna_seq_dir, paste0(comp, ".all.annot.xlsx"))
  
  if (file.exists(annotated_peaks_file) && file.exists(rna_seq_file)) {

    comp_output_dir <- file.path(output_dir, comp)
    dir.create(comp_output_dir, showWarnings = FALSE)

    atac_df <- read.csv(annotated_peaks_file)
    atac_up_genes <- atac_df %>% filter(peak_log2FC > 0) %>% pull(geneId) %>% unique()
    atac_down_genes <- atac_df %>% filter(peak_log2FC < 0) %>% pull(geneId) %>% unique()
  
    rna_df <- read_excel(rna_seq_file)
    sig_rna_df <- rna_df %>% filter(.data[[rna_padj_column]] < 0.05 & !is.na(.data[[rna_padj_column]]))
    rna_up_genes <- sig_rna_df %>% filter(.data[[rna_log2fc_column]] > 0) %>% pull(.data[[rna_gene_id_column]]) %>% unique()
    rna_down_genes <- sig_rna_df %>% filter(.data[[rna_log2fc_column]] < 0) %>% pull(.data[[rna_gene_id_column]]) %>% unique()

    activated_genes <- intersect(atac_up_genes, rna_up_genes)
    repressed_genes <- intersect(atac_down_genes, rna_down_genes)
    complex_up_down <- intersect(atac_up_genes, rna_down_genes)
    complex_down_up <- intersect(atac_down_genes, rna_up_genes)
    
    if (length(activated_genes) > 0) {
      writeLines(activated_genes, con = file.path(comp_output_dir, "Activated_Genes_ATAC_Up_RNA_Up.txt"))
    }
    if (length(repressed_genes) > 0) {
      writeLines(repressed_genes, con = file.path(comp_output_dir, "Repressed_Genes_ATAC_Down_RNA_Down.txt"))
    }
    if (length(complex_up_down) > 0) {
      writeLines(complex_up_down, con = file.path(comp_output_dir, "Complex_ATAC_Up_RNA_Down.txt"))
    }
    if (length(complex_down_up) > 0) {
      writeLines(complex_down_up, con = file.path(comp_output_dir, "Complex_ATAC_Down_RNA_Up.txt"))
    }

    venn_list <- list(
      `ATAC Up` = atac_up_genes,
      `RNA Up` = rna_up_genes,
      `ATAC Down` = atac_down_genes,
      `RNA Down` = rna_down_genes
    )
    
    suppressWarnings({
      venn_plot <- ggvenn(
        venn_list,
        columns = c("ATAC Up", "RNA Up", "ATAC Down", "RNA Down"),
        fill_color = c("#ff0000", "#00adff", "#ff852d", "#0000ff"),
        stroke_size = 0.5,
        set_name_size = 4,
        text_size = 3,
        show_percentage = FALSE
      )
    })
    
    ggsave(
      filename = file.path(comp_output_dir, paste0(comp, "_Integrative_Venn_Diagram.png")),
      plot = venn_plot,
      width = 10,
      height = 8,
      dpi = 300,
      bg = "white"
    )
  }
}