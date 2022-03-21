"""
This package provides different portfolio selection strategies that 
were implemented following the Strategy design pattern.

The user should only use the context, which is the PortfolioBuilder class.
In the strategy module the abstract strategy interface is provided, 
while the concrete strategies are implemented in portfolio_optimization and risk_parity modules.

"""
import os
import platform

if platform.system() == "Darwin" and "arm64" in platform.mac_ver():
    os.system("/usr/bin/arch -x86_64 /bin/zsh")
