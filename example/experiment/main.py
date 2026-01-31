import time
import pyarrow as pa


if __name__ == "__main__":
    with pa.OSFile("data/1769783081613/plot_1.arrow", "rb") as source:
        b = source.read_buffer()
        b.to_pybytes()

    # file.close()
