import json
import sys
from traceback import print_tb
from typing import cast

from .utils import Runtime
import h5py

runtime = Runtime()


def main():
    try:
        f = h5py.File("data.h5", "r")
        dataset_key = sys.argv[1]

        print(f[dataset_key].values())

        f.close()

    except Exception as e:
        runtime.printErr(f"Error: {e}")
        _, _, traceback = sys.exc_info()
        print_tb(traceback, file=sys.stderr)
        runtime.errFlush()

    runtime.end()
