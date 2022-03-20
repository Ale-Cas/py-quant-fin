from typing import Dict, List

import numpy as np
import pandas as pd
import scipy.cluster.hierarchy as sch

from quantfin.market.investment_universe import InvestmentUniverse
from quantfin.portfolio_selection.portfolio import OptimalPortfolio
from quantfin.portfolio_selection.strategy import PortfolioSelectionModel


class RiskParity(PortfolioSelectionModel):
    pass


class HierarchicalRiskParity(RiskParity):
    def __init__(
        self,
        investment_universe: InvestmentUniverse,
    ) -> None:
        super().__init__()
        self.investment_universe = investment_universe

    def tree_clustering(self) -> np.ndarray:
        dist = ((1 - self.investment_universe.returns.corr()) / 2) ** 0.5
        link: np.ndarray = sch.linkage(dist, "single")
        return link

    def quasi_diagonalization(self) -> List[int]:
        link = self.tree_clustering().astype(int)
        sort_index = pd.Series([link[-1, 0], link[-1, 1]])
        num_items = link[-1, 3]
        while sort_index.max() >= num_items:
            sort_index.index = range(0, sort_index.shape[0] * 2, 2)
            df0 = sort_index[sort_index >= num_items]
            i = df0.index
            j = df0.values - num_items
            sort_index[i] = link[j, 0]
            df0 = pd.Series(link[j, 1], index=i + 1)
            sort_index = sort_index.append(df0)
            sort_index = (
                sort_index.sort_index()
            )  # re-sort sortIx.index=range(sortIx.shape[0]) # re-index
        return sort_index.tolist()

    def get_inverse_variance_ptf(self) -> np.ndarray:
        """Compute the inverse variance portfolio."""
        ivp = 1.0 / np.diag(self.investment_universe.returns.cov())
        ivp /= ivp.sum()
        return ivp

    def get_cluster_variance(self, cluster_items: int):
        """Compute variance per cluster."""
        cov_: np.ndarray = self.investment_universe.returns.cov().loc[
            cluster_items, cluster_items
        ]
        w_: np.ndarray = self.get_inverse_variance_ptf(cov_).reshape(-1, 1)
        cluster_variance = np.dot(np.dot(w_.T, cov_), w_)[0, 0]
        return cluster_variance

    def recursive_bisection(self) -> Dict[str, float]:
        # Compute HRP alloc
        w = pd.Series(1, index=self.quasi_diagonalization())
        cluster_items = [
            self.quasi_diagonalization()
        ]  # initialize all items in one cluster while len(cluster_items)>0:
        cluster_items = [
            i[j:k]
            for i in cluster_items
            for j, k in ((0, len(i) / 2), (len(i) / 2, len(i)))
            if len(i) > 1
        ]  # bi-section
        for i in range(0, len(cluster_items), 2):  # parse in pairs
            cluster_items0 = cluster_items[i]  # cluster 1
            cluster_items1 = cluster_items[i + 1]  # cluster 2
            cVar0 = self.get_cluster_variance(cluster_items0)
            cVar1 = self.get_cluster_variance(cluster_items1)
            alpha = 1 - cVar0 / (cVar0 + cVar1)
            w[cluster_items0] *= alpha  # weight 1 w[cluster_items1]*=1-alpha # weight 2
        return w.to_dict()

    def compute_optimal_portfolio(self) -> OptimalPortfolio:
        return OptimalPortfolio(
            name="Hierarchical Risk Parity",
            holdings=self.recursive_bisection(),
            assets_returns=self.investment_universe.returns,
        )
