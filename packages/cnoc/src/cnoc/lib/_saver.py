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

    def write_batch(self, batch: pa.RecordBatch):
        self._stream.write_batch(batch)

    def close(self):
        self._stream.close()
        self._sink.close()

    def getvalue(self) -> bytes:
        return bytes(self._sink.getvalue().to_pybytes())


class Saver[T: Mapping[str, object]]:
    def __init__(
        self,
        dir: str,
        title: str,
        schema: type[T],
        run_coroutine_threadsafe: Callable[[Coroutine[Any, Any, Any]], None],
    ):
        self._schema = _TypedDict2Schema(schema)

        self._history = _PyArrow(self._schema)

        self._file = pa.ipc.new_file(f"{dir}/{title}.arrow", self._schema)

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

        self._run_coroutine_threadsafe(self._save(batch))  # pyright: ignore[reportPrivateUsage]

    async def _save(self, batch: pa.RecordBatch):
        # Write to history
        self._history.write_batch(batch)

        # Write to disk
        self._file.write_batch(batch)

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
            await self._ws.send(self._history.getvalue())
            self._sent_history = True
            return

        snapshot = _PyArrow(self._schema)
        snapshot.write_batch(batch)
        await self._ws.send(snapshot.getvalue())
        snapshot.close()

    def close(self):
        self._history.close()
        self._file.close()
