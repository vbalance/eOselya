"""
Financial metrics calculation: NPV, IRR, ROI.
"""

import numpy as np
import pandas as pd
from typing import Dict, Optional, Tuple
from config import ModelParameters


def npv(rate: float, cashflows: np.ndarray) -> float:
    """
    Calculate Net Present Value.

    Args:
        rate: discount rate per period
        cashflows: array of cashflows, cashflows[0] is at t=0

    Returns:
        NPV value
    """
    periods = np.arange(len(cashflows))
    return np.sum(cashflows / (1 + rate) ** periods)


def irr(cashflows: np.ndarray, guess: float = 0.1, max_iter: int = 100, tol: float = 1e-6) -> Optional[float]:
    """
    Calculate Internal Rate of Return using Newton-Raphson method.

    Args:
        cashflows: array of cashflows, cashflows[0] is at t=0
        guess: initial guess for IRR
        max_iter: maximum iterations
        tol: tolerance for convergence

    Returns:
        IRR value or None if not converged
    """
    rate = guess

    for i in range(max_iter):
        # Calculate NPV and derivative
        periods = np.arange(len(cashflows))

        # NPV
        npv_val = np.sum(cashflows / (1 + rate) ** periods)

        # Derivative of NPV with respect to rate
        dnpv = np.sum(-periods * cashflows / (1 + rate) ** (periods + 1))

        if abs(dnpv) < 1e-10:
            return None  # Derivative too small

        # Newton-Raphson step
        rate_new = rate - npv_val / dnpv

        if abs(rate_new - rate) < tol:
            return rate_new

        rate = rate_new

    return None  # Did not converge


def compute_metrics(
    params: ModelParameters,
    cashflow_df: pd.DataFrame,
    scenario_name: str = 'base'
) -> Dict[str, float]:
    """
    Compute all key financial metrics for a scenario.

    Returns dictionary with:
    - Initial_Investment_USD
    - Total_Rent_Collected_USD_nominal
    - Total_Rent_Collected_USD_real
    - Total_Mortgage_Paid_USD_nominal
    - Total_Mortgage_Paid_USD_real
    - Total_Maintenance_USD_nominal
    - Total_Maintenance_USD_real
    - NPV_Real_USD_no_sale
    - Terminal_Price_USD_nominal
    - Terminal_Price_USD_real
    - NPV_Real_USD_with_sale
    - IRR_monthly_USD_with_sale
    - IRR_annual_USD_with_sale
    - ROI_Real_USD_with_sale
    """

    metrics = {}

    # Initial investment (outflow at t=0)
    metrics['Initial_Investment_USD'] = params.own_cash_total_usd

    # Aggregate cashflows
    metrics['Total_Rent_Collected_USD_nominal'] = cashflow_df['Rent_USD_nominal'].sum()
    metrics['Total_Rent_Collected_USD_real'] = cashflow_df['Rent_USD_real'].sum()
    metrics['Total_Mortgage_Paid_USD_nominal'] = cashflow_df['Mortgage_Total_USD_nominal'].sum()
    metrics['Total_Mortgage_Paid_USD_real'] = cashflow_df['Mortgage_Total_USD_real'].sum()
    metrics['Total_Maintenance_USD_nominal'] = cashflow_df['Maintenance_USD_nominal'].sum()
    metrics['Total_Maintenance_USD_real'] = cashflow_df['Maintenance_USD_real'].sum()

    # NPV without sale
    npv_no_sale = -metrics['Initial_Investment_USD'] + cashflow_df['NetCF_USD_real'].sum()
    metrics['NPV_Real_USD_no_sale'] = npv_no_sale

    # Terminal price (sale)
    scenario = params.scenarios[scenario_name]
    terminal_price_nominal = params.apartment_cost_usd * (
        (1 + scenario.price_growth_annual_usd) ** params.loan_term_years
    )
    discount_factor_terminal = 1 / ((1 + params.usd_discount_annual) ** params.loan_term_years)
    terminal_price_real = terminal_price_nominal * discount_factor_terminal

    metrics['Terminal_Price_USD_nominal'] = terminal_price_nominal
    metrics['Terminal_Price_USD_real'] = terminal_price_real

    # NPV with sale
    npv_with_sale = npv_no_sale + terminal_price_real
    metrics['NPV_Real_USD_with_sale'] = npv_with_sale

    # IRR calculation
    # Construct cashflow array: [initial_investment (negative), monthly cashflows, final cashflow + sale]
    cashflows = np.zeros(len(cashflow_df) + 1)
    cashflows[0] = -metrics['Initial_Investment_USD']

    for idx in range(len(cashflow_df)):
        month = idx + 1
        if month == params.loan_term_months:
            # Last month: include sale
            cashflows[month] = cashflow_df.iloc[idx]['Total_CF_USD_nominal']
        else:
            cashflows[month] = cashflow_df.iloc[idx]['NetCF_USD_nominal']

    # Calculate IRR (monthly rate)
    irr_monthly = irr(cashflows, guess=0.01)

    if irr_monthly is not None:
        metrics['IRR_monthly_USD_with_sale'] = irr_monthly
        metrics['IRR_annual_USD_with_sale'] = (1 + irr_monthly) ** 12 - 1
    else:
        metrics['IRR_monthly_USD_with_sale'] = None
        metrics['IRR_annual_USD_with_sale'] = None

    # ROI
    if metrics['Initial_Investment_USD'] > 0:
        metrics['ROI_Real_USD_with_sale'] = npv_with_sale / metrics['Initial_Investment_USD']
    else:
        metrics['ROI_Real_USD_with_sale'] = None

    return metrics


