"""Script to populate the assets table."""
import config
import psycopg2
from pgcopy import CopyManager

from quantfin.market.investment_universe import scrape_largest_companies


def populate_assets_table() -> None:
    """This function populates the assets table."""
    create_table_sql = """CREATE TABLE IF NOT EXISTS assets (
                            id SERIAL PRIMARY KEY,
                            ticker TEXT NOT NULL,
                            name TEXT NOT NULL,
                            exchange TEXT NULL,
                            country TEXT NULL,
                            is_etf BOOLEAN NOT NULL,
                            UNIQUE(ticker)
                        );"""
    assets_df = scrape_largest_companies()
    assets_df["is_etf"] = [False for _ in range(len(assets_df.index))]
    try:
        connection = psycopg2.connect(
            host=config.DB_HOST,
            database=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
        )
        cur = connection.cursor()
        cur.execute(create_table_sql)
        mgr = CopyManager(conn=connection, table="assets", cols=assets_df.columns)
        mgr.copy([row for row in assets_df.itertuples(index=False, name=None)])
        connection.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        cur.close()
        connection.close()


if __name__ == "__main__":
    populate_assets_table()
