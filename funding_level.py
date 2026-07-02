import numpy as np
import pandas as pd

##############################################################################################
# Section 1 - Assumptions:
##############################################################################################

# Equity
Expected_annual_equity_return = 0.075
Equity_volatility = 0.18

# Bond
Exepected_annual_bond_return = 0.037
Bond_volatility = 0.09

# cash
Cash_return = 0.033

# Inflation 
Expected_inflation = 0.025
Inflation_volatility = 0.015

# Discount rate
Starting_discount_rate = 0.045
Long_run_discount_rate = 0.045
Discount_rate_volatility = 0.012
Mean_reversion_speed = 0.08

# Python list containing variables above 
VARIABLES = ["equity" , "bond" , "inflation" , "discount_rate"]

# Correlation matrix
CORRELATION_MATRIX = [
    [  1.00 ,  0.15, -0.10 ,  0.10  ],
    [  0.15 ,  1.00, -0.40 , -0.70  ],
    [ -0.10 , -0.40 , 1.00 ,  0.50  ],
    [  0.10 , -0.70 , 0.50 ,  1.00  ]
]

##############################################################################################
# Section 2 - Generate correlated shocks:
##############################################################################################

def generate_correlated_shocks(n_sims, n_years, seed = None):
    rng = np.random.default_rng(seed)
    corr_matrix = np.array(CORRELATION_MATRIX)
    L = np.linalg.cholesky(corr_matrix)
    independent_shocks = rng.standard_normal( (n_sims , n_years, 4) ) # array of size sims x years x 4 (which is #vars)
    return independent_shocks @ L.T

##############################################################################################
# Section 3 - Turn shocks into actual economic value
##############################################################################################

def simulate_economic_scenarios( n_sims, n_years, seed=None):
    # call shocks
    shocks = generate_correlated_shocks(n_sims, n_years, seed)
    
    # slice each of the 4 variables out: equity, bonds, inflation, discount rate
    
    equity_shock = shocks[:, :, 0] # all years, all sims, only equity shocks
    bond_shock = shocks[:, :, 1] # all years, all sims, only bond shocks
    inflation_shock = shocks[:, :, 2] # all years, all sims, only inflation shocks
    discount_rate_shock = shocks[:, :, 3] # all years, all sims, only discount rate shocks

    # Compute returns and inflation using: value = mean +volatility * shock
    
    equity_returns = Expected_annual_equity_return + Equity_volatility * equity_shock
    bond_returns = Exepected_annual_bond_return + Bond_volatility * bond_shock
    inflation = Expected_inflation + Inflation_volatility * inflation_shock

    # Discount rate ( has more complexities)
    discount_rates = np.zeros((n_sims, n_years))
    prev_rate = np.full(n_sims, Starting_discount_rate)

    for t in range(n_years):
        drift = Mean_reversion_speed * (Long_run_discount_rate - prev_rate)
        prev_rate = prev_rate + drift + Discount_rate_volatility * discount_rate_shock[:, t] 
        discount_rates[: , t] =prev_rate

    # Compute rate changes
    starting_rates = np.full((n_sims, 1), Starting_discount_rate)
    all_rates = np.hstack([starting_rates, discount_rates])
    rate_changes = np.diff(all_rates, axis=1)

    return {
    "equity_returns": equity_returns,
    "bond_returns": bond_returns,
    "inflation": inflation,
    "discount_rates": discount_rates,
    "rate_changes": rate_changes,
}

##############################################################################################
# Section 4 - Project assets:
##############################################################################################

def project_assets(starting_assets, asset_allocation, scenarios):
# scenarios = simulate_economic_scenarios, the other two are inputs float and dict

    n_sims, n_years = scenarios["equity_returns"].shape

    # Compute portfolio return
    portfolio_return = (
        asset_allocation.get("equity", 0) * scenarios["equity_returns"]
      + asset_allocation.get("bond",   0) * scenarios["bond_returns"]
      + asset_allocation.get("cash", 0) * Cash_return   # deterministic for cash
    )

    # Loop through years, to grow the asset  value

    assets = np.zeros((n_sims, n_years))
    prev = np.full(n_sims, float(starting_assets))

    for t in range(n_years):
       prev = prev * (1 + portfolio_return[:, t])
       assets[:, t] = prev

    return assets

##############################################################################################
# Section 5 - Project liabilities:
##############################################################################################

def project_liabilities(starting_liabilities, liability_duration, scenarios):
    n_sims, n_years = scenarios["inflation"].shape

    liabilities = np.zeros((n_sims, n_years))
    prev = np.full(n_sims, float(starting_liabilities))

    for t in range(n_years):
        inflation_t   = scenarios["inflation"][:, t]
        rate_change_t = scenarios["rate_changes"][:, t]
        prev = prev * (1 + inflation_t) * np.exp(-liability_duration * rate_change_t)
        liabilities[:, t] = prev

    return liabilities

##############################################################################################
# Section 6 - Run the full simulation and summarise 
##############################################################################################

def run_simulation(starting_assets, starting_liabilities, asset_allocation, liability_duration,
                    n_years=20, n_sims=1000, seed=None):
    
    scenarios = simulate_economic_scenarios(n_sims, n_years, seed)
    assets = project_assets(starting_assets, asset_allocation, scenarios)
    liabilities = project_liabilities(starting_liabilities, liability_duration, scenarios)

    funding_level = assets / liabilities

    years = np.arange(1, n_years + 1)
    percentile_table = pd.DataFrame({
       "year": years,
       "p10": np.percentile(funding_level, 10, axis=0),
       "p50": np.percentile(funding_level, 50, axis=0),
       "p90": np.percentile(funding_level, 90, axis=0),
   })
    
    return {
        "funding_level": funding_level,
        "percentile_table": percentile_table,
        "assets": assets,
        "liabilities": liabilities,
    }

results = run_simulation(
    starting_assets=80_000_000,
    starting_liabilities=100_000_000,
    asset_allocation={"equity": 0.5, "bond": 0.4, "cash": 0.1},
    liability_duration=15.0,
    n_years=20,
    n_sims=2000,
    seed=42,
)
print(results["percentile_table"])