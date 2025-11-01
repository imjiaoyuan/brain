# Perform initial quality control on raw FASTQ data.
fastqc -t 8 ${INPUT_DIR}/${FILEID}.fastq.gz -o ${OUTPUT_DIR}/${FILEID}

# Perform quality control and trimming of raw FASTQ data.
fastp -i ${INPUT_DIR}/${FILEID}_R1.fastq.gz -I ${INPUT_DIR}/${FILEID}_R2.fastq.gz -o ${OUTPUT_DIR}/${FILEID}_clean_R1.fastq.gz -O ${OUTPUT_DIR}/${FILEID}_clean_R2.fastq.gz --detect_adapter_for_pe -h ${OUTPUT_DIR}/${FILEID}.html -j ${OUTPUT_DIR}/${FILEID}.json

# Index the reference genome for BWA aligner.
bwa index -p /public/home/wangweiwei/MT_temp/shuilian/bwa_index/shuilian_genome /public/home/wangweiwei/MT_temp/shuilian/转录组分析结果及参考基因组注释文件-HM250630DDY01+广西农业科学院9例植物组织ATAC-seq测序分析/ref/HiC.review.assembly.chr.genome.fa

# Align paired-end reads to the reference genome and sort the output.
bwa mem -t 8 -M -k 16 /public/home/wangweiwei/MT_temp/shuilian/bwa_index/shuilian_genome ${INPUT_DIR}/${FILEID}_R1.fastq.gz ${INPUT_DIR}/${FILEID}_R2.fastq.gz | samtools sort -@ 8 -o ${OUTPUT_DIR}/${FILEID}.bam -

# Index the sorted BAM file for fast access.
samtools index ${INPUT_DIR}/${FILEID}.bam

# Generate alignment statistics from the BAM file.
samtools flagstat ${INPUT_DIR}/${FILEID}.bam > ${OUTPUT_DIR}/${FILEID}.flagstat.txt

# Calculate the effective genome size from the reference FASTA file.
conda install bioconda::ucsc-facount
faCount ${INPUT_DIR}/${FILEID}.fa

# Generate a bigWig coverage file with a 10bp bin size.
bamCoverage --bam ${INPUT_DIR}/${FILEID}.bam -o ${OUTPUT_DIR}/${FILEID}.bw --binSize 10 --effectiveGenomeSize 1076121553 --normalizeUsing RPKM --smoothLength 50 -p 8

# Generate a bigWig coverage file with a 50bp bin size.
bamCoverage --bam ${INPUT_DIR}/${FILEID}.bam -o ${OUTPUT_DIR}/${FILEID}.bw --binSize 50 --effectiveGenomeSize 1076121553 --normalizeUsing RPKM --smoothLength 150 -p 8

# Call peaks from the BAM file using MACS2.
macs2 callpeak -g 1076121553 -t ${INPUT_DIR}/${FILEID}.bam -f BAMPE --nomodel --extsize 200 --shift -100 --pvalue 0.01 -B -n ${FILEID} --outdir ${OUTPUT_DIR} --keep-dup all --call-summits

# Install the bedops toolkit using conda.
conda install bioconda::bedops

# Convert a GFF annotation file to BED format.
awk 'BEGIN{OFS="\t"} $3 == "gene" {id=$9; sub("ID=","",id); print $1, $4-1, $5, id, $6, $7}' /public/home/wangweiwei/MT_temp/juhua/gfffiles/Chrysanthemum_indicum.gff > /public/home/wangweiwei/MT_temp/juhua/bedfiles/Chrysanthemum_indicum2.bed
gff2bed < /public/home/wangweiwei/MT_temp/shuilian/转录组分析结果及参考基因组注释文件-HM250630DDY01+广西农业科学院9例植物组织ATAC-seq测序分析/ref/Nymphaea_Paul.gene.gff > /public/home/wangweiwei/MT_temp/shuilian/转录组分析结果及参考基因组注释文件-HM250630DDY01+广西农业科学院9例植物组织ATAC-seq测序分析/ref/Nymphaea_Paul.gene.bed

# Create a directory for TSS analysis results.
mkdir -p /public/home/wangweiwei/MT_temp/shuilian/tss

