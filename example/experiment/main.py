from dataclasses import dataclass
import json
import time
from typing import Any, TypedDict

from cnoc import P, p
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import pyarrow as pa

from cnoc.public._params import params2Save

from cnoc.public.saver import Reader


class SaverRowType(TypedDict):
    index: list[int]
    t1: list[float]
    t2: list[float]
    t3: np.typing.NDArray[np.float64]
    i2: list[int]


@dataclass
class Params:
    strparam: P.Str = p.str("wowow")


def main():
    # params = Params()

    # schema_fields: list[pa.Field[Any]] = []
    # for column_name, column_type in SaverRowType.__annotations__.items():
    #     if column_type == np.typing.NDArray[np.float64] or column_type == list[float]:
    #         schema_fields.append(pa.field(column_name, pa.float64()))
    #     elif column_type == np.typing.NDArray[np.int64] or column_type == list[int]:
    #         schema_fields.append(pa.field(column_name, pa.int64()))
    #     else:
    #         raise TypeError(f"Unsupported type: {column_type}")

    # start_time = time.perf_counter()

    # print("crate table from df", time.perf_counter() - start_time)
    # start_time = time.perf_counter()

    # pqwriter = pq.ParquetWriter("data/wow.parquet", pa.schema(schema_fields))

    # print("crate parquet writer", time.perf_counter() - start_time)
    # start_time = time.perf_counter()

    # pqwriter.write(
    #     pa.RecordBatch.from_pydict(
    #         {
    #             "index": [1, 2, 3],
    #             "t1": np.array([1.1, 2.2, 3.3]),
    #             "t2": [1.1, 2.2, 3.3],
    #             "t3": [1.1, 2.2, 3.3],
    #             "i2": [13, 14, 15],
    #         }
    #     )
    # )
    # pqwriter.write(
    #     pa.RecordBatch.from_pydict(
    #         {
    #             "index": [1, 2, 3],
    #             "t1": [1.1, 2.2, 3.3],
    #             "t2": [1.1, 2.2, 3.3],
    #             "t3": [1.1, 2.2, 3.3],
    #             "i2": [13, 14, 15],
    #         }
    #     )
    # )
    # pqwriter.write(
    #     pa.RecordBatch.from_pydict(
    #         {
    #             "index": [1, 2, 3],
    #             "t1": [1.1, 2.2, 3.3],
    #             "t2": [1.1, 2.2, 3.3],
    #             "t3": [1.1, 2.2, 3.3],
    #             "i2": [16, 17, 18],
    #         }
    #     )
    # )

    # pqwriter.add_key_value_metadata({"params": json.dumps(params2Save(params))})
    # pqwriter.add_key_value_metadata({"params2": json.dumps(params2Save(params))})
    # pqwriter.add_key_value_metadata({"notes": str(3)})

    # print("write_table three times", time.perf_counter() - start_time)
    # start_time = time.perf_counter()

    # pqwriter.close()

    # print("close parquet writer", time.perf_counter() - start_time)
    # start_time = time.perf_counter()

    # res = pd.read_parquet("data/PI_Spec3.parquet")

    # print(res)

    # print("read parquet", time.perf_counter() - start_time)
    # start_time = time.perf_counter()

    # print(res)

    # metadata = pq.read_metadata("data/wow.parquet").metadata[b"notes"]
    # print(int(metadata))
    # saver.saver.saveNote("wowow")

    print(type(json.dumps(3)))


if __name__ == "__main__":
    main()
