from abc import ABC, abstractmethod
from dataclasses import dataclass

from typing import Any, Callable, TypedDict, Unpack, override


@dataclass
class SqlSaverABC(ABC):
    _initialize_fn: Callable[[], None]
    _save_fn: Callable[[dict[str, float]], None]

    def initialize(self) -> None:
        self._initialize_fn()

    @classmethod
    @abstractmethod
    def kwargs[KW](cls, **kwargs: Unpack[KW]) -> KW:
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


class SqlSaverHolderABC(ABC):
    # The holder shall manage the database connection, and provide a method that would be consumed bu the SaverABC method

    @classmethod
    @abstractmethod
    def createSqlSaver[T: SqlSaverABC](cls, sql_saverT: type[T], kwargs: Any) -> T:
        # This method returns a plot object
        raise NotImplementedError


class XYSqlSaver(SqlSaverABC):
    class Config(TypedDict):
        title: str
        x_name: str
        y_names: list[str]

    class KW(TypedDict):
        title: str
        x_name: str
        y_names: list[str]

    title: str
    x_name: str
    y_names: list[str]
    config: Config

    def __init__(
        self,
        save_fn: Callable[[dict[str, float]], None],
        initialize_fn: Callable[[dict[str, float]], None],
        **kwargs: Unpack[KW],
    ):
        self.title = kwargs["title"]
        self.x_name = kwargs["x_name"]
        self.y_names = kwargs["y_names"]

        self.config = {
            "title": self.title,
            "x_name": self.x_name,
            "y_names": self.y_names,
        }

        self._save_fn = save_fn
        self._initialize_fn = initialize_fn

    @classmethod
    @override
    def kwargs(cls, **kwargs: Unpack[KW]):
        return kwargs

    @override
    def getCreateTableSql(self, table_name: str) -> str:
        return f"""CREATE TABLE "{table_name}" (
            timestamp INTEGER PRIMARY KEY,
            {self.x_name} REAL,
            {"".join([f",\n{y_name} REAL" for y_name in self.y_names])}
            ) """

    @override
    def save(self, frame: dict[str, float]):
        # Fill in Nones for missing keys
        for y_name in self.y_names:
            if y_name not in frame.keys():
                frame[y_name] = None

        # Execute the functions
        self._save_fn(frame)

    @override
    def getInsertSql(self, table_name: str):
        return f"""
        INSERT INTO "{table_name}" VALUES(:{self.x_name},{"".join([f":{y_name}," for y_name in self.y_names])})
    """
