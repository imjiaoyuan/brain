#!/usr/bin/env python3
import os
import subprocess
import shutil
import argparse
from pathlib import Path

def main(args):
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not shutil.which("datasets"):
        print("Error: 'datasets' command not found. Please install it, e.g., with conda: 'conda install conda-forge::ncbi-datasets-cli'", file=os.sys.stderr)
        return

    genome_ids = []
    input_path = Path(args.input)
    if input_path.is_file():
        with input_path.open('r') as f:
            genome_ids = [line.strip() for line in f if line.strip()]
    else:
        genome_ids.append(args.input)

    if not genome_ids:
        print("Error: No accession IDs provided.", file=os.sys.stderr)
        return

    include_opts = ["genome"]
    if args.protein:
        include_opts.append("protein")
    if args.gff:
        include_opts.append("gff3")
    include_str = ",".join(include_opts)

    for accession_id in genome_ids:
        zip_file = output_dir / f"{accession_id}.zip"
        cmd = [
            "datasets", "download", "genome", "accession", accession_id,
            "--include", include_str, "--filename", str(zip_file)
        ]
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            if shutil.which("unzip"):
                unzip_dir = output_dir / accession_id
                subprocess.run(["unzip", "-oq", str(zip_file), "-d", str(unzip_dir)], check=True)
                os.remove(zip_file)
        except subprocess.CalledProcessError as e:
            print(f"Failed: {accession_id} | {e.stderr.strip()}", file=os.sys.stderr)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True, help="A single accession ID or path to a text file with one ID per line.")
    parser.add_argument("-o", "--output", required=True, help="Output directory for downloaded files.")
    parser.add_argument("--protein", action="store_true", help="Download protein sequences.")
    parser.add_argument("--gff", action="store_true", help="Download GFF3 annotation files.")
    args = parser.parse_args()
    main(args)