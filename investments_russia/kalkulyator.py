#!/usr/bin/env python3
"""Учебный калькулятор: сложный процент, регулярные взносы, вклад vs ОФЗ vs ИИС-3.

Запуск:  python3 kalkulyator.py
         python3 kalkulyator.py --start 100000 --monthly 10000 --rate 14 --years 10
Все расчёты — упрощённые модели для обучения, не прогноз.
"""
import argparse

NDFL = 0.13
IIS_BASE_LIMIT = 400_000  # база вычета ИИС-3 за год


def future_value(start: float, monthly: float, rate_pct: float, years: int) -> float:
    """Ежемесячная капитализация, взнос в конце месяца."""
    r = rate_pct / 100 / 12
    value = start
    for _ in range(years * 12):
        value = value * (1 + r) + monthly
    return value


def broker_account(start, monthly, rate_pct, years):
    """Обычный счёт: налог 13% с дохода в конце срока (упрощённо, без ЛДВ)."""
    fv = future_value(start, monthly, rate_pct, years)
    paid = start + monthly * 12 * years
    return fv - max(fv - paid, 0) * NDFL


def iis3(start, monthly, rate_pct, years):
    """ИИС-3: вычет 13% со взносов (до 400 тыс./год) реинвестируется через год; доход без налога."""
    r = rate_pct / 100 / 12
    value = start
    contrib_year = start
    for m in range(1, years * 12 + 1):
        value = value * (1 + r) + monthly
        contrib_year += monthly
        if m % 12 == 0:  # вычет за прошедший год поступает и довносится
            refund = min(contrib_year, IIS_BASE_LIMIT) * NDFL
            value += refund
            contrib_year = refund
    return value


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--start", type=float, default=100_000)
    p.add_argument("--monthly", type=float, default=0)
    p.add_argument("--rate", type=float, default=14, help="годовых, %%")
    p.add_argument("--years", type=int, default=5)
    a = p.parse_args()

    fmt = lambda x: f"{x:,.0f} ₽".replace(",", " ")
    print(f"Старт {fmt(a.start)}, взнос {fmt(a.monthly)}/мес, {a.rate}% годовых, {a.years} лет")
    print(f"  Без налога:          {fmt(future_value(a.start, a.monthly, a.rate, a.years))}")
    print(f"  Брокерский счёт:     {fmt(broker_account(a.start, a.monthly, a.rate, a.years))}")
    print(f"  ИИС-3 (+вычеты):     {fmt(iis3(a.start, a.monthly, a.rate, a.years))}")

    print("\nСценарии модуля 5 (100 000 ₽, 5 лет, ИИС-3):")
    for name, rate in (("плохой", 5), ("плохой", 8), ("базовый", 13), ("базовый", 16), ("хороший", 18), ("хороший", 22)):
        print(f"  {name:8} {rate:>3}%: {fmt(iis3(100_000, 0, rate, 5))}")

    print("\nРегулярные взносы под 14% (модуль 5.6):")
    for m in (5_000, 10_000, 20_000):
        print(f"  {fmt(m)}/мес: 5 лет {fmt(future_value(0, m, 14, 5))}, 10 лет {fmt(future_value(0, m, 14, 10))}")


if __name__ == "__main__":
    main()
