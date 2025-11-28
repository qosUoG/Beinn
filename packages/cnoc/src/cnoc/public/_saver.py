from datetime import datetime
import json
import os
from typing import Any, Mapping, TypedDict, cast
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

from ._utils import DataclassInstance
from ._params import AllParamSaveType, params2Save


class Metadata(TypedDict):
    time: int
    params: dict[str, AllParamSaveType | dict[str, AllParamSaveType]]
    note: str
    # columns: list[str]


class Saver[T: Mapping[str, object]]:
    def __init__(self, key: str, params: DataclassInstance, schema: type[T]):
        # All space characters are replaced with underscores
        key = key.replace(" ", "_")

        self.params = params

        # Find the maximum existing subscript for this path
        maximum = -1
        for existing_key in os.listdir("data"):
            existing_key = existing_key.replace(".parquet", "")

            if not existing_key.startswith(key):
                continue

            # Without any number subscripts
            if existing_key == key:
                maximum = max(maximum, 0)
                continue

            # Parse the number after the path
            maybe_number: int
            try:
                maybe_number = int(existing_key.replace(key, ""))
            except ValueError:
                # If not a number, then it is not the same path
                continue

            maximum = max(maybe_number, maximum)

        if maximum >= 0:
            self.path = f"{key}{maximum + 1}.parquet"
        else:
            self.path = key + ".parquet"

        self._note = ""

        # Construct the schema object from Typeddict
        self.schema_fields: list[pa.Field[Any]] = []
        for column_name, column_type in schema.__annotations__.items():
            if (
                column_type == np.typing.NDArray[np.float64]
                or column_type == list[float]
            ):
                self.schema_fields.append(pa.field(column_name, pa.float64()))
            elif column_type == np.typing.NDArray[np.int64] or column_type == list[int]:
                self.schema_fields.append(pa.field(column_name, pa.int64()))
            else:
                raise TypeError(f"Unsupported type: {column_type}")

    def initWriter(self):
        if hasattr(self, "_writer"):
            return
        self._writer = pq.ParquetWriter(
            "data/" + self.path, pa.schema(self.schema_fields)
        )

        self._writer.add_key_value_metadata(
            {
                "time": str(int(datetime.now().timestamp() * 1000)),
                "params": json.dumps(params2Save(self.params)),
                "note": "",
                "experiment_metadata": "",
            }
        )

    def save(self, data: T):
        self.initWriter()
        self._writer.write(
            pa.RecordBatch.from_pydict(
                cast(
                    Mapping[
                        str,
                        list[int]
                        | list[float]
                        | np.typing.NDArray[np.float64]
                        | np.typing.NDArray[np.int64],
                    ],
                    data,
                )
            )
        )

    def saveNote(self, note: str):
        self.initWriter()
        self._writer.add_key_value_metadata({"note": note})

    def saveMetadata(self, key: str, value: Any):
        self.initWriter()
        self._writer.add_key_value_metadata({key: json.dumps(value)})

    def close(self):
        if not hasattr(self, "_writer"):
            return
        self._writer.close()
