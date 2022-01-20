CREATE TABLE public.prices (
    "time" timestamp NOT NULL,
    ticker text NULL,
    open double precision NULL,
    close double precision NULL,
    low double precision NULL,
    high double precision NULL,
    volume int NULL,
);

CREATE EXTENSION IF NOT EXISTS timescaledb;

SELECT create_hypertable('prices', 'time');