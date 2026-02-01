from dataclasses import dataclass
import json
import os
import time
import pyarrow as pa
from cnoc import P, p


if __name__ == "__main__":
    # with pa.OSFile("data/1769783081613/plot_1.arrow", "rb") as source:
    #     b = source.read_buffer()
    #     b.to_pybytes()

    # if not os.path.exists("metadata.json"):
    with open("metadata.json", "w+") as f:
        json.dump({"wow": "hohoho"}, f)

    original_data = None

    with open("metadata.json", "r") as f:
        original_data = json.load(f)

    with open("metadata.json", "w") as f:
        original_data["shit"] = "shitshit"
        json.dump(original_data, f)

    with open("metadata.json", "r") as f:
        original_data = json.load(f)
        print(original_data)
