from datetime import datetime
import os
from typing import Any, Mapping, TypedDict
import pyarrow as pa  # pyright: ignore[reportMissingTypeStubs]
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

        # Find the maximum existing subscript for this path
        maximum = -1
        for existing_key in os.listdir("data"):
            existing_key = existing_key.replace(".arrow", "")

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
            self.path = f"{key}{maximum + 1}.arrow"
        else:
            self.path = key + ".arrow"

        self._metadata: Metadata = {
            "time": int(datetime.now().timestamp() * 1000),
            "params": params2Save(params),
            "note": "",
            # "columns": list(tuple(inspect.get_annotations(type).keys())),
        }

        self._sink = pa.OSFile("data/" + self.path, "wb")

        # Construct the schema object from Typeddict
        schema_fields: list[pa.Field[Any]] = []
        for column_name, column_type in schema.__annotations__.items():
            schema_fields.append(
                pa.field(
                    column_name,
                    pa.int64() if column_type.__args__[0] is int else pa.float64(),
                )
            )

        self._writer: pa.RecordBatchFileWriter = pa.ipc.new_file(
            self._sink,
            pa.schema(schema_fields),
            metadata=self._metadata,  # type: ignore
        )

    def save(self, data: T):
        self._writer.write_batch(pa.RecordBatch.from_pydict(data))  # type: ignore

    def saveNote(self, note: str):
        self._metadata["note"] = note
        self._writer.write_batch(pa.RecordBatch(), self._metadata)  # type: ignore

    def close(self):
        self._writer.close()
        self._sink.close()
