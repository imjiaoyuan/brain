import argparse
import os
import sys
from pyfaidx import Fasta
import gffutils
from tqdm import tqdm
from collections import defaultdict

def get_args():
    parser = argparse.ArgumentParser(
        description="Translate a genome to protein sequences using a reference genome and a GFF/GTF annotation file."
    )
    parser.add_argument(
        'fasta',
        help='Absolute path to the reference genome FASTA file.'
    )
    parser.add_argument(
        'annotation',
        help='Absolute path to the gene annotation GFF/GTF file.'
    )
    parser.add_argument(
        'output',
        help='Absolute path for the output protein FASTA file.'
    )
    parser.add_argument(
        '--id_attribute',
        default='ID',
        help='The attribute key in the parent gene feature to use for the protein FASTA header. Defaults to "ID".'
    )
    return parser.parse_args()

def reverse_complement(dna):
    complement = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A', 'N': 'N'}
    return "".join(complement.get(base, 'N') for base in reversed(dna.upper()))

def translate_dna(sequence):
    gencode = {
        'ATA':'I', 'ATC':'I', 'ATT':'I', 'ATG':'M',
        'ACA':'T', 'ACC':'T', 'ACG':'T', 'ACT':'T',
        'AAC':'N', 'AAT':'N', 'AAA':'K', 'AAG':'K',
        'AGC':'S', 'AGT':'S', 'AGA':'R', 'AGG':'R',
        'CTA':'L', 'CTC':'L', 'CTG':'L', 'CTT':'L',
        'CCA':'P', 'CCC':'P', 'CCG':'P', 'CCT':'P',
        'CAC':'H', 'CAT':'H', 'CAA':'Q', 'CAG':'Q',
        'CGA':'R', 'CGC':'R', 'CGG':'R', 'CGT':'R',
        'GTA':'V', 'GTC':'V', 'GTG':'V', 'GTT':'V',
        'GCA':'A', 'GCC':'A', 'GCG':'A', 'GCT':'A',
        'GAC':'D', 'GAT':'D', 'GAA':'E', 'GAG':'E',
        'GGA':'G', 'GGC':'G', 'GGG':'G', 'GGT':'G',
        'TCA':'S', 'TCC':'S', 'TCG':'S', 'TCT':'S',
        'TTC':'F', 'TTT':'F', 'TTA':'L', 'TTG':'L',
        'TAC':'Y', 'TAT':'Y', 'TAA':'_', 'TAG':'_',
        'TGC':'C', 'TGT':'C', 'TGA':'_', 'TGG':'W',
    }
    protein = []
    i = 0
    while i + 2 < len(sequence):
        codon = sequence[i:i+3]
        amino_acid = gencode.get(codon, 'X')
        if amino_acid == '_':
            break
        protein.append(amino_acid)
        i += 3
    return "".join(protein)

def main():
    args = get_args()

    fasta_path = args.fasta
    annotation_path = args.annotation
    output_path = args.output

    if not all(os.path.isabs(p) for p in [fasta_path, annotation_path, output_path]):
        print("Error: All file paths must be absolute.", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(fasta_path):
        print(f"Error: FASTA file not found at {fasta_path}", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(annotation_path):
        print(f"Error: Annotation file not found at {annotation_path}", file=sys.stderr)
        sys.exit(1)
    
    db_path = annotation_path + '.db'
    db = None 

    try:
        print("Loading reference genome...")
        genome = Fasta(fasta_path, sequence_always_upper=True)

        print("Creating/loading annotation database (this may take a while for large files)...")
        try:
            db = gffutils.FeatureDB(db_path, keep_order=True)
        except ValueError:
            db = gffutils.create_db(
                annotation_path,
                dbfn=db_path,
                force=True,
                keep_order=True,
                merge_strategy='merge',
                sort_attribute_values=True,
                disable_infer_transcripts=True,
                disable_infer_genes=True
            )

        print("Preprocessing CDS features for performance...")
        cds_by_parent = defaultdict(list)
        for cds in tqdm(db.features_of_type('CDS'), desc="Grouping CDS"):
            for parent_id in cds.attributes.get('Parent', []):
                cds_by_parent[parent_id].append(cds)
        
        print("Translating coding sequences...")
        with open(output_path, 'w') as outfile:
            feature_types = ['mRNA', 'transcript']
            transcript_iterator = None
            feature_type_to_use = None
            
            for feature_type in feature_types:
                count = db.count_features_of_type(feature_type)
                if count > 0:
                    transcript_iterator = db.features_of_type(feature_type, order_by='start')
                    feature_type_to_use = feature_type
                    total_transcripts = count
                    break
            
            if not transcript_iterator:
                print(f"Error: No 'mRNA' or 'transcript' features found in {annotation_path}", file=sys.stderr)
                sys.exit(1)
            
            for transcript in tqdm(transcript_iterator, total=total_transcripts, desc=f"Processing {feature_type_to_use}s"):
                try:
                    cds_exons = cds_by_parent.get(transcript.id)
                    if not cds_exons:
                        continue
                    
                    cds_exons.sort(key=lambda x: x.start)
                    cds_sequence = "".join([genome[cds.chrom][cds.start-1:cds.end].seq for cds in cds_exons])

                    if transcript.strand == '-':
                        cds_sequence = reverse_complement(cds_sequence)

                    if not cds_sequence:
                        continue
                    
                    protein = translate_dna(cds_sequence)

                    if protein:
                        protein_id = transcript.id
                        try:
                            parents = list(db.parents(transcript, featuretype='gene'))
                            if parents and args.id_attribute in parents[0].attributes:
                                protein_id = parents[0].attributes[args.id_attribute][0]
                        except Exception:
                            pass
                        
                        outfile.write(f">{protein_id}\n")
                        for i in range(0, len(protein), 60):
                            outfile.write(protein[i:i+60] + '\n')

                except KeyError as e:
                    print(f"\nWarning: Chromosome {e} not found in FASTA file for transcript {transcript.id}. Skipping.", file=sys.stderr)
                    continue
                except Exception as e:
                    print(f"\nWarning: Could not process transcript {transcript.id}. Reason: {e}. Skipping.", file=sys.stderr)
                    continue

        print(f"\nTranslation complete. Protein sequences saved to {output_path}")

    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        if db and hasattr(db, 'conn'):
            db.conn.close() 

        if os.path.exists(db_path):
             try:
                os.remove(db_path)
             except OSError as e:
                print(f"Error removing database file {db_path}: {e}", file=sys.stderr)


if __name__ == '__main__':
    main()