def compute_all_scenarios_metrics(
    params: ModelParameters,
    cashflows: Dict[str, pd.DataFrame]
) -> Dict[str, Dict[str, float]]:
    """Compute metrics for all scenarios"""
    all_metrics = {}

    for scenario_name, cashflow_df in cashflows.items():
        all_metrics[scenario_name] = compute_metrics(params, cashflow_df, scenario_name)

    return all_metrics


def format_metrics_summary(metrics: Dict[str, float]) -> str:
    """Format metrics as readable text summary"""
    lines = []
    lines.append("=" * 60)
    lines.append("FINANCIAL METRICS SUMMARY")
    lines.append("=" * 60)

    lines.append(f"\nInitial Investment: ${metrics['Initial_Investment_USD']:,.2f}")

    lines.append("\n--- Rent Income ---")
    lines.append(f"Total Rent (Nominal USD): ${metrics['Total_Rent_Collected_USD_nominal']:,.2f}")
    lines.append(f"Total Rent (Real USD): ${metrics['Total_Rent_Collected_USD_real']:,.2f}")

    lines.append("\n--- Expenses ---")
    lines.append(f"Total Mortgage Payments (Nominal USD): ${metrics['Total_Mortgage_Paid_USD_nominal']:,.2f}")
    lines.append(f"Total Mortgage Payments (Real USD): ${metrics['Total_Mortgage_Paid_USD_real']:,.2f}")
    lines.append(f"Total Maintenance (Nominal USD): ${metrics['Total_Maintenance_USD_nominal']:,.2f}")
    lines.append(f"Total Maintenance (Real USD): ${metrics['Total_Maintenance_USD_real']:,.2f}")

    lines.append("\n--- NPV (Net Present Value) ---")
    lines.append(f"NPV without Sale (Real USD): ${metrics['NPV_Real_USD_no_sale']:,.2f}")
    lines.append(f"NPV with Sale (Real USD): ${metrics['NPV_Real_USD_with_sale']:,.2f}")

    lines.append("\n--- Terminal Value ---")
    lines.append(f"Apartment Sale Price (Nominal USD): ${metrics['Terminal_Price_USD_nominal']:,.2f}")
    lines.append(f"Apartment Sale Price (Real USD): ${metrics['Terminal_Price_USD_real']:,.2f}")

    lines.append("\n--- Returns ---")
    if metrics['IRR_annual_USD_with_sale'] is not None:
        lines.append(f"IRR (Annual, USD): {metrics['IRR_annual_USD_with_sale']*100:.2f}%")
        lines.append(f"IRR (Monthly, USD): {metrics['IRR_monthly_USD_with_sale']*100:.4f}%")
    else:
        lines.append("IRR: Could not be calculated (no convergence)")

    if metrics['ROI_Real_USD_with_sale'] is not None:
        lines.append(f"ROI (Real USD with Sale): {metrics['ROI_Real_USD_with_sale']*100:.2f}%")
    else:
        lines.append("ROI: N/A")

    lines.append("=" * 60)

    return "\n".join(lines)
