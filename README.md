# Python Quantitative Finance Framework
The py-quant-fin package is an open-source library which offers an integrated framework for quantitative finance. 

![Tests](https://github.com/Ale-Cas/py-quant-fin/actions/workflows/python-package.yml/badge.svg)

## Features
- Data downloading from different data sources, such as: 
    - Yahoo Finance;
    - Alpaca.

- Calculation of several risk measures, such as:
    - Variance.

- Implementation of several portfolio selection models:
    - Portfolio Optimization models based on Risk-Return tradeoff with the above specified risk measures;
    - Risk Parity (ERC, HRP).

- Backtesting and simulation testing frameworks.

- Automatic trade execution, both in paper and real accounts, with the following brokers:
    - Alpaca.  

## Development
To set up the developer environment, run the following commands:
```
git clone https://github.com/Ale-Cas/py-quant-fin.git
pip install poetry
poetry install
```
