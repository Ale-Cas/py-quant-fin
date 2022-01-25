"""This module implements tools to interact with TimescaleDB."""
from abc import ABC, abstractmethod
from typing import List, Union, Dict

import psycopg2
import pandas as pd

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

    def connect(self) -> None:
        """Open the connection with the db object and instantiate cursor."""
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                database=self.name,
                user=self.user,
                password=self.password,
            )
            self.cursor = self.connection.cursor()
        except psycopg2.OperationalError:
            print("Error: Invalid credentials.")

    def disconnect(self) -> None:
        """Close the connection with the db object and cursor."""
        try:
            self.connection.close()
        except AttributeError:
            print("""You must be connected to the database to disconnect from it.""")

    def get_tickers(
        self,
        n_ids: int = 50,
    ) -> List[str]:
        """Gets tickers from the assets table.

        Parameters
        ----------
        n_ids:
            Limit for the number of ids to retrieve.
            The ids are ordered by market_cap.

        Returns
        -------
            A list of tickers.
        """
        query = f"""SELECT ticker FROM assets 
            LIMIT {n_ids};"""
        self.cursor.execute(query)
        return [x for (x,) in self.cursor.fetchall()]

    def get_prices(
        self, tickers: Union[str, List[str]]
    ) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
        """Gets prices from the prices table."""
        if isinstance(tickers, str) or len(tickers) == 1:
            query = f"""SELECT "time", open, low, high, close 
            FROM prices 
            WHERE assets_id = (SELECT id FROM assets 
            WHERE ticker = '{tickers}');"""
            self.cursor.execute(query)
            cols = ["time", "open", "low", "high", "close"]
            prices: pd.DataFrame = pd.DataFrame(self.cursor.fetchall(), columns=cols)
            prices = prices.set_index("time")
            prices = prices.sort_index()
        else:
            prices: Dict = {}
            cols = ["time", "open", "low", "high", "close"]
            for ticker in tickers:
                query = f"""SELECT "time", open, low, high, close 
                FROM prices 
                WHERE assets_id = (SELECT id FROM assets 
                WHERE ticker = '{ticker}');"""
                self.cursor.execute(query)
                prices[ticker] = pd.DataFrame(self.cursor.fetchall(), columns=cols)
                prices[ticker] = prices[ticker].set_index("time")
                prices[ticker] = prices[ticker].sort_index()
        return prices
