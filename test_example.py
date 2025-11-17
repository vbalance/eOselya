"""
Example usage and testing of the real estate investment model.
"""

from config import ModelParameters, ScenarioParameters
from main import run_analysis


def test_default_parameters():
    """Test with default parameters"""
    print("\n" + "="*80)
    print("TEST 1: Default Parameters")
    print("="*80)

    from main import create_default_params
    params = create_default_params()

    results = run_analysis(params, output_dir="output/test1_default")

    # Verify key metrics
    base_metrics = results['metrics']['base']
    print(f"\nVerification:")
    print(f"  Initial Investment: ${base_metrics['Initial_Investment_USD']:,.2f}")
    print(f"  NPV (base): ${base_metrics['NPV_Real_USD_with_sale']:,.2f}")
    print(f"  IRR (base): {base_metrics['IRR_annual_USD_with_sale']*100:.2f}%")

    assert base_metrics['Initial_Investment_USD'] == 16500.0, "Initial investment mismatch"
    print("\n✓ Test 1 PASSED")


def test_custom_scenario():
    """Test with custom scenario"""
    print("\n" + "="*80)
    print("TEST 2: Custom Scenario - Higher Down Payment")
    print("="*80)

    params = ModelParameters(
        apartment_cost_usd=60000.0,
        fx_today=40.0,
        downpayment_usd=20000.0,  # Higher down payment
        extra_purchase_costs_usd=3000.0,
        loan_term_years=15,  # Shorter term
        interest_annual=0.08,
        rent_initial_uah=15000.0,  # Higher rent
        usd_discount_annual=0.04
    )

    results = run_analysis(params, output_dir="output/test2_custom")

    base_metrics = results['metrics']['base']
    print(f"\nVerification:")
    print(f"  Apartment Cost: ${params.apartment_cost_usd:,.2f}")
    print(f"  Loan Term: {params.loan_term_years} years")
    print(f"  Down Payment: ${params.downpayment_usd:,.2f}")
    print(f"  Loan Amount: {params.loan_amount_uah:,.2f} UAH")
    print(f"  NPV (base): ${base_metrics['NPV_Real_USD_with_sale']:,.2f}")

    print("\n✓ Test 2 PASSED")


def test_aggressive_optimistic_scenario():
    """Test with aggressive growth scenario"""
    print("\n" + "="*80)
    print("TEST 3: Aggressive Growth Scenario")
    print("="*80)

    params = ModelParameters(
        apartment_cost_usd=50000.0,
        fx_today=42.0,
        downpayment_usd=10000.0,
        extra_purchase_costs_usd=2000.0,
        loan_term_years=20,
        interest_annual=0.065,
        rent_initial_uah=10000.0,
        scenarios={
            'aggressive': ScenarioParameters(
                rent_growth_annual=0.05,  # 5% annual rent growth
                inflation_uah_annual=0.08,
                price_growth_annual_usd=0.04  # 4% price appreciation
            )
        }
    )

    results = run_analysis(params, output_dir="output/test3_aggressive")

    aggressive_metrics = results['metrics']['aggressive']
    print(f"\nVerification:")
    print(f"  Scenario: Aggressive Growth")
    print(f"  Rent Growth: 5% annually")
    print(f"  Price Growth: 4% annually (USD)")
    print(f"  NPV: ${aggressive_metrics['NPV_Real_USD_with_sale']:,.2f}")
    if aggressive_metrics['IRR_annual_USD_with_sale'] is not None:
        print(f"  IRR: {aggressive_metrics['IRR_annual_USD_with_sale']*100:.2f}%")
    if aggressive_metrics['ROI_Real_USD_with_sale'] is not None:
        print(f"  ROI: {aggressive_metrics['ROI_Real_USD_with_sale']*100:.2f}%")

    # With aggressive growth, should have positive returns
    assert aggressive_metrics['NPV_Real_USD_with_sale'] > 0, "NPV should be positive with aggressive growth"
    if aggressive_metrics['IRR_annual_USD_with_sale'] is not None:
        assert aggressive_metrics['IRR_annual_USD_with_sale'] > 0.05, "IRR should be > 5% with aggressive growth"

    print("\n✓ Test 3 PASSED")


