"""Script to populate the assets table."""
import config
import psycopg2
from pgcopy import CopyManager

from quantfin.market.investment_universe import scrape_largest_companies


def populate_assets_table() -> None:
    """This function populates the assets table."""
    assets_df = scrape_largest_companies()
    assets_df["is_etf"] = [False for _ in range(len(assets_df.index))]
    try:
        connection = psycopg2.connect(
            host=config.DB_HOST,
            database=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
        )
        mgr = CopyManager(conn=connection, table="assets", cols=assets_df.columns)
        mgr.copy([row for row in assets_df.itertuples(index=False, name=None)])
        connection.commit()
    except Exception as e:
        print(e)
    finally:
        connection.close()


if __name__ == "__main__":
    populate_assets_table()
