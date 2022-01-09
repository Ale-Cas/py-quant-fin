from source.portfolio import Portfolio


def test_portfolio() -> None:
    ptf = Portfolio()
    assert isinstance(ptf, Portfolio)