# Calculate signal scores centered on the Transcription Start Site (TSS).
computeMatrix reference-point \
    -p 8 \
    --referencePoint TSS \
    --missingDataAsZero \
    -b 3000 -a 3000 \
    -R /public/home/wangweiwei/MT_temp/shuilian/转录组分析结果及参考基因组注释文件-HM250630DDY01+广西农业科学院9例植物组织ATAC-seq测序分析/ref/Nymphaea_Paul.gene.bed \
    -S VL0-1_S99_clean.bw VL0-3_S99_clean.bw VL1-2_S99_clean.bw VL2-1_S99_clean.bw VL2-3_S99_clean.bw VL0-2_S99_clean.bw VL1-1_S99_clean.bw VL1-3_S99_clean.bw VL2-2_S99_clean.bw \
    -o /public/home/wangweiwei/MT_temp/shuilian/tss/TSS_combined_matrix.gz && \
# Plot a heatmap of the signal around the TSS.
plotHeatmap \
    -m /public/home/wangweiwei/MT_temp/shuilian/tss/TSS_combined_matrix.gz \
    -out /public/home/wangweiwei/MT_temp/shuilian/tss/TSS_heatmap.png \
    --colorMap viridis \
    --zMin 0 --zMax 10 \
    --regionsLabel "Peaks" \
    --samplesLabel VL0-1_S99 VL0-3_S99 VL1-2_S99 VL2-1_S99 VL2-3_S99 VL0-2_S99 VL1-1_S99 VL1-3_S99 VL2-2_S99 && \
# Plot an average profile of the signal around the TSS.
plotProfile \
    -m /public/home/wangweiwei/MT_temp/shuilian/tss/TSS_combined_matrix.gz \
    -out /public/home/wangweiwei/MT_temp/shuilian/tss/TSS_profile.png \
    --colors blue green red purple \
    --plotHeight 10 --plotWidth 12

# Calculate signal scores across scaled gene bodies.
computeMatrix scale-regions \
    -p 8 \
    -S VL0-1_S99_clean.bw VL0-3_S99_clean.bw VL1-2_S99_clean.bw VL2-1_S99_clean.bw VL2-3_S99_clean.bw VL0-2_S99_clean.bw VL1-1_S99_clean.bw VL1-3_S99_clean.bw VL2-2_S99_clean.bw \
    -R /public/home/wangweiwei/MT_temp/shuilian/转录组分析结果及参考基因组注释文件-HM250630DDY01+广西农业科学院9例植物组织ATAC-seq测序分析/ref/Nymphaea_Paul.gene.bed \
    -a 3000 -b 3000 \
    --regionBodyLength 5000 \
    --skipZeros \
    -o /public/home/wangweiwei/MT_temp/shuilian/tss/matrix_gene_body.gz && \
# Plot a heatmap of the signal across gene bodies.
plotHeatmap \
    -m /public/home/wangweiwei/MT_temp/shuilian/tss/matrix_gene_body.gz \
    -out /public/home/wangweiwei/MT_temp/shuilian/tss/gene_body_heatmap.png \
    --colorMap RdYlBu \
    --zMin -2 --zMax 2 \
    --samplesLabel VL0-1_S99 VL0-3_S99 VL1-2_S99 VL2-1_S99 VL2-3_S99 VL0-2_S99 VL1-1_S99 VL1-3_S99 VL2-2_S99 && \
# Plot an average profile of the signal across gene bodies.
plotProfile \
    -m /public/home/wangweiwei/MT_temp/shuilian/tss/matrix_gene_body.gz \
    -out /public/home/wangweiwei/MT_temp/shuilian/tss/gene_body_profile.png \
    --startLabel "TSS" \
    --endLabel "TES" \
    --plotType std

# Find enriched motifs within peak regions using HOMER.
findMotifsGenome.pl ${INPUT_DIR}/${FILEID}.narrowPeak /public/home/wangweiwei/MT_temp/shuilian/转录组分析结果及参考基因组注释文件-HM250630DDY01+广西农业科学院9例植物组织ATAC-seq测序分析/ref/HiC.review.assembly.chr.genome.fa ${OUTPUT_DIR}/${FILEID} -size 200 -p 8


# Count reads in consensus peak regions for all samples.
cd /public/home/wangweiwei/MT_temp/shuilian/bamfiles
featureCounts -T 8 \
              -p \
              -F SAF \
              -a consensus_peaks.saf \
              -o counts_matrix.txt \
              VL0-1_S99_clean.bam \
              VL0-2_S99_clean.bam \
              VL0-3_S99_clean.bam \
              VL1-1_S99_clean.bam \
              VL1-2_S99_clean.bam \
              VL1-3_S99_clean.bam \
              VL2-1_S99_clean.bam \
              VL2-2_S99_clean.bam \
              VL2-3_S99_clean.bam