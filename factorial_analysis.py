"""
Factorial analysis: 27 scenarios (3×3×3)
Analyzes all combinations of inflation, rent growth, and price growth.
"""

import itertools
import pandas as pd
from pathlib import Path
from config import ModelParameters, ScenarioParameters
from main import run_analysis


def generate_27_scenarios():
    """
    Generate 27 scenarios from 3 factors with 3 levels each:

    1. Inflation UAH: Low (6%), Medium (10%), High (15%)
    2. Rent vs Inflation: Lags (-4%), Matches (0%), Leads (+3%)
    3. Price Growth USD: Falls (-2%), Stable (+1%), Grows (+4%)
    """

    # Factor 1: Inflation levels
    inflation_levels = {
        'low_inf': 0.06,      # 6% - стабилизация
        'med_inf': 0.10,      # 10% - средняя
        'high_inf': 0.15      # 15% - кризис
    }

    # Factor 2: Rent growth relative to inflation
    rent_growth_delta = {
        'rent_lags': -0.04,     # Отстает на 4%
        'rent_match': 0.00,     # Вровень
        'rent_leads': 0.03      # Обгоняет на 3%
    }

    # Factor 3: Price growth in USD
    price_growth_usd = {
        'price_falls': -0.02,    # Падает
        'price_stable': 0.01,    # Стабильна
        'price_grows': 0.04      # Растет
    }

    scenarios = {}
    scenario_descriptions = {}

    for (inf_key, inflation), (rent_key, rent_delta), (price_key, price) in \
        itertools.product(inflation_levels.items(),
                         rent_growth_delta.items(),
                         price_growth_usd.items()):

        # Scenario name: low_inf_rent_lags_price_falls
        scenario_name = f"{inf_key}_{rent_key}_{price_key}"

        # Calculate actual rent growth
        rent_growth = inflation + rent_delta

        # Create scenario
        scenarios[scenario_name] = ScenarioParameters(
            rent_growth_annual=rent_growth,
            inflation_uah_annual=inflation,
            price_growth_annual_usd=price
        )

        # Human-readable description
        inf_label = {'low_inf': 'Инфляция 6%', 'med_inf': 'Инфляция 10%', 'high_inf': 'Инфляция 15%'}[inf_key]
        rent_label = {'rent_lags': 'Аренда отстает', 'rent_match': 'Аренда вровень', 'rent_leads': 'Аренда обгоняет'}[rent_key]
        price_label = {'price_falls': 'Цена падает', 'price_stable': 'Цена стабильна', 'price_grows': 'Цена растет'}[price_key]

        scenario_descriptions[scenario_name] = f"{inf_label}, {rent_label}, {price_label}"

    return scenarios, scenario_descriptions


