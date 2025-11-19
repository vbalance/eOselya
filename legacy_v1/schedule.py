"""
Schedule building functions for credit and rent.
"""

import pandas as pd
from typing import Dict
from config import ModelParameters


def build_credit_schedule(params: ModelParameters) -> pd.DataFrame:
    """
    Build differentiated credit payment schedule.

    Returns DataFrame with columns:
    - Month: 1 to loan_term_months
    - Balance_Start_UAH: loan balance at start of month
    - Principal_UAH: principal payment (constant)
    - Interest_UAH: interest payment (declining)
    - Insurance_UAH: insurance payment (constant)
    - Total_Mortgage_UAH: total monthly payment
    - Balance_End_UAH: loan balance at end of month

    Note: USD conversion is done in cashflow.py with current FX rates
    """

    rows = []
    balance = params.loan_amount_uah

    for month in range(1, params.loan_term_months + 1):
        balance_start = balance

        # Fixed principal payment
        principal = params.principal_monthly

        # Interest on remaining balance
        interest = balance_start * params.interest_monthly

        # Insurance (constant, based on apartment cost)
        insurance = params.insurance_monthly_uah

        # Total mortgage payment
        total_mortgage_uah = principal + interest + insurance

        # Update balance
        balance_end = balance_start - principal
        balance = balance_end

        rows.append({
            'Month': month,
            'Balance_Start_UAH': balance_start,
            'Principal_UAH': principal,
            'Interest_UAH': interest,
            'Insurance_UAH': insurance,
            'Total_Mortgage_UAH': total_mortgage_uah,
            'Balance_End_UAH': balance_end
        })

    return pd.DataFrame(rows)


def build_rent_schedule(params: ModelParameters, scenario_name: str = 'base') -> pd.DataFrame:
    """
    Build rent schedule with growth.

    Returns DataFrame with columns:
    - Month: 1 to loan_term_months
    - Rent_UAH: rent in UAH (growing)
    - FX_rate: USD/UAH exchange rate (growing with UAH inflation)
    - Rent_USD_nominal: rent in USD at current exchange rate
    - Rent_USD_real: rent in real USD (discounted)
    """

    monthly_rates = params.get_scenario_monthly_rates(scenario_name)
    rent_growth_monthly = monthly_rates['rent_growth_monthly']
    inflation_uah_monthly = monthly_rates['inflation_uah_monthly']

    rows = []

    for month in range(1, params.loan_term_months + 1):
        # Rent grows monthly
        # Month 1: initial rent
        # Month m: initial * (1 + growth)^(m-1)
        rent_uah = params.rent_initial_uah * ((1 + rent_growth_monthly) ** (month - 1))

        # FX rate grows with UAH inflation
        # Month 1: initial rate
        # Month m: initial * (1 + inflation)^(m/12) [converted to years]
        fx_rate = params.fx_today * ((1 + inflation_uah_monthly) ** (month - 1))

        # Convert to USD (nominal) using current FX rate
        rent_usd_nominal = rent_uah / fx_rate

        # Discount to real USD
        discount_factor = 1 / ((1 + params.usd_discount_annual) ** (month / 12))
        rent_usd_real = rent_usd_nominal * discount_factor

        rows.append({
            'Month': month,
            'Rent_UAH': rent_uah,
            'FX_rate': fx_rate,
            'Rent_USD_nominal': rent_usd_nominal,
            'Rent_USD_real': rent_usd_real
        })

    return pd.DataFrame(rows)


def build_all_scenarios_rent_schedule(params: ModelParameters) -> Dict[str, pd.DataFrame]:
    """Build rent schedules for all scenarios"""
    return {
        scenario_name: build_rent_schedule(params, scenario_name)
        for scenario_name in params.scenarios.keys()
    }
