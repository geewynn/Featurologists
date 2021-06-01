import glob
import logging
import os
from pathlib import Path

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor


logging.basicConfig(level=logging.INFO)

CURRENT_DIR = Path(__file__).parent


def collect_nbs(d: Path):
    return [Path(p) for p in glob.glob(f"{d}/**/*.ipynb")]


def process_nb(nb: Path, timeout: int = 600, metadata=None):
    logging.info(f"Processing {nb}")
    with nb.open("r") as f:
        nb_text = nbformat.read(f, as_version=4)
    ep = ExecutePreprocessor(timeout=timeout)
    old_cwd = os.getcwd()
    try:
        os.chdir(nb.parent)
        ep.preprocess(nb_text, metadata)
    finally:
        os.chdir(old_cwd)


def process_all_nbs(d: Path):
    logging.info(f"Processing all notebooks in {CURRENT_DIR}")
    for nb in collect_nbs(d):
        process_nb(nb)


if __name__ == "__main__":
    process_all_nbs(CURRENT_DIR)
