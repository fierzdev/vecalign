import argparse
import subprocess
import csv
import sys
from io import StringIO

import vecalign.vecalign


def read_file(folder, file):
    with open(folder + '/' + file) as f:
        return f.read()


def align_mappings(tgt_embed, src_embed, src_folder, tgt_folder, mapping_file):
    with open(mapping_file) as f:
        mappings = [line for line in csv.reader(f)]
    for src_file, tgt_file in mappings:
        cmd = f"python3 vecalign.py -s {src_folder}/{src_file} -t {tgt_folder}/{tgt_file} --tgt_embed {tgt_embed} {tgt_embed}.vec.npy --src_embed {src_embed} {src_embed}.vec.npy"
        alignments = subprocess.check_output(cmd.split(" "))
        content = read_file(src_folder, src_file).splitlines()
        content2 = read_file(tgt_folder, tgt_file).splitlines()
        for alignment in alignments.decode().splitlines():
            print(alignment)
            alignment = alignment.split(":")[:-1]
            for i, cont in zip(alignment, (content, content2)):
                indices = eval(i)
                for ix in indices:
                    print(cont[ix], end=" ")
                print("")
            print("----")


def align_mappings_to_moses(tgt_embed, src_embed, src_folder, tgt_folder, mapping_file, out_src, out_tgt):
    out_files = [open(out_src, 'w+', encoding='utf-8'), open(out_tgt, 'w+', encoding='utf-8')]
    with open(mapping_file, encoding='utf-8') as f:
        mappings = [line for line in csv.reader(f)]
    for src_file, tgt_file in mappings:
        output = vecalign.vecalign.align([f'{src_folder}/{src_file}'], [f'{tgt_folder}/{tgt_file}'], (f'{src_embed}', f'{src_embed}.vec.npy'), (f'{tgt_embed}', f'{tgt_embed}.vec.npy'))
        #cmd = f"python3 vecalign.py -s {src_folder}/{src_file} -t {tgt_folder}/{tgt_file} --tgt_embed {tgt_embed} {tgt_embed}.vec.npy --src_embed {src_embed} {src_embed}.vec.npy"
        #alignments = subprocess.check_output(cmd.split(" ")).decode().splitlines()
        output.seek(0)
        alignments = output.read().splitlines()
        content = read_file(src_folder, src_file).splitlines()
        content2 = read_file(tgt_folder, tgt_file).splitlines()
        unmatched = 0
        for alignment in alignments:
            alignment = alignment.split(":")[:-1]
            if alignment[0] == "[]" or alignment[1] == "[]":  # If segment could not be aligned
                unmatched += 1
            else:  # only write out aligned segments --> we do not want hallucinations
                for file_ix, (i, cont) in enumerate(zip(alignment, (content, content2))):
                    indices = eval(i)
                    space = False
                    for ix in indices:
                        if space:
                            out_files[file_ix].write(" ")  # space between two segments on same line
                        out_files[file_ix].write(cont[ix])
                        space = True
                    out_files[file_ix].write("\n")  # newline after segement is done
        # Only accept files with less than 30% unmatched lines
        if not unmatched / len(alignments) > 0.3:
            out_files[0].write("@@ENDOFDOC@@\n")
            out_files[1].write("@@ENDOFDOC@@\n")
    for file in out_files:
        try:
            file.close()
        except Exception:
            print("Problems closing file")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("tgt_embed")
    parser.add_argument("src_embed")
    parser.add_argument("src_folder")
    parser.add_argument("target_folder")
    parser.add_argument("mapping")
    parser.add_argument("--out-src", dest="out_src", default=None)
    parser.add_argument("--out-tgt", dest="out_tgt", default=None)
    args = parser.parse_args()
    if args.out_src:
        align_mappings_to_moses(args.tgt_embed, args.src_embed, args.src_folder, args.target_folder, args.mapping,
                                args.out_src, args.out_tgt)
    else:
        align_mappings(args.tgt_embed, args.src_embed, args.src_folder, args.target_folder, args.mapping)
