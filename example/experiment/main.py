import os
import pickle


if __name__ == "__main__":
    filename = "./data/testing.pickle"
    data = {"data": "wow"}
    datas: list[dict[str, str]] = [data]

    if not os.path.isfile(filename):
        with open(filename, "wb") as f:
            pickle.dump(datas, f)

    # Read the past data
    with open(filename, "rb") as f:
        datas = pickle.load(f)

    datas.append(data)

    with open(filename, "wb") as f:
        pickle.dump(datas, f)

    with open(filename, "rb") as f:
        print(pickle.load(f))
