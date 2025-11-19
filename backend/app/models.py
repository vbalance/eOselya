from pydantic import BaseModel, Field, computed_field
from typing import Dict, Optional, Literal

class ScenarioParameters(BaseModel):
    """Parameters that can vary by scenario"""
    rent_growth_annual: float = Field(..., description="Annual rent growth rate (e.g. 0.03)")
    inflation_uah_annual: float = Field(..., description="Annual UAH inflation rate (e.g. 0.10)")
    price_growth_annual_usd: float = Field(..., description="Annual property price growth in USD (e.g. 0.02)")

class InvestmentInput(BaseModel):
    """Input parameters for the investment model"""
    
    # Apartment & Transaction
    apartment_cost_usd: float = Field(..., gt=0, description="Cost of the apartment in USD")
    fx_today: float = Field(..., gt=0, description="Current USD/UAH exchange rate")
    downpayment_usd: float = Field(..., ge=0, description="Down payment in USD")
    extra_purchase_costs_usd: float = Field(..., ge=0, description="Extra costs (taxes, notary, etc) in USD")
    
    # Loan
    loan_term_years: int = Field(..., gt=0, description="Loan term in years")
    interest_annual: float = Field(..., ge=0, description="Annual interest rate (e.g. 0.07)")
    payment_type: Literal['differentiated', 'annuity'] = Field('differentiated', description="Type of mortgage payment")
    
    # Rent & Maintenance
    rent_initial_uah: float = Field(..., gt=0, description="Initial monthly rent in UAH")
    insurance_annual: float = Field(0.0025, ge=0, description="Annual insurance rate (as share of property value)")
    amortization_coefficient: float = Field(1.0, ge=0, description="Maintenance/Renovation cost as months of rent per year")
    
    # Discounting
    usd_discount_annual: float = Field(0.03, description="Discount rate for NPV calculation")
    
    # Scenarios
    scenarios: Dict[str, ScenarioParameters] = Field(default_factory=lambda: {
        'pessimistic': ScenarioParameters(rent_growth_annual=-0.01, inflation_uah_annual=0.07, price_growth_annual_usd=-0.01),
        'base': ScenarioParameters(rent_growth_annual=0.0, inflation_uah_annual=0.10, price_growth_annual_usd=0.0),
        'optimistic': ScenarioParameters(rent_growth_annual=0.03, inflation_uah_annual=0.13, price_growth_annual_usd=0.02)
    })

    @computed_field
    def apartment_cost_uah(self) -> float:
        return self.apartment_cost_usd * self.fx_today

    @computed_field
    def loan_amount_uah(self) -> float:
        downpayment_uah = self.downpayment_usd * self.fx_today
        return max(0, self.apartment_cost_uah - downpayment_uah)

    @computed_field
    def loan_term_months(self) -> int:
        return self.loan_term_years * 12

    @computed_field
    def interest_monthly(self) -> float:
        return self.interest_annual / 12
