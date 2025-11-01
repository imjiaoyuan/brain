#!/bin/bash

if [ -z "$1" ]; then
    exit 1
fi

REPORT_DIR="$1"

if [ ! -d "$REPORT_DIR" ]; then
    exit 1
fi

printf "%-20s %-12s %-12s %-12s %-12s %-12s\n" \
       "Sample" "Total" "Mapped(%)" "Proper(%)" "Singletons(%)" "DiffChr(%)"
echo "========================================================================"

for file in ${REPORT_DIR}/*.flagstat.txt; do
    [ -f "$file" ] || continue
    sample=$(basename "$file" .flagstat.txt)
    total=$(awk 'NR==1{print $1}' "$file")
    mapped_pct=$(grep "mapped (" "$file" | head -n 1 | grep -oP '\(\K[0-9.]+(?=%)')
    proper_pct=$(grep "properly paired" "$file" | grep -oP '\(\K[0-9.]+(?=%)')
    singleton_pct=$(grep "singletons (" "$file" | grep -oP '\(\K[0-9.]+(?=%)')
    diff_chr_pct=$(grep "different chr (mapQ>=5)" "$file" | grep -oP '\(\K[0-9.]+(?=%)')
    [ -z "$mapped_pct" ] && mapped_pct="N/A"
    [ -z "$diff_chr_pct" ] && diff_chr_pct="N/A"
    printf "%-20s %-12s %-12s %-12s %-12s %-12s\n" \
           "$sample" "$total" "$mapped_pct%" "$proper_pct%" "$singleton_pct%" "$diff_chr_pct%"
done