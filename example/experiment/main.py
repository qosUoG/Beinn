import os
import pickle
import pprint


if __name__ == "__main__":
    filename = "./data/ExampleSqlSaver.pickle"

    with open(filename, "rb") as f:
        pprint.pprint(pickle.load(f))
