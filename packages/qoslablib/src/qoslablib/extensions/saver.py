from abc import ABC, abstractmethod
from dataclasses import dataclass

import dataclasses

import enum
import time
from typing import Any, Callable, Iterable, Literal, TypedDict, Unpack, override

from aiosqlite import Row


@dataclass
class SqlSaverConfigABC(ABC):
    title: str
    type: str

    @abstractmethod
    def toDict(self) -> dict[str, Any]:
        raise NotImplementedError


@dataclass
class SqlSaverABC(ABC):
    _save_fn: Callable[[dict[str, float]], None]
    config: SqlSaverConfigABC

    @abstractmethod
    def __init__(
        self,
        *,
        save_fn: Callable[[dict[str, float]], None],
        timestamp: int,
        **kwargs: Unpack[Any],
    ):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def kwargs(cls, **kwargs: Any) -> Any:
        # This method creates the kwargs object for instantiating the chart
        raise NotImplementedError

    @abstractmethod
    def save(self, frame) -> None:
        # This method saves one frame of data
        raise NotImplementedError

    @abstractmethod
    def getCreateTableSql(self, table_name: str) -> str:
        # This function returns the string used for the sql creating table
        raise NotImplementedError

    @abstractmethod
    def getInsertSql(self, table_name: str) -> str:
        # This function returns the string used for the sql creating table
        raise NotImplementedError

    @abstractmethod
    def getSelectAllSql(self) -> str:
        # this function returns the sql that fetchs all data for finalize function
        raise NotImplementedError

    @abstractmethod
    def finalize(self, raw: Any) -> Any:
        # this function returns the actual final dataset
        raise NotImplementedError


class SqlSaverManagerABC(ABC):
    # The holder shall manage the database connection, and provide a method that would be consumed bu the SaverABC method

    @classmethod
    @abstractmethod
    def createSqlSaver[T: SqlSaverABC](cls, sql_saverT: type[T], kwargs: Any) -> T:
        # This method returns a plot object
        raise NotImplementedError


@dataclass
class XYFloatSqlSaverConfig(SqlSaverConfigABC):
    type: Literal["XYFloatSqlSaver"]
    title: str
    timestamp: int
    y_names: list[str]

    def toDict(self):
        return dataclasses.asdict(self)


class XYFloatSqlSaver(SqlSaverABC):
    class KW(TypedDict):
        title: str
        y_names: list[str]

    def __init__(
        self,
        *,
        save_fn: Callable[[dict[str, float]], None],
        timestamp: int,
        **kwargs: Unpack[KW],
    ):
        self.title = kwargs["title"]
        self.timestamp = timestamp
        self.table_name = f"{self.title} %ts{timestamp}ts%"
        self.y_names = kwargs["y_names"]

        self.config = XYFloatSqlSaverConfig(
            type="XYFloatSqlSaver",
            title=self.title,
            timestamp=self.timestamp,
            y_names=self.y_names,
        )

        self._save_fn = save_fn

    @classmethod
    @override
    def kwargs(cls, **kwargs: Unpack[KW]):
        return kwargs

    @override
    def getCreateTableSql(self) -> str:
        return f"""CREATE TABLE "{self.table_name}" (
            id INTEGER PRIMARY KEY,
            x REAL NOT NULL,
            {",\n".join([f"{key} REAL" for key in self.y_names])}
            ) """

    @override
    def getSelectAllSql(self) -> str:
        return f'''SELECT id,x,{",".join([f"{key}" for key in self.y_names])} from "{self.table_name}" ORDER BY id DESC'''

    @override
    def finalize(self, raw: Iterable[Row]):
        # Put in the keys of the data, each y_name is a {x: y}, where x and y are pair of values

        stage_1: dict[str, dict[float, float]] = {}

        for y_name in self.y_names:
            stage_1[y_name] = {}

        # The raw is traversed backward, from later in time to earlier in time.
        for row in raw:
            # id = row[0]
            x = row[1]
            # Then the index in the tuple shall match the index of y_name in y_names
            for i, y_name in enumerate(self.y_names):
                # Only put y in if x did not exist
                if x in stage_1[y_name]:
                    continue

                stage_1[y_name][x] = row[i + 2]

        # Convert the dict into a list of {x: float, y:float} such that they can be sorted
        class Value(TypedDict):
            x: float
            y: float

        stage_2: dict[str, list[Value]] = {}
        for y_name in self.y_names:
            stage_2[y_name] = []

        for y_name, values in stage_1.items():
            for x, y in values.items():
                stage_2[y_name].append({"x": x, "y": y})

        # Sort each y_name list by each value's x
        for values in stage_2.values():
            values.sort(key=lambda v: v["x"])

        # Flatten each y_name in to {x: [],y:[]}, where x and y are arrays of values
        class Dataset(TypedDict):
            x: list[float]
            y: list[float]

        res: dict[str, Dataset] = {}

        for y_name, values in stage_2.items():
            res[y_name] = {"x": [], "y": []}
            for value in values:
                res[y_name]["x"].append(value["x"])
                res[y_name]["y"].append(value["y"])

        return res

    @override
    def save(self, frame: dict[str, float]):
        # x is asuumed to exist
        # Fill in Nones for missing y_names
        for key in self.y_names:
            if key not in frame.keys():
                frame[key] = None

        # Execute the functions
        self._save_fn(frame)

    @override
    def getInsertSql(self):
        return f"""
        INSERT INTO "{self.table_name}"(x,{",".join([f"{key}" for key in self.y_names])}) VALUES(:x,{",".join([f":{key}" for key in self.y_names])})
    """
