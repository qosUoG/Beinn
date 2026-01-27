from datetime import datetime
import json
import os
from typing import Any, Mapping, TypedDict, cast
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

from ._utils import DataclassInstance
from ._params import AllParamSaveType, params2Save


class Metadata:
    def __init__(self, dir: str):
        self._dir = dir

    @property
    def params(self) -> DataclassInstance:
        return self.params

    @params.setter
    def _(self, params: DataclassInstance):
        self.params = params
        self._saveMetadata()

    @property
    def note(self) -> str:
        return self.note

    @note.setter
    def _(self, note: str):
        self.note = note
        self._saveMetadata()

    def _saveMetadata(self):
        with open(dir + "/" + "metadata.json", "w") as f:
            f.write(
                json.dumps(
                    {"params": json.dumps(params2Save(self.params)), "note": self.note}
                )
            )


class Saver[T: Mapping[str, object]]:
    def __init__(self, dir: str, key: str, params: DataclassInstance, schema: type[T]):
        self.dir = dir
        self.path = key.replace(" ", "_") + ".parquet"

        # path = str(int(datetime.now().timestamp() * 1000))

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

        self._writer = pq.ParquetWriter(
            "data/" + self.dir + "/" + self.path, pa.schema(self.schema_fields)
        )

        self.metadata = Metadata(self._writer)
        self.metadata.params = params

    def save(self, data: T):
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

    def close(self):
        self._writer.close()
