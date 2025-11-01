#!/bin/bash

if [ -z "$1" ]; then
    exit 1
fi

PEAK_DIR="$1"

if [ ! -d "$PEAK_DIR" ]; then
    exit 1
fi

printf "%-25s %-12s %-12s %-12s %-12s %-15s %-12s %-12s\n" \
       "Sample" "Total_Peaks" "Mean_Width" "Min_Width" "Max_Width" "Mean_Pvalue" "Min_Pvalue" "Max_Pvalue"
echo "====================================================================================================================="

for file in "$PEAK_DIR"/*.narrowPeak; do
    [ -e "$file" ] || continue
    
    sample=$(basename "$file" _peaks.narrowPeak)
    
    stats=($(awk '
        BEGIN {
            min_w=9999999; max_w=0;
            min_p=9999999; max_p=0;
        }
        {
            w = $3 - $2;
            p = $8;
            sum_w += w;
            sum_p += p;
            if(w < min_w) min_w = w;
            if(w > max_w) max_w = w;
            if(p < min_p) min_p = p;
            if(p > max_p) max_p = p;
        }
        END {
            if (NR > 0) {
                printf "%d %.1f %d %d %.4f %.4f %.4f", NR, sum_w/NR, min_w, max_w, sum_p/NR, min_p, max_p;
            } else {
                printf "0 0.0 0 0 0.0000 0.0000 0.0000";
            }
        }' "$file"))

    printf "%-25s %-12d %-12.1f %-12d %-12d %-15.4f %-12.4f %-12.4f\n" \
           "$sample" "${stats[0]}" "${stats[1]}" "${stats[2]}" "${stats[3]}" "${stats[4]}" "${stats[5]}" "${stats[6]}"
done