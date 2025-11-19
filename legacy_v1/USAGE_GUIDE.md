# eOselya - Руководство по использованию

## Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Запуск с параметрами по умолчанию

```bash
python main.py
```

Это запустит анализ со следующими параметрами:
- Стоимость квартиры: $57,000
- Курс: 41.5 UAH/USD
- Первый взнос: $11,500
- Срок кредита: 20 лет
- Ставка: 7% годовых
- Арендная плата: 12,000 UAH/месяц

### 3. Запуск с собственной конфигурацией

```bash
python main.py config_example.json
```

## Создание конфигурации

### Формат JSON

Создайте файл `my_config.json`:

```json
{
  "apartment_cost_usd": 60000.0,
  "fx_today": 40.0,
  "downpayment_usd": 15000.0,
  "extra_purchase_costs_usd": 4000.0,
  "loan_term_years": 20,
  "interest_annual": 0.08,
  "insurance_annual": 0.003,
  "maintenance_annual": 0.015,
  "rent_initial_uah": 15000.0,
  "usd_discount_annual": 0.04,
  "scenarios": {
    "pessimistic": {
      "rent_growth_annual": -0.02,
      "inflation_uah_annual": 0.05,
      "price_growth_annual_usd": -0.02
    },
    "base": {
      "rent_growth_annual": 0.0,
      "inflation_uah_annual": 0.10,
      "price_growth_annual_usd": 0.0
    },
    "optimistic": {
      "rent_growth_annual": 0.04,
      "inflation_uah_annual": 0.15,
      "price_growth_annual_usd": 0.03
    }
  }
}
```

Запуск:
```bash
python main.py my_config.json
```

## Описание параметров

### Базовые параметры недвижимости

| Параметр | Описание | Пример |
|----------|----------|---------|
| `apartment_cost_usd` | Стоимость квартиры в USD | 57000.0 |
| `fx_today` | Курс USD/UAH на момент покупки | 41.5 |
| `downpayment_usd` | Первый взнос в USD | 11500.0 |
| `extra_purchase_costs_usd` | Доп. расходы (ремонт, нотариус) в USD | 5000.0 |

### Параметры кредита

| Параметр | Описание | Значение по умолчанию |
|----------|----------|----------------------|
| `loan_term_years` | Срок кредита в годах | обязательно |
| `interest_annual` | Годовая ставка (доля, не %) | обязательно |
| `insurance_annual` | Страховка (доля от стоимости) | 0.0025 (0.25%) |
| `maintenance_annual` | Обслуживание (доля от стоимости) | 0.01 (1%) |

**Важно:** Ставки указываются в долях, не в процентах:
- 7% = 0.07
- 0.25% = 0.0025

### Параметры аренды

| Параметр | Описание | Пример |
|----------|----------|---------|
| `rent_initial_uah` | Начальная арендная плата в UAH/месяц | 12000.0 |

### Дисконтирование

| Параметр | Описание | Значение по умолчанию |
|----------|----------|----------------------|
| `usd_discount_annual` | Ставка дисконтирования в USD | 0.03 (3%) |

Это ставка для расчета NPV - какую доходность вы могли бы получить, инвестируя в альтернативные инструменты в USD.

### Сценарии

Каждый сценарий включает три параметра:

| Параметр | Описание | Пример |
|----------|----------|---------|
| `rent_growth_annual` | Годовой рост аренды | 0.03 (3%) |
| `inflation_uah_annual` | Инфляция гривны | 0.10 (10%) |
| `price_growth_annual_usd` | Рост стоимости квартиры в USD | 0.02 (2%) |

**Типичные сценарии:**

**Пессимистичный:**
- Арендная плата: -1% (падение спроса)
- Инфляция UAH: 7% (низкая инфляция)
- Цена квартиры: -1% (падение рынка недвижимости)

**Базовый:**
- Арендная плата: 0% (стабильность)
- Инфляция UAH: 10% (умеренная инфляция)
- Цена квартиры: 0% (без изменений в USD)

**Оптимистичный:**
- Арендная плата: +3% (рост спроса)
- Инфляция UAH: 13% (высокая инфляция)
- Цена квартиры: +2% (рост рынка)

## Выходные данные

Программа создает папку `output/` с файлами:

### 1. Excel-отчет

Файл: `real_estate_analysis_YYYYMMDD_HHMMSS.xlsx`

**Листы:**

1. **Parameters** - все входные параметры
2. **Summary** - ключевые метрики по всем сценариям
3. **Credit_Schedule** - график погашения кредита
   - Остаток долга
   - Основной долг
   - Проценты
   - Страховка
   - Итого платеж
4. **Rent_[Scenario]** - графики аренды по сценариям
5. **Cashflow_[Scenario]** - полный анализ денежных потоков

### 2. CSV файлы

- `metrics_pessimistic.csv`
- `metrics_base.csv`
- `metrics_optimistic.csv`

Содержат все рассчитанные метрики в табличном формате.

## Интерпретация результатов

### NPV (Net Present Value)

