import argparse
import locale
from collections import namedtuple
from datetime import datetime

CalculationResult = namedtuple('CalculationResult', ['purchase', 'income', 'profitability'])

bond_name = ''
bond_denomination = 1000
bond_price = 965.18
bond_aci = 33.94
bond_count = 75
broker_commision = 0.3
tax = 13
coupons = [
    (datetime(2022, 2, 16), 34.9),
    (datetime(2022, 8, 17), 34.9),
    (datetime(2023, 2, 16), 34.9),
    (datetime(2023, 8, 16), 34.9),
]

def strfloat(value):
    return locale.format_string('%.2f', value)

def fixed_calculation():
    purchase_sum = (bond_price + bond_aci) * bond_count
    commision = purchase_sum * (broker_commision / 100)
    purchase_with_commision = purchase_sum + commision
    coupon_income = 0
    for c in coupons:
        coupon_income += c[1] * bond_count
    coupon_income_tax = coupon_income * (tax / 100)
    repayment_sum = bond_denomination * bond_count
    repayment_income = repayment_sum - purchase_with_commision
    repayment_tax = 0
    if repayment_income > 0:
        repayment_tax = repayment_income * (tax / 100)
    final_income = (
        (repayment_sum - repayment_tax) +
        (coupon_income - coupon_income_tax)
    )
    profitability = final_income * 100 / purchase_with_commision - 100
    days_till_repayment = (coupons[-1][0] - datetime.today()).days
    year_profitability = profitability * 365 / days_till_repayment

    return CalculationResult(
        purchase_with_commision,
        final_income,
        year_profitability
    )

def progressive_calculation():
    purchase_sum = (bond_price + bond_aci) * bond_count
    commision = purchase_sum * (broker_commision / 100)
    purchase_with_commision = purchase_sum + commision

    extra_bonds = 0
    leftover = 0
    extra_bonds_cost = 0
    for c in coupons[:-1]:
        coupon_income = c[1] * (bond_count + extra_bonds)
        coupon_income_tax = coupon_income * (tax / 100)
        coupon_income -= coupon_income_tax

        new_bonds = (coupon_income + leftover) // bond_price
        new_bounds_cost = new_bonds * bond_price
        commision = new_bounds_cost * (broker_commision / 100)
        new_bounds_cost += commision

        leftover = (coupon_income + leftover) - new_bounds_cost
        extra_bonds += new_bonds
        extra_bonds_cost += new_bounds_cost

    coupon_income = coupons[-1][1] * (bond_count + extra_bonds)
    coupon_income_tax = coupon_income * (tax / 100)
    coupon_income -= coupon_income_tax

    repayment_sum = bond_denomination * bond_count
    repayment_income = repayment_sum - purchase_with_commision
    repayment_tax = 0
    if repayment_income > 0:
        repayment_tax = repayment_income * (tax / 100)

    extra_bonds_repayment = bond_denomination * extra_bonds
    extra_bonds_income = extra_bonds_repayment - extra_bonds_cost
    extra_bonds_tax = 0
    if extra_bonds_income > 0:
        extra_bonds_tax = extra_bonds_income * (tax / 100)

    final_income = (
        (repayment_sum - repayment_tax) +
        (extra_bonds_repayment - extra_bonds_tax) +
        coupon_income + leftover
    )
    profitability = final_income * 100 / purchase_with_commision - 100
    days_till_repayment = (coupons[-1][0] - datetime.today()).days
    year_profitability = profitability * 365 / days_till_repayment

    return CalculationResult(
        purchase_with_commision,
        final_income,
        year_profitability
    )

def report(fixed, progressive):
    print('{:30} {:10} {:10}'.format(' ', 'F', 'P'))
    print('=' * 50)
    print('{:30} {:10}'.format(
        'Сумма покупки с коммисией',
        strfloat(fixed.purchase),
    ))
    print('{:30} {:10} {:10}'.format(
        'Сумма выплат при погашении',
        strfloat(fixed.income),
        strfloat(progressive.income)
    ))
    print('{:30} {:10} {:10}'.format(
        'Доход',
        strfloat(fixed.income - fixed.purchase),
        strfloat(progressive.income - progressive.purchase)
    ))
    print('{:30} {:10} {:10}'.format(
        'Годовая доходность',
        strfloat(fixed.profitability),
        strfloat(progressive.profitability)
    ))
    print('\nF -- без реинвестирования купонного дохода')
    print('P -- с реинвестированием купонного дохода')




if __name__ == '__main__':
    #locale.setlocale(locale.LC_NUMERIC, 'ru_RU.utf8')
    #parser = argparse.ArgumentParser()
    #args = parser.parse_args()

    report(fixed_calculation(), progressive_calculation())


