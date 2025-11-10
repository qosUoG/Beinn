import json
import sys
from traceback import print_tb
from typing import cast

from .utils import Runtime
import h5py

runtime = Runtime()


def main():
    f: h5py.File | None = None
    try:
        f = h5py.File("data.h5", "r+")
        dataset_key = sys.argv[1]

        metadata = json.loads(cast(str, f[dataset_key].attrs["metadata"]))
        metadata["note"] = sys.argv[2]
        f[dataset_key].attrs["metadata"] = json.dumps(metadata)

    except Exception as e:
        runtime.printErr(f"Error: {e}")
        _, _, traceback = sys.exc_info()
        print_tb(traceback, file=sys.stderr)
        runtime.errFlush()

    if f:
        f.close()
    runtime.end()
