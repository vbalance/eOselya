"""
Cashflow analysis combining credit, rent, and expenses.
"""

import pandas as pd
from config import ModelParameters


def build_cashflow_usd(
    params: ModelParameters,
    credit_df: pd.DataFrame,
    rent_df: pd.DataFrame,
    scenario_name: str = 'base'
) -> pd.DataFrame:
    """
    Build complete cashflow analysis in USD.

    Combines:
    - Rent income (from rent_df)
    - Mortgage payments (from credit_df)
    - Maintenance costs
    - Terminal sale value (in last month)

    Returns DataFrame with columns:
    - Month
    - Rent_USD_nominal
    - Maintenance_USD_nominal
    - Mortgage_Total_USD_nominal
    - NetCF_USD_nominal (before sale)
    - DiscountFactor_USD
    - Rent_USD_real
    - Maintenance_USD_real
    - Mortgage_Total_USD_real
    - NetCF_USD_real (before sale)
    - Sale_USD_nominal (only in last month)
    - Sale_USD_real (only in last month)
    - Total_CF_USD_nominal (including sale)
    - Total_CF_USD_real (including sale)
    """

    # Ensure both DataFrames have the same length
    assert len(credit_df) == len(rent_df), "Credit and rent schedules must have same length"

    # Calculate terminal apartment price
    scenario = params.scenarios[scenario_name]
    terminal_price_usd_nominal = params.apartment_cost_usd * (
        (1 + scenario.price_growth_annual_usd) ** params.loan_term_years
    )

    rows = []

    # Get scenario parameters for FX rate calculation
    monthly_rates = params.get_scenario_monthly_rates(scenario_name)
    inflation_uah_monthly = monthly_rates['inflation_uah_monthly']

    for idx in range(len(credit_df)):
        month = credit_df.iloc[idx]['Month']

        # Rent income (already calculated with proper FX)
        rent_usd_nominal = rent_df.iloc[idx]['Rent_USD_nominal']
        rent_usd_real = rent_df.iloc[idx]['Rent_USD_real']

        # Current FX rate (grows with inflation)
        fx_rate = params.fx_today * ((1 + inflation_uah_monthly) ** (month - 1))

        # Maintenance costs (in UAH, convert to USD at current rate)
        maintenance_uah = params.maintenance_monthly_uah
        maintenance_usd_nominal = maintenance_uah / fx_rate

        # Mortgage payment (in UAH, convert to USD at current rate)
        mortgage_uah = credit_df.iloc[idx]['Total_Mortgage_UAH']
        mortgage_usd_nominal = mortgage_uah / fx_rate

        # Discount factor
        discount_factor = 1 / ((1 + params.usd_discount_annual) ** (month / 12))

        # Real USD values
        maintenance_usd_real = maintenance_usd_nominal * discount_factor
        mortgage_usd_real = mortgage_usd_nominal * discount_factor

        # Net cashflow (before sale)
        net_cf_usd_nominal = rent_usd_nominal - maintenance_usd_nominal - mortgage_usd_nominal
        net_cf_usd_real = rent_usd_real - maintenance_usd_real - mortgage_usd_real

        # Sale (only in last month)
        if month == params.loan_term_months:
            sale_usd_nominal = terminal_price_usd_nominal
            sale_usd_real = terminal_price_usd_nominal * discount_factor
        else:
            sale_usd_nominal = 0.0
            sale_usd_real = 0.0

        # Total cashflow (including sale)
        total_cf_usd_nominal = net_cf_usd_nominal + sale_usd_nominal
        total_cf_usd_real = net_cf_usd_real + sale_usd_real

        rows.append({
            'Month': month,
            'Rent_USD_nominal': rent_usd_nominal,
            'Maintenance_USD_nominal': maintenance_usd_nominal,
            'Mortgage_Total_USD_nominal': mortgage_usd_nominal,
            'NetCF_USD_nominal': net_cf_usd_nominal,
            'DiscountFactor_USD': discount_factor,
            'Rent_USD_real': rent_usd_real,
            'Maintenance_USD_real': maintenance_usd_real,
            'Mortgage_Total_USD_real': mortgage_usd_real,
            'NetCF_USD_real': net_cf_usd_real,
            'Sale_USD_nominal': sale_usd_nominal,
            'Sale_USD_real': sale_usd_real,
            'Total_CF_USD_nominal': total_cf_usd_nominal,
            'Total_CF_USD_real': total_cf_usd_real
        })

    return pd.DataFrame(rows)


def build_all_scenarios_cashflow(
    params: ModelParameters,
    credit_df: pd.DataFrame,
    rent_schedules: dict
) -> dict:
    """Build cashflow for all scenarios"""
    cashflows = {}

    for scenario_name in params.scenarios.keys():
        rent_df = rent_schedules[scenario_name]
        cashflows[scenario_name] = build_cashflow_usd(
            params, credit_df, rent_df, scenario_name
        )

    return cashflows
