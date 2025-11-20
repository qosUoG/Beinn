from dataclasses import dataclass
from typing import TypedDict

from cnoc import P, p, Saver


class SaverRowType(TypedDict):
    index: list[int]
    t1: list[float]
    t2: list[float]
    t3: list[float]
    i2: list[int]


@dataclass
class Params:
    strparam: P.Str


def main():
    params = Params(strparam=p.str("wowow"))
    saver = Saver[SaverRowType]("temp_data", params, SaverRowType)

    saver.save(
        {
            "index": [1, 2, 3],
            "t1": [1.1, 2.2, 3.3],
            "t2": [1.1, 2.2, 3.3],
            "t3": [1.1, 2.2, 3.3],
            "i2": [1, 2, 3],
        }
    )

    saver.saver.saveNote("wowow")


if __name__ == "__main__":
    main()
