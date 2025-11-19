import pandas as pd
import io
from typing import Dict, Any
from app.models import InvestmentInput
from app.services.calculation import build_credit_schedule, build_rent_schedule, build_cashflow, compute_metrics

def generate_excel_report(params: InvestmentInput) -> io.BytesIO:
    """
    Generate a comprehensive Excel report for the investment analysis.
    Returns a BytesIO object containing the Excel file.
    """
    
    # 1. Calculate all data
    credit_df = build_credit_schedule(params)
    
    rent_schedules = {}
    cashflows = {}
    all_metrics = {}
    
    for name, scenario in params.scenarios.items():
        rent_df = build_rent_schedule(params, scenario)
        cashflow_df = build_cashflow(params, credit_df, rent_df, scenario)
        metrics = compute_metrics(params, cashflow_df)
        
        rent_schedules[name] = rent_df
        cashflows[name] = cashflow_df
        all_metrics[name] = metrics

    # 2. Create Excel Writer
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        
        # --- PARAMETERS SHEET ---
        params_data = [
            ['APARTMENT & TRANSACTION', '', ''],
            ['Apartment Cost (USD)', params.apartment_cost_usd, 'USD'],
            ['Exchange Rate', params.fx_today, 'UAH/USD'],
            ['Down Payment (USD)', params.downpayment_usd, 'USD'],
            ['Extra Costs (USD)', params.extra_purchase_costs_usd, 'USD'],
            ['', '', ''],
            ['LOAN', '', ''],
            ['Loan Amount (UAH)', params.loan_amount_uah, 'UAH'],
            ['Term', params.loan_term_years, 'Years'],
            ['Interest Rate', params.interest_annual, 'Annual'],
            ['Payment Type', params.payment_type, ''],
            ['', '', ''],
            ['RENT & MAINTENANCE', '', ''],
            ['Initial Rent (UAH)', params.rent_initial_uah, 'UAH'],
            ['Amortization Coeff', params.amortization_coefficient, 'Months of Rent'],
            ['', '', ''],
            ['SCENARIOS', '', '']
        ]
        
        for name, scen in params.scenarios.items():
            params_data.append([f'--- {name.upper()} ---', '', ''])
            params_data.append(['Rent Growth', scen.rent_growth_annual, 'Annual'])
            params_data.append(['Inflation UAH', scen.inflation_uah_annual, 'Annual'])
            params_data.append(['Price Growth USD', scen.price_growth_annual_usd, 'Annual'])
            
        pd.DataFrame(params_data, columns=['Parameter', 'Value', 'Unit']).to_excel(writer, sheet_name='Parameters', index=False)
        
        # --- SUMMARY SHEET ---
        summary_data = []
        metrics_keys = [
            ('Initial Investment', 'initial_investment'),
            ('NPV (No Sale)', 'npv_no_sale'),
            ('NPV (With Sale)', 'npv_with_sale'),
            ('IRR (Annual)', 'irr_annual'),
            ('ROI', 'roi'),
            ('Total Rent (Nominal)', 'total_rent_nominal'),
            ('Total Mortgage (Nominal)', 'total_mortgage_nominal'),
            ('Sale Price (Nominal)', 'sale_price_nominal')
        ]
        
        summary_df = pd.DataFrame({'Metric': [k[0] for k in metrics_keys]})
        for name in params.scenarios.keys():
            summary_df[name] = [all_metrics[name].get(k[1]) for k in metrics_keys]
            
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # --- SCHEDULES ---
        credit_df.to_excel(writer, sheet_name='Credit_Schedule', index=False)
        
        for name, df in rent_schedules.items():
            df.to_excel(writer, sheet_name=f'Rent_{name}', index=False)
            
        for name, df in cashflows.items():
            df.to_excel(writer, sheet_name=f'Cashflow_{name}', index=False)
            
    output.seek(0)
    return output
