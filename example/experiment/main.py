from ctypes import cast
from dataclasses import asdict, dataclass, field, fields


@dataclass
class Nested:
    x: int = field(default=0)


@dataclass
class Parent:
    nested: Nested = field(default_factory=Nested)


def main():
    p = Parent()

    print(asdict(p))


if __name__ == "__main__":
    main()
