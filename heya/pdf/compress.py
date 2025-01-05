from __future__ import annotations

import os
import sys
import subprocess

from shutil import rmtree


def compress(source: str, target: str, power: int = 0):
    """
    Compress a given PDF file

    :param str source: source PDF file
    :param str target: target location to save the compressed PDF
    :param int power: power of the compression. Default value is 0. This can be 0: default, 1: prepress, 2: printer, 3: ebook, 4: screen
    """

    quality = {
        0: "/default",
        1: "/prepress",
        2: "/printer",
        3: "/ebook",
        4: "/screen",
    }

    if not os.path.isfile(source):
        print("Error: invalid path for input PDF file")
        sys.exit(1)

    if source.split(".")[-1].lower() != "pdf":
        print("Error: input file is not a PDF")
        sys.exit(1)

    subprocess.call(
        [
            "gs",
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            "-dPDFSETTINGS={}".format(quality[power]),
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            "-sOutputFile={}".format(target),
            source,
        ],
    )


def __compress(result, target: str, power: int):
    tmp_dir: str = "./_tmp"
    tmp_file: str = f"{tmp_dir}/tmp.pdf"

    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    with open(tmp_file, "wb") as file:
        file.write(result)

    compress(tmp_file, target, power)
    rmtree(tmp_dir)
