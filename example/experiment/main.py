from typing import TypedDict


class SaverRowType(TypedDict):
    index: list[int]
    t1: list[float]
    t2: list[float]
    t3: list[float]
    i2: list[int]


def main():
    print(list(SaverRowType.__annotations__.values())[1].__args__[0] is float)


if __name__ == "__main__":
    main()
