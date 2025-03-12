from abc import ABC, abstractmethod
from dataclasses import dataclass

from typing import Callable, TypedDict, Unpack, override


@dataclass
class SqlSaverABC(ABC):
    _initialize_fn: Callable[[], None]
    _save_fn: Callable[[dict[str, float]], None]

    @abstractmethod
    def kwargs[KW](self, **kwargs: Unpack[KW]) -> KW:
        # This method creates the kwargs object for instantiating the chart
        raise NotImplementedError

    @abstractmethod
    def save(self, frame) -> None:
        # This method saves one frame of data
        raise NotImplementedError

    @abstractmethod
    def getConfig(self):
        # This function returns the config of the saver
        raise NotImplementedError

    @abstractmethod
    def getColumnsDefinition(self) -> str:
        # This function returns the string used for the sql creating table
        raise NotImplementedError

    @abstractmethod
    def initialize(self) -> None:
        self._initialize_fn()


class SqlSaverHolderABC(ABC):
    # The holder shall manage the database connection, and provide a method that would be consumed bu the SaverABC method

    @classmethod
    @abstractmethod
    def createSqlSaver[T: SqlSaverABC, KW](cls, sql_saverT: T, kwargs: KW) -> T:
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

    def __init__(
        self,
        save_fn: Callable[[dict[str, float]], None],
        initialize_fn: Callable[[dict[str, float]], None],
        **kwargs: Unpack[KW],
    ):
        self.title = kwargs.title
        self.x_name = kwargs.x_name
        self.y_names = kwargs.y_names

        self.config: XYSqlSaver.Config = {
            "title": self.title,
            "x_name": self.x_name,
            "y_names": self.y_names,
        }

        self._save_fn = save_fn
        self._initialize_fn = initialize_fn

    @override
    def kwargs(self, **kwargs: Unpack[KW]):
        return kwargs

    @override
    def getConfig(self) -> Config:
        return self.config

    @override
    def getColumnsDefinition(self) -> str:
        res = "timestamp INTEGER PRIMARY KEY"
        res += f",\n{self.x_name} REAL"
        for y_name in self.y_names:
            res += f",\n{y_name} REAL"

        return res

    @override
    def save(self, frame: dict[str, float]):
        self._save_fn(frame)
