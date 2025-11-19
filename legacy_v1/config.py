"""
Configuration module for real estate investment modeling.
Handles parameter loading and validation.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional
import json
import yaml
from pathlib import Path


@dataclass
class ScenarioParameters:
    """Parameters that can vary by scenario (pessimistic, base, optimistic)"""
    rent_growth_annual: float  # e.g., -0.01, 0.0, 0.03
    inflation_uah_annual: float  # e.g., 0.07, 0.10, 0.13
    price_growth_annual_usd: float  # e.g., -0.01, 0.0, 0.02


@dataclass
class ModelParameters:
    """Complete set of parameters for the real estate investment model"""

    # Apartment and transaction parameters (required)
    apartment_cost_usd: float  # e.g., 57000
    fx_today: float  # USD/UAH exchange rate, e.g., 41.5
    downpayment_usd: float  # e.g., 11500
    extra_purchase_costs_usd: float  # repairs, notary, commissions, e.g., 5000

    # Loan parameters (required)
    loan_term_years: int  # e.g., 20
    interest_annual: float  # annual rate in UAH, e.g., 0.07

    # Rental parameters (required)
    rent_initial_uah: float  # e.g., 12000

    # Loan parameters (optional)
    insurance_annual: float = 0.0025  # 0.25% of apartment cost
    maintenance_annual: float = 0.01  # 1% annual maintenance

    # Discount rate for USD calculations
    usd_discount_annual: float = 0.03  # e.g., 3%

    # Scenarios
    scenarios: Dict[str, ScenarioParameters] = field(default_factory=lambda: {
        'pessimistic': ScenarioParameters(
            rent_growth_annual=-0.01,
            inflation_uah_annual=0.07,
            price_growth_annual_usd=-0.01
        ),
        'base': ScenarioParameters(
            rent_growth_annual=0.0,
            inflation_uah_annual=0.10,
            price_growth_annual_usd=0.0
        ),
        'optimistic': ScenarioParameters(
            rent_growth_annual=0.03,
            inflation_uah_annual=0.13,
            price_growth_annual_usd=0.02
        )
    })

    # Optional: manual override for loan amount
    loan_amount_uah_override: Optional[float] = None

    def __post_init__(self):
        """Calculate derived parameters and validate"""
        # Derived parameters
        self.apartment_cost_uah = self.apartment_cost_usd * self.fx_today
        self.own_cash_total_usd = self.downpayment_usd + self.extra_purchase_costs_usd
        self.own_cash_total_uah = self.own_cash_total_usd * self.fx_today

        # Loan amount
        if self.loan_amount_uah_override is not None:
            self.loan_amount_uah = self.loan_amount_uah_override
        else:
            # Note: downpayment is already in UAH equivalent via own_cash_total_uah
            # loan = apartment cost - downpayment (not including extra costs)
            downpayment_uah = self.downpayment_usd * self.fx_today
            self.loan_amount_uah = self.apartment_cost_uah - downpayment_uah

        self.loan_term_months = self.loan_term_years * 12

        # Monthly rates
        self.interest_monthly = self.interest_annual / 12
        self.usd_discount_monthly = (1 + self.usd_discount_annual) ** (1/12) - 1

        # Fixed monthly payments
        self.principal_monthly = self.loan_amount_uah / self.loan_term_months
        self.insurance_monthly_uah = self.apartment_cost_uah * self.insurance_annual / 12
        self.maintenance_monthly_uah = self.apartment_cost_uah * self.maintenance_annual / 12

        # Validate
        self._validate()

    def _validate(self):
        """Validate parameters"""
        errors = []
        warnings = []

        # Critical validations
        if self.loan_term_years <= 0:
            errors.append("Loan term must be positive")

        if self.fx_today <= 0:
            errors.append("Exchange rate must be positive")

        if self.apartment_cost_usd <= 0:
            errors.append("Apartment cost must be positive")

        if self.interest_annual < 0:
            errors.append("Interest rate cannot be negative")

        if self.loan_amount_uah < 0:
            warnings.append(f"Loan amount is negative: {self.loan_amount_uah:.2f} UAH")

        if self.loan_amount_uah < 1000:
            warnings.append(f"Loan amount is very small: {self.loan_amount_uah:.2f} UAH")

        # Rate sanity checks
        if self.interest_annual > 0.5:
            warnings.append(f"Interest rate seems very high: {self.interest_annual*100:.1f}%")

        if self.usd_discount_annual < 0 or self.usd_discount_annual > 0.2:
            warnings.append(f"USD discount rate seems unusual: {self.usd_discount_annual*100:.1f}%")

        # Print warnings
        for warning in warnings:
            print(f"WARNING: {warning}")

        # Raise errors
        if errors:
            raise ValueError("Parameter validation failed:\n" + "\n".join(errors))

    def get_scenario_monthly_rates(self, scenario_name: str) -> Dict[str, float]:
        """Calculate monthly rates for a given scenario"""
        scenario = self.scenarios[scenario_name]

        rent_growth_monthly = (1 + scenario.rent_growth_annual) ** (1/12) - 1
        inflation_uah_monthly = (1 + scenario.inflation_uah_annual) ** (1/12) - 1

        return {
            'rent_growth_monthly': rent_growth_monthly,
            'inflation_uah_monthly': inflation_uah_monthly,
            'price_growth_annual_usd': scenario.price_growth_annual_usd
        }


def load_from_json(filepath: str) -> ModelParameters:
    """Load parameters from JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Convert scenarios
    if 'scenarios' in data:
        scenarios = {}
        for name, params in data['scenarios'].items():
            scenarios[name] = ScenarioParameters(**params)
        data['scenarios'] = scenarios

    return ModelParameters(**data)


def load_from_yaml(filepath: str) -> ModelParameters:
    """Load parameters from YAML file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    # Convert scenarios
    if 'scenarios' in data:
        scenarios = {}
        for name, params in data['scenarios'].items():
            scenarios[name] = ScenarioParameters(**params)
        data['scenarios'] = scenarios

    return ModelParameters(**data)


def save_to_json(params: ModelParameters, filepath: str):
    """Save parameters to JSON file"""
    # Create a dict excluding computed fields
    data = {
        'apartment_cost_usd': params.apartment_cost_usd,
        'fx_today': params.fx_today,
        'downpayment_usd': params.downpayment_usd,
        'extra_purchase_costs_usd': params.extra_purchase_costs_usd,
        'loan_term_years': params.loan_term_years,
        'interest_annual': params.interest_annual,
        'insurance_annual': params.insurance_annual,
        'maintenance_annual': params.maintenance_annual,
        'rent_initial_uah': params.rent_initial_uah,
        'usd_discount_annual': params.usd_discount_annual,
        'scenarios': {
            name: {
                'rent_growth_annual': s.rent_growth_annual,
                'inflation_uah_annual': s.inflation_uah_annual,
                'price_growth_annual_usd': s.price_growth_annual_usd
            }
            for name, s in params.scenarios.items()
        }
    }

    if params.loan_amount_uah_override is not None:
        data['loan_amount_uah_override'] = params.loan_amount_uah_override

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
