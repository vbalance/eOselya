import pandas as pd
import numpy as np
from typing import Dict, List, Any
from app.models import InvestmentInput, ScenarioParameters

# --- SCHEDULE BUILDERS ---

def build_credit_schedule(params: InvestmentInput) -> pd.DataFrame:
    """
    Build credit payment schedule (Differentiated or Annuity).
    """
    rows = []
    balance = params.loan_amount_uah
    monthly_rate = params.interest_monthly
    term_months = params.loan_term_months
    
    # Annuity payment calculation
    annuity_payment = 0.0
    if params.payment_type == 'annuity' and monthly_rate > 0:
        annuity_payment = balance * (monthly_rate * (1 + monthly_rate)**term_months) / ((1 + monthly_rate)**term_months - 1)
    elif params.payment_type == 'annuity' and monthly_rate == 0:
        annuity_payment = balance / term_months

    for month in range(1, term_months + 1):
        balance_start = balance
        
        # Interest
        interest = balance_start * monthly_rate
        
        # Principal
        if params.payment_type == 'differentiated':
            principal = params.loan_amount_uah / term_months
        else: # annuity
            principal = annuity_payment - interest
            
        # Insurance (constant)
        insurance = (params.apartment_cost_uah * params.insurance_annual) / 12
        
        # Total Payment
        total_mortgage_uah = principal + interest + insurance
        
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

def build_rent_schedule(params: InvestmentInput, scenario: ScenarioParameters) -> pd.DataFrame:
    """
    Build rent schedule with growth.
    """
    rent_growth_monthly = (1 + scenario.rent_growth_annual) ** (1/12) - 1
    inflation_uah_monthly = (1 + scenario.inflation_uah_annual) ** (1/12) - 1
    
    rows = []
    
    for month in range(1, params.loan_term_months + 1):
        # Rent grows monthly
        rent_uah = params.rent_initial_uah * ((1 + rent_growth_monthly) ** (month - 1))
        
        # FX rate grows with UAH inflation
        fx_rate = params.fx_today * ((1 + inflation_uah_monthly) ** (month - 1))
        
        # Convert to USD
        rent_usd_nominal = rent_uah / fx_rate
        
        # Discount
        discount_factor = 1 / ((1 + params.usd_discount_annual) ** (month / 12))
        rent_usd_real = rent_usd_nominal * discount_factor
        
        rows.append({
            'Month': month,
            'Rent_UAH': rent_uah,
            'FX_rate': fx_rate,
            'Rent_USD_nominal': rent_usd_nominal,
            'Rent_USD_real': rent_usd_real,
            'DiscountFactor_USD': discount_factor
        })
        
    return pd.DataFrame(rows)

# --- CASHFLOW BUILDER ---

def build_cashflow(params: InvestmentInput, credit_df: pd.DataFrame, rent_df: pd.DataFrame, scenario: ScenarioParameters) -> pd.DataFrame:
    """
    Build complete cashflow analysis.
    """
    # Terminal value
    terminal_price_usd_nominal = params.apartment_cost_usd * (
        (1 + scenario.price_growth_annual_usd) ** params.loan_term_years
    )
    
    rows = []
    
    for idx in range(len(credit_df)):
        month = credit_df.iloc[idx]['Month']
        
        # Rent
        rent_usd_nominal = rent_df.iloc[idx]['Rent_USD_nominal']
        rent_usd_real = rent_df.iloc[idx]['Rent_USD_real']
        fx_rate = rent_df.iloc[idx]['FX_rate']
        discount_factor = rent_df.iloc[idx]['DiscountFactor_USD']
        
        # Amortization (Maintenance)
        # Logic: Annual Amortization = Rent_Monthly * Coeff
        # Monthly Amortization = (Rent_Monthly * Coeff) / 12
        # We use current month's rent for calculation to scale with rent growth
        amortization_uah = (rent_df.iloc[idx]['Rent_UAH'] * params.amortization_coefficient) / 12
        amortization_usd_nominal = amortization_uah / fx_rate
        amortization_usd_real = amortization_usd_nominal * discount_factor
        
        # Mortgage
        mortgage_uah = credit_df.iloc[idx]['Total_Mortgage_UAH']
        mortgage_usd_nominal = mortgage_uah / fx_rate
        mortgage_usd_real = mortgage_usd_nominal * discount_factor
        
        # Net CF
        net_cf_usd_nominal = rent_usd_nominal - amortization_usd_nominal - mortgage_usd_nominal
        net_cf_usd_real = rent_usd_real - amortization_usd_real - mortgage_usd_real
        
        # Sale
        if month == params.loan_term_months:
            sale_usd_nominal = terminal_price_usd_nominal
            sale_usd_real = terminal_price_usd_nominal * discount_factor
        else:
            sale_usd_nominal = 0.0
            sale_usd_real = 0.0
            
        total_cf_usd_nominal = net_cf_usd_nominal + sale_usd_nominal
        total_cf_usd_real = net_cf_usd_real + sale_usd_real
        
        # Property Value (for chart)
        price_growth_monthly = (1 + scenario.price_growth_annual_usd) ** (1/12) - 1
        property_value_usd = params.apartment_cost_usd * ((1 + price_growth_monthly) ** month)

        rows.append({
            'Month': month,
            'Rent_USD_nominal': rent_usd_nominal,
            'Amortization_USD_nominal': amortization_usd_nominal,
            'Mortgage_USD_nominal': mortgage_usd_nominal,
            'NetCF_USD_nominal': net_cf_usd_nominal,
            'Rent_USD_real': rent_usd_real,
            'Amortization_USD_real': amortization_usd_real,
            'Mortgage_USD_real': mortgage_usd_real,
            'NetCF_USD_real': net_cf_usd_real,
            'Sale_USD_nominal': sale_usd_nominal,
            'Sale_USD_real': sale_usd_real,
            'Total_CF_USD_nominal': total_cf_usd_nominal,
            'Total_CF_USD_real': total_cf_usd_real,
            'Property_Value_USD': property_value_usd
        })
        
    return pd.DataFrame(rows)

