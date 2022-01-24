from sqlite3 import Time
from db.assets_db import TimescaleDB


def test_db_creation() -> None:
    db = TimescaleDB()
    assert db


def test_db_connection() -> None:
    db = TimescaleDB()
    db.connect()
    assert db.connection


def test_db_assert_disconnection() -> None:
    db = TimescaleDB()
    db.disconnect()
    assert db
