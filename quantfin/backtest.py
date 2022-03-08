"""
This module implements a framework to backtest strategies.
"""

from quantfin.utils import ListEnum


class RebalanceFrequency(ListEnum):
    """List of available rebalance frequencies."""

    B = "Business Day"
    W = "Weekly"
    SMS = "Semi-Month Start"
    M = "Month End"
    BMS = "Business Month Start"
    BM = "Business Month End"
    BQ = "Business Quarter End"
    BQS = "Business Quarter Start"
    BY = "Business Year End"
    BYS = "Business Year Start"


# class Backtest:
#     """Class to perform a backtest."""

#     def __init__(
#         self,
#         optimization_problem: OptimizationModel,
#         investment_universe: InvestmentUniverse,
#         start_date: Union[str, pd.Timestamp, date] = str(
#             (pd.Timestamp.today() - pd.DateOffset(years=1)).date()
#         ),
#         end_date: Union[str, pd.Timestamp, date] = str(pd.Timestamp.today().date()),
#         learning_period: Union[pd.DateOffset, pd.Timedelta] = pd.DateOffset(
#             years=2, months=0, weeks=0, days=0
#         ),
#         rebalance_freq: Optional[str] = None,
#         num_rebalancements: Optional[int] = None,
#         rebalance_dates: Optional[Union[List[pd.Timestamp], pd.DatetimeIndex]] = None,
#     ) -> None:
#         """Initialize the backtest object by specifying
#         a portfolio optimization problem and an investment universe.
#         The default start_date for the backtest is 1 year ago and the default end_date is today.
#         Either specify a rebalance frequency or a number of rebalancements, otherwise the default
#         rebalance frequency is at the beginning of each month.
#         The default learning period is 2 years.
#         """
#         self.optimization_problem = optimization_problem
#         self.investment_universe = investment_universe
#         self.start_date = start_date
#         self.end_date = end_date
#         self.learning_period = learning_period
#         self.rebalance_freq = rebalance_freq
#         self.num_rebalancements = num_rebalancements
#         if not self.rebalance_freq and not self.num_rebalancements:
#             self.rebalance_freq = RebalanceFrequency.BMS.name
#         if self.rebalance_freq:
#             self.rebalance_dates = rebalance_dates or pd.date_range(
#                 self.start_date, self.end_date, freq=self.rebalance_freq
#             )
#         if self.num_rebalancements:
#             self.rebalance_dates = rebalance_dates or pd.date_range(
#                 self.start_date, self.end_date, periods=self.num_rebalancements
#             )

#     def _set_backtest_universe(self) -> None:
#         self.investment_universe.get_returns(
#             start=(self.start_date - self.learning_period), end=self.end_date
#         )

#     def run(self) -> None:
#         """Run the backtest."""
#         for date in self.rebalance_dates:
#             print(date.date())
