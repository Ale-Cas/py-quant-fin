CREATE TABLE IF NOT EXISTS assets (
    id SERIAL PRIMARY KEY,
    ticker TEXT NOT NULL,
    name TEXT NOT NULL,
    exchange TEXT NULL,
    country TEXT NULL,
    is_etf BOOLEAN NOT NULL,
    UNIQUE(ticker)
);


CREATE TABLE prices (
    assets_id INTEGER NOT NULL,
    time timestamp WITHOUT TIME ZONE NOT NULL,
    ticker text NULL,
    open double precision NULL,
    low double precision NULL,
    high double precision NULL,
    close double precision NULL,
    volume int NULL,
    market_cap double precision NULL,
    PRIMARY KEY (assets_id, time),
    CONSTRAINT fk_assets FOREIGN KEY assets_id REFERENCES assets(id)
);
CREATE INDEX ON prices (stock_id, dt DESC);
CREATE EXTENSION IF NOT EXISTS timescaledb;

SELECT create_hypertable('prices', 'time');