# --- METRICS ---

import numpy_financial as npf

def calculate_irr(cashflows: np.ndarray) -> float | None:
    """Calculate IRR using numpy_financial"""
    try:
        irr = npf.irr(cashflows)
        if np.isnan(irr) or np.isinf(irr):
            return None
        return float(irr)
    except:
        return None

def compute_metrics(params: InvestmentInput, cashflow_df: pd.DataFrame) -> Dict[str, Any]:
    """Compute financial metrics"""
    
    initial_investment = params.downpayment_usd + params.extra_purchase_costs_usd
    
    # NPV
    npv_real_no_sale = -initial_investment + cashflow_df['NetCF_USD_real'].sum()
    npv_real_with_sale = -initial_investment + cashflow_df['Total_CF_USD_real'].sum()
    
    # IRR
    cf_array = np.zeros(len(cashflow_df) + 1)
    cf_array[0] = -initial_investment
    cf_array[1:] = cashflow_df['Total_CF_USD_nominal'].values
    
    irr_monthly = calculate_irr(cf_array)
    irr_annual = (1 + irr_monthly) ** 12 - 1 if irr_monthly else None
    
    # ROI
    roi = (npv_real_with_sale / initial_investment) if initial_investment > 0 else 0
    
    return {
        'initial_investment': initial_investment,
        'npv_no_sale': npv_real_no_sale,
        'npv_with_sale': npv_real_with_sale,
        'irr_annual': irr_annual,
        'roi': roi,
        'total_rent_nominal': cashflow_df['Rent_USD_nominal'].sum(),
        'total_mortgage_nominal': cashflow_df['Mortgage_USD_nominal'].sum(),
        'total_amortization_nominal': cashflow_df['Amortization_USD_nominal'].sum(),
        'sale_price_nominal': cashflow_df['Sale_USD_nominal'].iloc[-1]
    }

def calculate_all(params: InvestmentInput) -> Dict[str, Any]:
    """Main entry point for calculation"""
    
    credit_df = build_credit_schedule(params)
    
    results = {}
    
    for name, scenario in params.scenarios.items():
        rent_df = build_rent_schedule(params, scenario)
        cashflow_df = build_cashflow(params, credit_df, rent_df, scenario)
        metrics = compute_metrics(params, cashflow_df)
        
        # Convert DF to list of dicts for JSON response, keeping size manageable
        # Maybe return only yearly summary or full monthly? Let's return full monthly for charts.
        # To save bandwidth, we can round values.
        
        # Calculate Cumulative Net Cashflow (excluding sale)
        cashflow_df['Cumulative_NetCF_USD_nominal'] = cashflow_df['NetCF_USD_nominal'].cumsum()

        chart_data = cashflow_df[['Month', 'NetCF_USD_nominal', 'Total_CF_USD_nominal', 'Rent_USD_nominal', 'Mortgage_USD_nominal', 'Property_Value_USD', 'Cumulative_NetCF_USD_nominal']].to_dict(orient='records')
        
        results[name] = {
            'metrics': metrics,
            'chart_data': chart_data
        }
        
    return results
