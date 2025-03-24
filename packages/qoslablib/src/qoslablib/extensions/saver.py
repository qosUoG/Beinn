from abc import ABC, abstractmethod
from dataclasses import dataclass

import dataclasses
from typing import Any, Callable, Literal, TypedDict, Unpack, override


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


class SqlSaverManagerABC(ABC):
    # The holder shall manage the database connection, and provide a method that would be consumed bu the SaverABC method

    @classmethod
    @abstractmethod
    def createSqlSaver[T: SqlSaverABC](cls, sql_saverT: type[T], kwargs: Any) -> T:
        # This method returns a plot object
        raise NotImplementedError


@dataclass
class KVSqlSaverConfig(SqlSaverConfigABC):
    type: Literal["KVFloatSqlSaver"]
    title: str
    keys: list[str]

    def toDict(self):
        return dataclasses.asdict(self)


class KVFloatSqlSaver(SqlSaverABC):
    class KW(TypedDict):
        title: str
        keys: list[str]

    def __init__(
        self,
        *,
        save_fn: Callable[[dict[str, float]], None],
        **kwargs: Unpack[KW],
    ):
        self.title = kwargs["title"]
        self.keys = kwargs["keys"]

        self.config = KVSqlSaverConfig(
            type="KVFloatSqlSaver", title=self.title, keys=self.keys
        )

        self._save_fn = save_fn

    @classmethod
    @override
    def kwargs(cls, **kwargs: Unpack[KW]):
        return kwargs

    @override
    def getCreateTableSql(self, table_name: str) -> str:
        return f"""CREATE TABLE "{table_name}" (
            timestamp INTEGER PRIMARY KEY{"".join([f",\n{key} REAL" for key in self.keys])}
            ) """

    @override
    def save(self, frame: dict[str, float]):
        # Fill in Nones for missing keys
        for key in self.keys:
            if key not in frame.keys():
                frame[key] = None

        # Execute the functions
        self._save_fn(frame)

    @override
    def getInsertSql(self, table_name: str):
        return f"""
        INSERT INTO "{table_name}"({"".join([f"{key}," for key in self.keys])}) VALUES({"".join([f":{key}," for key in self.keys])})
    """
