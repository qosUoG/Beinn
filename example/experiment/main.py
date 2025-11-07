from dataclasses import asdict, dataclass, field
from typing import cast

from examplelib.ExampleDriver import ExampleEquipment, Params

from cnoc.public._params import params2Dict


@dataclass
class Nested:
    x: int = field(default=0)


@dataclass
class Parent:
    nested: Nested = field(default_factory=Nested)


def main():
    print(ExampleEquipment.params.__dict__)


if __name__ == "__main__":
    main()
