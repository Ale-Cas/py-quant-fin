"""Script to populate the assets table."""
import config
import psycopg2
from pgcopy import CopyManager
import pandas as pd
import yfinance as yf


def populate_prices_table() -> None:
    """This function populates the prices table."""
    create_prices_table_sql = """CREATE TABLE IF NOT EXISTS prices (
    assets_id INTEGER NOT NULL,
    time TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    ticker text NULL,
    open double precision NULL,
    low double precision NULL,
    high double precision NULL,
    close double precision NULL,
    volume NUMERIC NULL,
    market_cap double precision NULL,
    PRIMARY KEY (assets_id, time),
    CONSTRAINT fk_assets FOREIGN KEY (assets_id) REFERENCES assets(id)
);"""
    sql_query = """SELECT id, ticker FROM assets"""
    try:
        connection = psycopg2.connect(
            host=config.DB_HOST,
            database=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
        )
        cur = connection.cursor()
        cur.execute(create_prices_table_sql)
        cur.execute(query=sql_query)
        rows = cur.fetchall()
        for id, ticker in rows[:100]:
            yfticker = yf.Ticker(ticker)
            prices = yfticker.history(period="max", auto_adjust=False)
            prices["assets_id"] = id
            prices["ticker"] = ticker
            prices.index = prices.index.date
            prices.index = prices.index.rename("time")
            prices = prices.rename(
                columns={
                    "Open": "open",
                    "Close": "close",
                    "High": "high",
                    "Low": "low",
                    "Volume": "volume",
                }
            )
            prices = prices.drop(["Adj Close", "Dividends", "Stock Splits"], axis=1)
            try:
                for row in prices.itertuples(index=True, name=None):
                    cur.execute(
                        """INSERT INTO prices (time, open, high, low, close, volume, assets_id, ticker)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
                        row,
                    )
            except psycopg2.errors.UniqueViolation:
                pass
            except psycopg2.errors.InFailedSqlTransaction:
                connection.rollback()
            except Exception as e:
                print(str(e.__class__) + str(e) + " when inserting")
        # mgr = CopyManager(conn=connection, table="prices", cols=prices.columns)
        # mgr.copy([row for row in prices.itertuples(index=True, name=None)])
        connection.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        cur.close()
        connection.close()


if __name__ == "__main__":
    populate_prices_table()
