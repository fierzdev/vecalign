import os
import pathlib

from typer import Typer

from vecalign.align import align_mappings_to_moses
import vecalign.overlap

app = Typer()

@app.command()
def align(embeddings_src: str, embeddings_trg: str, files_src: str, files_trg: str, mapping: str, outfile_src: str, outfile_trg: str):
    """
    args:
    embeddings_src: str --> Embeddings files with overlapped embeddings for source
    embeddings_trg: str --> Embeddings files with overlapped embeddings for target
    files_src: str --> Folder containing files with source language
    files_trg: str --> Folder containing files with target language
    mapping: str --> File with mappings from source to target files (aligned documents)
    outfile_src: str --> Moses file to write source
    outfile_trg: str --> Moses file to write target
    """
    align_mappings_to_moses(embeddings_src, embeddings_trg, files_src, files_trg, mapping, outfile_src, outfile_trg)


@app.command()
def create_overlap_files(infolder: str, outfile: str, num_overlaps=4):
    """
    args:
    infolder: str --> Folder with files to create overlaps for
    outfile: str --> Write overlaps to this file
    num_overlaps: int --> Maximum number of allowed overlaps.
    """
    vecalign.overlap.go(outfile, [os.path.join(infolder, x) for x in os.listdir(infolder) if "_filtered" in x and pathlib.Path(os.path.join(infolder, x)).is_file()], num_overlaps=num_overlaps)
