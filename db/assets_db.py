"""This module implements tools to interact with TimescaleDB."""
from abc import ABC, abstractmethod

import config


class DataBase(ABC):
    """This abstract class implements tools to interact with a database."""

    def __init__(
        self,
        host: str,
        name: str,
        user: str,
        password: str,
        db_type: str,
    ) -> None:
        self.host = host
        self.name = name
        self.user = user
        self.password = password
        self.db_type = db_type

    @abstractmethod
    def connect(self) -> None:
        pass

    @abstractmethod
    def disconnect(self) -> None:
        pass


class TimescaleDB(DataBase):
    """This class implements tools to interact with TimescaleDB."""

    def __init__(
        self,
        host: str = config.DB_HOST,
        name: str = config.DB_NAME,
        user: str = config.DB_USER,
        password: str = config.DB_PASSWORD,
    ) -> None:
        super().__init__(
            host,
            name,
            user,
            password,
            db_type="TimescaleDB",
        )
