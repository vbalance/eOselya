# Real Estate Investment Model (eOselya)

A comprehensive Python tool for modeling real estate investments with mortgage financing in UAH, calculating metrics in USD with proper discounting and scenario analysis.

## Features

- **Differentiated Mortgage Payments**: Models declining interest payments with fixed principal
- **Multi-Currency Analysis**: Handles UAH mortgage with USD-based investment metrics
- **Scenario Analysis**: Pessimistic, Base, and Optimistic scenarios for:
  - Rent growth
  - UAH inflation
  - Property price appreciation
- **Key Metrics Calculation**:
  - NPV (Net Present Value) in real USD
  - IRR (Internal Rate of Return) in USD
  - ROI (Return on Investment)
- **Excel Export**: Comprehensive multi-sheet Excel reports with formatted output
- **Flexible Configuration**: JSON/YAML config files or programmatic setup

## Installation

1. Install required packages:
```bash
pip install -r requirements.txt
```

## Quick Start

### Using Default Parameters

```bash
python main.py
```

### Using Configuration File

```bash
python main.py config_example.json
```

## Configuration

Edit `config_example.json` or create your own configuration file:

```json
{
  "apartment_cost_usd": 57000.0,
  "fx_today": 41.5,
  "downpayment_usd": 11500.0,
  "extra_purchase_costs_usd": 5000.0,
  "loan_term_years": 20,
  "interest_annual": 0.07,
  "rent_initial_uah": 12000.0,
  "usd_discount_annual": 0.03,
  "scenarios": {
    "base": {
      "rent_growth_annual": 0.0,
      "inflation_uah_annual": 0.10,
      "price_growth_annual_usd": 0.0
    }
  }
}
```

### Parameters

#### Apartment & Transaction
- `apartment_cost_usd`: Property price in USD
- `fx_today`: USD/UAH exchange rate at purchase
- `downpayment_usd`: Initial down payment
- `extra_purchase_costs_usd`: Repairs, notary, commissions, etc.

#### Loan
- `loan_term_years`: Mortgage term in years
- `interest_annual`: Annual interest rate (e.g., 0.07 = 7%)
- `insurance_annual`: Annual insurance rate (default: 0.0025 = 0.25%)
- `maintenance_annual`: Annual maintenance rate (default: 0.01 = 1%)

#### Rental
- `rent_initial_uah`: Starting monthly rent in UAH

#### Discount Rate
- `usd_discount_annual`: USD discount rate for NPV calculations (e.g., 0.03 = 3%)

#### Scenarios
Each scenario includes:
- `rent_growth_annual`: Annual rent growth rate
- `inflation_uah_annual`: UAH inflation rate
- `price_growth_annual_usd`: Annual property appreciation in USD

## Output

The program generates:

1. **Excel Report** (`real_estate_analysis_YYYYMMDD_HHMMSS.xlsx`):
   - `Parameters`: All input parameters
   - `Summary`: Key metrics across all scenarios
   - `Credit_Schedule`: Monthly mortgage payment breakdown
   - `Rent_[Scenario]`: Rent projections by scenario
   - `Cashflow_[Scenario]`: Complete cashflow analysis by scenario

2. **CSV Files**: Individual metrics files for each scenario

3. **Console Output**: Formatted summary with key metrics

## Project Structure

```
eOselya/
├── config.py           # Parameter configuration and validation
├── schedule.py         # Credit and rent schedule builders
├── cashflow.py         # Cashflow analysis
├── metrics.py          # NPV, IRR, ROI calculations
├── export_excel.py     # Excel export functionality
├── main.py             # Main orchestration script
├── requirements.txt    # Python dependencies
├── config_example.json # Sample configuration
└── README.md           # This file
```

## Usage Examples

### Programmatic Usage

```python
from config import ModelParameters
from main import run_analysis

# Create custom parameters
params = ModelParameters(
    apartment_cost_usd=60000,
    fx_today=40.0,
    downpayment_usd=12000,
    extra_purchase_costs_usd=3000,
    loan_term_years=15,
    interest_annual=0.065,
    rent_initial_uah=15000,
    usd_discount_annual=0.04
)

# Run analysis
results = run_analysis(params, output_dir="my_analysis")

# Access results
print(results['metrics']['base']['NPV_Real_USD_with_sale'])
```

### Custom Scenario

```python
from config import ModelParameters, ScenarioParameters

params = ModelParameters(
    apartment_cost_usd=57000,
    fx_today=41.5,
    downpayment_usd=11500,
    extra_purchase_costs_usd=5000,
    loan_term_years=20,
    interest_annual=0.07,
    rent_initial_uah=12000,
    scenarios={
        'custom': ScenarioParameters(
            rent_growth_annual=0.05,
            inflation_uah_annual=0.08,
            price_growth_annual_usd=0.03
        )
    }
)
```

## Financial Model Details

### Credit Schedule (Differentiated Payments)

- **Principal**: Fixed monthly payment = Loan Amount / Number of Months
- **Interest**: Declining payment = Remaining Balance × Monthly Interest Rate
- **Insurance**: Fixed monthly payment based on apartment cost
- **Total Payment**: Principal + Interest + Insurance (decreases over time)

### Discounting Methodology

All cashflows are converted to:
1. **Nominal USD**: Using initial exchange rate
2. **Real USD**: Discounted using USD discount rate

This accounts for the time value of money in dollars while the loan is denominated in UAH.

### NPV Calculation

```
NPV = -Initial_Investment + Σ(Discounted_Monthly_Cashflows) + Discounted_Sale_Price
```

### IRR Calculation

Solves for the rate where NPV = 0 using Newton-Raphson method on nominal USD cashflows including sale proceeds.

## Validation

The program validates:
- Positive loan amounts
- Reasonable interest rates
- Positive exchange rates
- Valid loan terms

Warnings are issued for:
- Very small loan amounts
- Unusually high interest rates
- Suspicious parameter values

## License

MIT License

## Author

Created for real estate investment analysis in Ukraine
