// Types matching backend models
export interface ScenarioParameters {
  rent_growth_annual: number;
  inflation_uah_annual: number;
  price_growth_annual_usd: number;
}

export interface InvestmentInput {
  apartment_cost_usd: number;
  fx_today: number;
  downpayment_usd: number;
  extra_purchase_costs_usd: number;
  loan_term_years: number;
  interest_annual: number;
  payment_type: 'differentiated' | 'annuity';
  rent_initial_uah: number;
  insurance_annual: number;
  amortization_coefficient: number;
  usd_discount_annual: number;
  scenarios: {
    [key: string]: ScenarioParameters;
  };
}

export interface Metrics {
  initial_investment: number;
  npv_no_sale: number;
  npv_with_sale: number;
  irr_annual: number | null;
  roi: number;
  total_rent_nominal: number;
  total_mortgage_nominal: number;
  total_amortization_nominal: number;
  sale_price_nominal: number;
}

export interface ChartDataPoint {
  Month: number;
  NetCF_USD_nominal: number;
  Total_CF_USD_nominal: number;
  Rent_USD_nominal: number;
  Mortgage_USD_nominal: number;
  Property_Value_USD: number;
  Cumulative_NetCF_USD_nominal: number;
}

export interface ScenarioResult {
  metrics: Metrics;
  chart_data: ChartDataPoint[];
}

export interface CalculationResult {
  [scenario: string]: ScenarioResult;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api';

export async function calculateInvestment(data: InvestmentInput): Promise<CalculationResult> {
  const response = await fetch(`${API_URL}/calculate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error('Calculation failed');
  }

  return response.json();
}

export async function exportInvestment(data: InvestmentInput): Promise<Blob> {
  const response = await fetch(`${API_URL}/export`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error('Export failed');
  }

  return response.blob();
}