**NPV без продажи** - приведенная стоимость денежных потоков без учета продажи квартиры.

**NPV с продажей** - полная приведенная стоимость инвестиции.

- NPV > 0: инвестиция выгодна
- NPV < 0: инвестиция невыгодна
- NPV = 0: доходность равна альтернативным вложениям

### IRR (Internal Rate of Return)

Внутренняя норма доходности - годовая доходность инвестиции в USD.

- IRR > USD discount rate: инвестиция выгоднее альтернативы
- IRR < USD discount rate: альтернатива выгоднее

### ROI (Return on Investment)

ROI = NPV / Начальная инвестиция

Показывает относительную прибыль.

- ROI = 100%: удвоили вложения
- ROI = 0%: вернули только вложенное
- ROI < 0%: потеря части вложений

## Программное использование

### Пример 1: Базовый анализ

```python
from config import ModelParameters
from main import run_analysis

params = ModelParameters(
    apartment_cost_usd=57000,
    fx_today=41.5,
    downpayment_usd=11500,
    extra_purchase_costs_usd=5000,
    loan_term_years=20,
    interest_annual=0.07,
    rent_initial_uah=12000
)

results = run_analysis(params, output_dir="my_output")

# Получить метрики
base_metrics = results['metrics']['base']
print(f"NPV: ${base_metrics['NPV_Real_USD_with_sale']:,.2f}")
print(f"IRR: {base_metrics['IRR_annual_USD_with_sale']*100:.2f}%")
```

### Пример 2: Сравнение разных объектов

```python
from config import ModelParameters
from main import run_analysis

# Объект 1: дешевле, но меньше аренда
params1 = ModelParameters(
    apartment_cost_usd=45000,
    fx_today=41.5,
    downpayment_usd=9000,
    extra_purchase_costs_usd=3000,
    loan_term_years=20,
    interest_annual=0.07,
    rent_initial_uah=9000
)

results1 = run_analysis(params1, output_dir="output/apartment1")

# Объект 2: дороже, но больше аренда
params2 = ModelParameters(
    apartment_cost_usd=70000,
    fx_today=41.5,
    downpayment_usd=14000,
    extra_purchase_costs_usd=6000,
    loan_term_years=20,
    interest_annual=0.07,
    rent_initial_uah=16000
)

results2 = run_analysis(params2, output_dir="output/apartment2")

# Сравнить
print("Сравнение:")
print(f"Объект 1 - NPV: ${results1['metrics']['base']['NPV_Real_USD_with_sale']:,.2f}")
print(f"Объект 2 - NPV: ${results2['metrics']['base']['NPV_Real_USD_with_sale']:,.2f}")
```

### Пример 3: Кастомные сценарии

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
        'conservative': ScenarioParameters(
            rent_growth_annual=-0.005,
            inflation_uah_annual=0.06,
            price_growth_annual_usd=-0.005
        ),
        'aggressive': ScenarioParameters(
            rent_growth_annual=0.05,
            inflation_uah_annual=0.15,
            price_growth_annual_usd=0.04
        )
    }
)

results = run_analysis(params)
```

## Тестирование

Запустить тесты:

```bash
python test_example.py
```

Тесты проверяют:
1. Работу с параметрами по умолчанию
2. Кастомные параметры
3. Агрессивные сценарии роста
4. Валидацию параметров
5. Корректность расчетов денежных потоков

## Частые вопросы

### Почему NPV отрицательный?

Отрицательный NPV означает, что с учетом:
- Стоимости денег во времени (дисконтирования)
- Альтернативной доходности (USD discount rate)
- Всех расходов

Инвестиция менее выгодна, чем альтернативные вложения. Это не значит, что вы теряете деньги, но доходность ниже ожидаемой.

### Как учитывается инфляция?

Инфляция UAH указывается в сценариях, но:
- Кредит в UAH фиксирован (номинально не меняется)
- Аренда растет согласно `rent_growth_annual`
- Все пересчитывается в USD по начальному курсу
- Дисконтируется по `usd_discount_annual`

### Что такое дисконтирование?

Дисконтирование учитывает, что:
- $100 сегодня стоят больше, чем $100 через год
- Вы могли бы инвестировать деньги в альтернативные инструменты

`usd_discount_annual` = 3% означает, что вы могли бы получить 3% годовых, вкладывая в безрисковые USD-инструменты.

### Как изменить валюту?

Программа работает с UAH-кредитом и USD-метриками. Для других валют нужно:
1. Указать соответствующий курс в `fx_today`
2. Изменить названия в комментариях/выводе

Логика останется той же.

## Ограничения

1. **Курс фиксирован**: Программа использует один курс на весь период
2. **Дифференцированный график**: Только дифференцированные платежи (не аннуитет)
3. **Без досрочного погашения**: Не моделируется досрочное погашение кредита
4. **Без налогов**: Не учтены налоги на аренду и продажу
5. **Фиксированная аренда**: Без вакансий и перерывов в аренде

## Поддержка

Вопросы и проблемы: см. README.md
