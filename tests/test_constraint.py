from quantfin.portfolio_selection.portfolio_optimization.constraints import (
    ConstraintType,
    NoShortSelling,
    Constraints,
)


def test_no_shortselling() -> None:
    no_short = NoShortSelling(num_assets=1)
    assert no_short


def test_constraints() -> None:
    cons = Constraints([])