def test_validation_errors():
    """Test parameter validation"""
    print("\n" + "="*80)
    print("TEST 4: Parameter Validation")
    print("="*80)

    # Test negative loan term
    try:
        params = ModelParameters(
            apartment_cost_usd=57000.0,
            fx_today=41.5,
            downpayment_usd=11500.0,
            extra_purchase_costs_usd=5000.0,
            loan_term_years=-10,  # Invalid!
            interest_annual=0.07,
            rent_initial_uah=12000.0
        )
        print("ERROR: Should have raised validation error!")
        assert False, "Validation should have failed"
    except ValueError as e:
        print(f"✓ Correctly caught validation error: {e}")

    # Test zero exchange rate
    try:
        params = ModelParameters(
            apartment_cost_usd=57000.0,
            fx_today=0.0,  # Invalid!
            downpayment_usd=11500.0,
            extra_purchase_costs_usd=5000.0,
            loan_term_years=20,
            interest_annual=0.07,
            rent_initial_uah=12000.0
        )
        print("ERROR: Should have raised validation error!")
        assert False, "Validation should have failed"
    except ValueError as e:
        print(f"✓ Correctly caught validation error: {e}")

    print("\n✓ Test 4 PASSED")


def test_cashflow_calculations():
    """Test specific cashflow calculations"""
    print("\n" + "="*80)
    print("TEST 5: Cashflow Calculations")
    print("="*80)

    params = ModelParameters(
        apartment_cost_usd=50000.0,
        fx_today=40.0,
        downpayment_usd=10000.0,
        extra_purchase_costs_usd=0.0,  # No extra costs for simple test
        loan_term_years=10,  # Shorter for easier verification
        interest_annual=0.06,
        rent_initial_uah=10000.0,
        insurance_annual=0.0,  # Disable for simple test
        maintenance_annual=0.0,  # Disable for simple test
        usd_discount_annual=0.0  # No discounting for simple test
    )

    from schedule import build_credit_schedule, build_rent_schedule
    from cashflow import build_cashflow_usd

    credit_df = build_credit_schedule(params)
    rent_df = build_rent_schedule(params, 'base')
    cashflow_df = build_cashflow_usd(params, credit_df, rent_df, 'base')

    # Verify first month calculations
    first_month = cashflow_df.iloc[0]

    print(f"\nFirst Month Verification:")
    print(f"  Rent (UAH): {rent_df.iloc[0]['Rent_UAH']:,.2f}")
    print(f"  Rent (USD): ${first_month['Rent_USD_nominal']:,.2f}")
    print(f"  Mortgage (UAH): {credit_df.iloc[0]['Total_Mortgage_UAH']:,.2f}")
    print(f"  Mortgage (USD): ${first_month['Mortgage_Total_USD_nominal']:,.2f}")
    print(f"  Net CF (USD): ${first_month['NetCF_USD_nominal']:,.2f}")

    # With zero growth, rent should be constant
    assert rent_df.iloc[0]['Rent_UAH'] == rent_df.iloc[-1]['Rent_UAH'], "Rent should be constant with 0% growth"

    # Principal should be constant (differentiated payment)
    assert abs(credit_df.iloc[0]['Principal_UAH'] - credit_df.iloc[-1]['Principal_UAH']) < 0.01, \
        "Principal should be constant"

    print("\n✓ Test 5 PASSED")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*80)
    print("RUNNING ALL TESTS")
    print("="*80)

    try:
        test_default_parameters()
        test_custom_scenario()
        test_aggressive_optimistic_scenario()
        test_validation_errors()
        test_cashflow_calculations()

        print("\n" + "="*80)
        print("ALL TESTS PASSED ✓")
        print("="*80)

    except Exception as e:
        print("\n" + "="*80)
        print(f"TEST FAILED ✗: {e}")
        print("="*80)
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    run_all_tests()
