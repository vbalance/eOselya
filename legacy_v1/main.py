"""
Main orchestration script for real estate investment modeling.

Usage:
    python main.py [config_file]

If no config file is provided, uses default parameters.
"""

import sys
from pathlib import Path
from datetime import datetime
import json
import yaml

from config import ModelParameters, load_from_json, load_from_yaml
from schedule import build_credit_schedule, build_all_scenarios_rent_schedule
from cashflow import build_all_scenarios_cashflow
from metrics import compute_all_scenarios_metrics, format_metrics_summary
from export_excel import export_to_excel, export_metrics_to_csv


def create_default_params() -> ModelParameters:
    """Create default parameters matching the specification"""
    return ModelParameters(
        apartment_cost_usd=57000.0,
        fx_today=41.5,
        downpayment_usd=11500.0,
        extra_purchase_costs_usd=5000.0,
        loan_term_years=20,
        interest_annual=0.07,
        insurance_annual=0.0025,
        maintenance_annual=0.01,
        rent_initial_uah=12000.0,
        usd_discount_annual=0.03
    )


def run_analysis(params: ModelParameters, output_dir: str = "output"):
    """
    Run complete investment analysis.

    Args:
        params: Model parameters
        output_dir: Directory for output files
    """

    print("=" * 80)
    print("REAL ESTATE INVESTMENT MODEL - ANALYSIS START")
    print("=" * 80)
    print()

    # Display key parameters
    print("Key Parameters:")
    print(f"  Apartment Cost: ${params.apartment_cost_usd:,.2f} USD ({params.apartment_cost_uah:,.2f} UAH)")
    print(f"  Exchange Rate: {params.fx_today} UAH/USD")
    print(f"  Down Payment: ${params.downpayment_usd:,.2f} USD")
    print(f"  Extra Costs: ${params.extra_purchase_costs_usd:,.2f} USD")
    print(f"  Total Own Cash: ${params.own_cash_total_usd:,.2f} USD")
    print(f"  Loan Amount: {params.loan_amount_uah:,.2f} UAH (${params.loan_amount_uah/params.fx_today:,.2f} USD)")
    print(f"  Loan Term: {params.loan_term_years} years ({params.loan_term_months} months)")
    print(f"  Interest Rate: {params.interest_annual*100:.2f}% annually")
    print(f"  Initial Rent: {params.rent_initial_uah:,.2f} UAH/month")
    print(f"  USD Discount Rate: {params.usd_discount_annual*100:.2f}% annually")
    print()

    # Step 1: Build credit schedule
    print("Step 1: Building credit schedule...")
    credit_df = build_credit_schedule(params)
    print(f"  ✓ Credit schedule built: {len(credit_df)} months")
    print(f"  First payment: {credit_df.iloc[0]['Total_Mortgage_UAH']:,.2f} UAH")
    print(f"  Last payment: {credit_df.iloc[-1]['Total_Mortgage_UAH']:,.2f} UAH")
    print()

    # Step 2: Build rent schedules for all scenarios
    print("Step 2: Building rent schedules for all scenarios...")
    rent_schedules = build_all_scenarios_rent_schedule(params)
    for scenario_name, rent_df in rent_schedules.items():
        first_rent = rent_df.iloc[0]['Rent_UAH']
        last_rent = rent_df.iloc[-1]['Rent_UAH']
        growth = ((last_rent / first_rent) - 1) * 100
        print(f"  ✓ {scenario_name.capitalize()}: {first_rent:,.2f} → {last_rent:,.2f} UAH ({growth:+.1f}%)")
    print()

    # Step 3: Build cashflows for all scenarios
    print("Step 3: Building cashflow analysis...")
    cashflows = build_all_scenarios_cashflow(params, credit_df, rent_schedules)
    for scenario_name in cashflows.keys():
        print(f"  ✓ {scenario_name.capitalize()} cashflow computed")
    print()

    # Step 4: Compute metrics for all scenarios
    print("Step 4: Computing financial metrics...")
    all_metrics = compute_all_scenarios_metrics(params, cashflows)
    print()

    # Display metrics for each scenario
    for scenario_name, metrics in all_metrics.items():
        print(f"\n{'=' * 80}")
        print(f"SCENARIO: {scenario_name.upper()}")
        print(format_metrics_summary(metrics))

    # Step 5: Export to Excel
    print("\nStep 5: Exporting to Excel...")
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_filename = output_path / f"real_estate_analysis_{timestamp}.xlsx"

    export_to_excel(
        params=params,
        credit_df=credit_df,
        rent_schedules=rent_schedules,
        cashflows=cashflows,
        all_metrics=all_metrics,
        output_path=str(excel_filename)
    )

    # Step 6: Export metrics to CSV
    print("\nStep 6: Exporting metrics to CSV...")
    export_metrics_to_csv(all_metrics, str(output_path))

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"\nOutput files created in: {output_path.absolute()}")
    print(f"  - Excel report: {excel_filename.name}")
    print(f"  - Metrics CSVs: metrics_*.csv")
    print()

    # Quick summary
    # Use 'base' scenario if available, otherwise use first scenario
    summary_scenario = 'base' if 'base' in all_metrics else list(all_metrics.keys())[0]
    print(f"QUICK SUMMARY ({summary_scenario.capitalize()} Scenario):")
    summary_metrics = all_metrics[summary_scenario]
    print(f"  Initial Investment: ${summary_metrics['Initial_Investment_USD']:,.2f}")
    print(f"  NPV with Sale: ${summary_metrics['NPV_Real_USD_with_sale']:,.2f}")
    if summary_metrics['IRR_annual_USD_with_sale'] is not None:
        print(f"  IRR (Annual): {summary_metrics['IRR_annual_USD_with_sale']*100:.2f}%")
    if summary_metrics['ROI_Real_USD_with_sale'] is not None:
        print(f"  ROI: {summary_metrics['ROI_Real_USD_with_sale']*100:.2f}%")
    print()

    return {
        'params': params,
        'credit_schedule': credit_df,
        'rent_schedules': rent_schedules,
        'cashflows': cashflows,
        'metrics': all_metrics
    }


def main():
    """Main entry point"""

    # Check if config file provided
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
        print(f"Loading configuration from: {config_path}")

        try:
            # Detect file type
            if config_path.endswith('.json'):
                params = load_from_json(config_path)
            elif config_path.endswith(('.yaml', '.yml')):
                params = load_from_yaml(config_path)
            else:
                print("ERROR: Config file must be .json or .yaml/.yml")
                sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON in config file: {e}")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"ERROR: Invalid YAML in config file: {e}")
            sys.exit(1)
        except TypeError as e:
            print(f"ERROR: Missing or invalid parameters in config file: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"ERROR: Failed to load config file: {e}")
            sys.exit(1)
    else:
        print("No config file provided, using default parameters")
        params = create_default_params()

    # Run analysis
    try:
        results = run_analysis(params)
        print("Success!")
        return results
    except Exception as e:
        print(f"\nERROR during analysis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
