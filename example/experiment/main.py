from ctypes import cast
from dataclasses import dataclass, field, fields
from enum import Enum
from typing import Any


class ee(Enum):
    a = 1
    b = 2
    c = 3


def main():
    e = ee.a

    print(e.__class__.__members__.keys())


if __name__ == "__main__":
    main()