def run_factorial_analysis(output_dir='output/factorial_27'):
    """Run analysis for all 27 scenarios"""

    print("=" * 80)
    print("ФАКТОРНЫЙ АНАЛИЗ: 27 СЦЕНАРИЕВ")
    print("=" * 80)
    print()

    # Generate scenarios
    print("Генерация 27 сценариев...")
    scenarios, descriptions = generate_27_scenarios()
    print(f"✓ Создано {len(scenarios)} сценариев")
    print()

    # Create parameters
    params = ModelParameters(
        apartment_cost_usd=57000,
        fx_today=41.5,
        downpayment_usd=11500,
        extra_purchase_costs_usd=5000,
        loan_term_years=20,
        interest_annual=0.07,
        rent_initial_uah=12000,
        scenarios=scenarios
    )

    # Run analysis (suppress detailed output)
    print("Запуск анализа всех сценариев...")
    print("(это может занять 1-2 минуты)")
    print()

    import sys
    from io import StringIO

    # Redirect stdout to suppress detailed output
    old_stdout = sys.stdout
    sys.stdout = StringIO()

    results = run_analysis(params, output_dir=output_dir)

    # Restore stdout
    sys.stdout = old_stdout

    print("✓ Анализ завершен!")
    print()

    # Create summary DataFrame
    print("Создание сводной таблицы...")
    summary_data = []

    for scenario_name, metrics in results['metrics'].items():
        # Parse scenario name
        parts = scenario_name.split('_')
        inf = parts[0] + '_' + parts[1]  # low_inf, med_inf, high_inf
        rent = parts[2] + '_' + parts[3]  # rent_lags, rent_match, rent_leads
        price = parts[4] + '_' + parts[5]  # price_falls, price_stable, price_grows

        # Get scenario parameters
        scenario_params = params.scenarios[scenario_name]

        summary_data.append({
            'Scenario': scenario_name,
            'Description': descriptions[scenario_name],
            'Inflation_UAH': scenario_params.inflation_uah_annual,
            'Rent_Growth': scenario_params.rent_growth_annual,
            'Price_Growth_USD': scenario_params.price_growth_annual_usd,
            'Real_Rent_Growth': scenario_params.rent_growth_annual - scenario_params.inflation_uah_annual,
            'Inflation_Level': inf,
            'Rent_vs_Inflation': rent,
            'Price_Trend': price,
            'NPV_USD': metrics['NPV_Real_USD_with_sale'],
            'IRR_pct': metrics['IRR_annual_USD_with_sale'] * 100 if metrics['IRR_annual_USD_with_sale'] else None,
            'ROI_pct': metrics['ROI_Real_USD_with_sale'] * 100 if metrics['ROI_Real_USD_with_sale'] else None,
            'Initial_Investment': metrics['Initial_Investment_USD'],
            'Total_Rent_Real_USD': metrics['Total_Rent_Collected_USD_real'],
            'Terminal_Price_Real_USD': metrics['Terminal_Price_USD_real']
        })

    df = pd.DataFrame(summary_data)

    # Sort by NPV
    df = df.sort_values('NPV_USD', ascending=False)

    # Save summary
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    summary_file = output_path / 'summary_27_scenarios.csv'
    df.to_csv(summary_file, index=False)
    print(f"✓ Сводная таблица: {summary_file}")

    # Create pivot tables
    print("\nСоздание pivot таблиц...")

    # NPV matrix
    pivot_npv = df.pivot_table(
        values='NPV_USD',
        index='Inflation_Level',
        columns=['Rent_vs_Inflation', 'Price_Trend'],
        aggfunc='mean'
    )
    pivot_npv.to_csv(output_path / 'npv_matrix.csv')
    print(f"✓ NPV матрица: {output_path / 'npv_matrix.csv'}")

    # IRR matrix
    pivot_irr = df.pivot_table(
        values='IRR_pct',
        index='Inflation_Level',
        columns=['Rent_vs_Inflation', 'Price_Trend'],
        aggfunc='mean'
    )
    pivot_irr.to_csv(output_path / 'irr_matrix.csv')
    print(f"✓ IRR матрица: {output_path / 'irr_matrix.csv'}")

    return df, results


