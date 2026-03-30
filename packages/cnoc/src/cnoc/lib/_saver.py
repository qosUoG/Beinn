from typing import Any, Callable, Coroutine, Mapping, cast

import numpy as np
import pyarrow as pa
from websockets import ServerConnection


def _TypedDict2Schema(schema: type[Mapping[str, object]]) -> pa.Schema:
    schema_fields: list[pa.Field[Any]] = []
    for column_name, column_type in schema.__annotations__.items():
        # Array of float
        if column_type == np.typing.NDArray[np.float64] or column_type == list[float]:
            schema_fields.append(pa.field(column_name, pa.float64()))
        # Array of int
        elif column_type == np.typing.NDArray[np.int64] or column_type == list[int]:
            schema_fields.append(pa.field(column_name, pa.int64()))
        else:
            raise TypeError(f"Unsupported type: {column_type}")

    return pa.schema(schema_fields)


def _TypedDict2Columns(schema: type[Mapping[str, object]]) -> list[str]:
    columns: list[str] = []
    for column_name, column_type in schema.__annotations__.items():
        # Array of number
        if (
            (column_type == np.typing.NDArray[np.float64])
            or (column_type == list[float])
            or (column_type == np.typing.NDArray[np.int64])
            or (column_type == list[int])
        ):
            columns.append(column_name)

        else:
            raise TypeError(f"Unsupported type of key {column_name}: {column_type}")

    return columns


class _PyArrow:
    def __init__(self, schema: pa.Schema):
        self._sink = pa.BufferOutputStream()
        self._stream = pa.ipc.new_stream(self._sink, schema)
        self._closed = False

    def write_batch(self, batch: pa.RecordBatch):
        self._stream.write_batch(batch)

    def close(self):
        if self._closed:
            return
        self._closed = True
        self._stream.close()
        self._sink.close()

    def getvalue(self) -> bytes:
        self._closed = True
        return self._sink.getvalue().to_pybytes()


class Saver[T: Mapping[str, object]]:
    def __init__(
        self,
        dir: str,
        title: str,
        schema: type[T],
        run_coroutine_threadsafe: Callable[[Coroutine[Any, Any, Any]], None],
    ):
        self._schema = _TypedDict2Schema(schema)

        self._file_path = f"{dir}/{title}.arrow"

        self._osfile = pa.OSFile(self._file_path, "wb")
        self._file_writer = pa.ipc.new_file(self._osfile, self._schema)

        self._ws: ServerConnection | None = None

        self.config = {
            "title": title,
            "columns": _TypedDict2Columns(schema),
        }
        self._run_coroutine_threadsafe = run_coroutine_threadsafe

    def save(self, data: T):
        batch = pa.RecordBatch.from_pydict(
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

        self._run_coroutine_threadsafe(self._save(batch))

    async def _save(self, batch: pa.RecordBatch):
        # Write to disk
        self._file_writer.write_batch(batch)

        # Plot the data
        await self._plot(batch)

    def _subscribe(self, ws: ServerConnection) -> None:
        self._ws = ws
        self._sent_history = False

    def _unsubscribe(self) -> None:
        self._ws = None

    async def _plot(self, batch: pa.RecordBatch) -> None:
        if self._ws is None:
            return

        if not self._sent_history:
            self._file_writer.close()
            self._osfile.close()

            with pa.ipc.open_file(self._file_path) as source:
                table = source.read_all()
                sink = pa.BufferOutputStream()
                stream = pa.ipc.new_stream(sink, self._schema)
                stream.write_table(table)
                await self._ws.send(sink.getvalue().to_pybytes())

            self._osfile = pa.OSFile(self._file_path, "wb")
            self._file_writer = pa.ipc.new_file(self._osfile, self._schema)
            self._file_writer.write_table(table)

            self._sent_history = True
            return

        snapshot = _PyArrow(self._schema)

        snapshot.write_batch(batch)

        await self._ws.send(snapshot.getvalue())

        snapshot.close()

    def close(self):
        self._file_writer.close()
        self._osfile.close()
