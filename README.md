# Python Quantitative Finance Framework
The py-quant-fin library is an open-source quantitative finance framework. 

![Tests](https://github.com/Ale-Cas/py-quant-fin/actions/workflows/python-package.yml/badge.svg)

## TODO:
- Min CVaR
- Frontend input-output
- Refactoring assets module
- Expected return constraint
- Max instrument weight constraint
- CDaR
- Risk parity:
    - ERC
    - HRP

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