def print_summary(df):
    """Print summary statistics"""

    print("\n" + "=" * 80)
    print("СТАТИСТИКА ПО 27 СЦЕНАРИЯМ")
    print("=" * 80)
    print()

    print("NPV (Net Present Value, USD):")
    print(f"  Минимум:  ${df['NPV_USD'].min():>12,.0f}")
    print(f"  Медиана:  ${df['NPV_USD'].median():>12,.0f}")
    print(f"  Среднее:  ${df['NPV_USD'].mean():>12,.0f}")
    print(f"  Максимум: ${df['NPV_USD'].max():>12,.0f}")
    print()

    print("IRR (Internal Rate of Return, %):")
    print(f"  Минимум:  {df['IRR_pct'].min():>12.2f}%")
    print(f"  Медиана:  {df['IRR_pct'].median():>12.2f}%")
    print(f"  Среднее:  {df['IRR_pct'].mean():>12.2f}%")
    print(f"  Максимум: {df['IRR_pct'].max():>12.2f}%")
    print()

    print("ROI (Return on Investment, %):")
    print(f"  Минимум:  {df['ROI_pct'].min():>12.0f}%")
    print(f"  Медиана:  {df['ROI_pct'].median():>12.0f}%")
    print(f"  Среднее:  {df['ROI_pct'].mean():>12.0f}%")
    print(f"  Максимум: {df['ROI_pct'].max():>12.0f}%")
    print()

    # Count profitable scenarios
    profitable = (df['NPV_USD'] > 0).sum()
    print(f"Прибыльных сценариев (NPV > 0): {profitable} из 27 ({profitable/27*100:.0f}%)")

    above_alternative = (df['IRR_pct'] > 3).sum()
    print(f"Выше альтернативы (IRR > 3%): {above_alternative} из 27 ({above_alternative/27*100:.0f}%)")
    print()

    # Top 5 and Bottom 5
    print("=" * 80)
    print("ТОП-5 ЛУЧШИХ СЦЕНАРИЕВ (по NPV)")
    print("=" * 80)
    print()

    for idx, row in df.head(5).iterrows():
        print(f"{row['Description']}")
        print(f"  NPV: ${row['NPV_USD']:,.0f} | IRR: {row['IRR_pct']:.2f}% | ROI: {row['ROI_pct']:.0f}%")
        print()

    print("=" * 80)
    print("ТОП-5 ХУДШИХ СЦЕНАРИЕВ (по NPV)")
    print("=" * 80)
    print()

    for idx, row in df.tail(5).iterrows():
        print(f"{row['Description']}")
        print(f"  NPV: ${row['NPV_USD']:,.0f} | IRR: {row['IRR_pct']:.2f}% | ROI: {row['ROI_pct']:.0f}%")
        print()

    # Factor analysis
    print("=" * 80)
    print("ВЛИЯНИЕ ФАКТОРОВ (средний NPV)")
    print("=" * 80)
    print()

    print("По уровню инфляции:")
    for inf in ['low_inf', 'med_inf', 'high_inf']:
        avg_npv = df[df['Inflation_Level'] == inf]['NPV_USD'].mean()
        label = {'low_inf': '6%', 'med_inf': '10%', 'high_inf': '15%'}[inf]
        print(f"  {label:>4}: ${avg_npv:>12,.0f}")
    print()

    print("По росту аренды относительно инфляции:")
    for rent in ['rent_lags', 'rent_match', 'rent_leads']:
        avg_npv = df[df['Rent_vs_Inflation'] == rent]['NPV_USD'].mean()
        label = {'rent_lags': 'Отстает', 'rent_match': 'Вровень', 'rent_leads': 'Обгоняет'}[rent]
        print(f"  {label:>10}: ${avg_npv:>12,.0f}")
    print()

    print("По росту цены недвижимости:")
    for price in ['price_falls', 'price_stable', 'price_grows']:
        avg_npv = df[df['Price_Trend'] == price]['NPV_USD'].mean()
        label = {'price_falls': 'Падает', 'price_stable': 'Стабильна', 'price_grows': 'Растет'}[price]
        print(f"  {label:>11}: ${avg_npv:>12,.0f}")
    print()


def main():
    """Main entry point for factorial analysis"""

    # Run analysis
    df, results = run_factorial_analysis()

    # Print summary
    print_summary(df)

    print("=" * 80)
    print("АНАЛИЗ ЗАВЕРШЕН")
    print("=" * 80)
    print()
    print("Файлы созданы в: output/factorial_27/")
    print("  - summary_27_scenarios.csv - полная сводная таблица")
    print("  - npv_matrix.csv - матрица NPV по факторам")
    print("  - irr_matrix.csv - матрица IRR по факторам")
    print("  - real_estate_analysis_*.xlsx - детальный Excel отчет")
    print()

    return df, results


if __name__ == "__main__":
    main()
