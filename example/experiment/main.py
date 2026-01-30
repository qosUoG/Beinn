import time
import pyarrow as pa


if __name__ == "__main__":
    file = pa.ipc.new_file(
        "data.arrow",
        pa.schema([pa.field("x", pa.float64()), pa.field("y", pa.float64())]),
    )
    file.write_batch(
        pa.RecordBatch.from_pydict({"x": [1.0, 2.0, 3.0], "y": [4.0, 5.0, 6.0]})
    )

    rfile = pa.OSFile("data.arrow", "rb")
    b = rfile.read()
    rfile.close()

    time.sleep(1)

    # file.close()
