from dataclasses import dataclass
import json
import os
import time
import pyarrow as pa
from cnoc import P, p


if __name__ == "__main__":
    with pa.ipc.open_file(f"./data/{1771265921836}/plot_1.arrow") as reader:
        df1 = reader.read_pandas()

        print(df1)
