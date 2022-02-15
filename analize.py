import argparse
import locale
from collections import namedtuple
from datetime import datetime

CalculationResult = namedtuple('CalculationResult', ['purchase', 'income', 'profitability'])
BondData = namedtuple('BondData', [
    'name', 'denomination', 'price',
    'aci', 'coupons'
])

BROKER_COMMISION = 0.3
TAX = 13

bond = BondData(
    'ОФЗ-26227',
    1000,
    965.18,
    33.94,
    [
        (datetime(2022, 2, 16), 34.9),
        (datetime(2022, 8, 17), 34.9),
        (datetime(2023, 2, 16), 34.9),
        (datetime(2023, 8, 16), 34.9),
    ]
)

def strfloat(value):
    return locale.format_string('%.2f', value)

def fixed_calculation(bond_count):
    purchase_sum = (bond.price + bond.aci) * bond_count
    commision = purchase_sum * (BROKER_COMMISION / 100)
    purchase_with_commision = purchase_sum + commision
    coupon_income = 0
    for c in bond.coupons:
        coupon_income += c[1] * bond_count
    coupon_income_tax = coupon_income * (TAX / 100)
    repayment_sum = bond.denomination * bond_count
    repayment_income = repayment_sum - purchase_with_commision
    repayment_tax = 0
    if repayment_income > 0:
        repayment_tax = repayment_income * (TAX / 100)
    final_income = (
        (repayment_sum - repayment_tax) +
        (coupon_income - coupon_income_tax)
    )
    profitability = final_income * 100 / purchase_with_commision - 100
    days_till_repayment = (bond.coupons[-1][0] - datetime.today()).days
    year_profitability = profitability * 365 / days_till_repayment

    return CalculationResult(
        purchase_with_commision,
        final_income,
        year_profitability
    )

def progressive_calculation(bond_count):
    purchase_sum = (bond.price + bond.aci) * bond_count
    commision = purchase_sum * (BROKER_COMMISION / 100)
    purchase_with_commision = purchase_sum + commision

    extra_bonds = 0
    leftover = 0
    extra_bonds_cost = 0
    for c in bond.coupons[:-1]:
        coupon_income = c[1] * (bond_count + extra_bonds)
        coupon_income_tax = coupon_income * (TAX / 100)
        coupon_income -= coupon_income_tax

        new_bonds = (coupon_income + leftover) // bond.price
        new_bounds_cost = new_bonds * bond.price
        commision = new_bounds_cost * (BROKER_COMMISION / 100)
        new_bounds_cost += commision

        leftover = (coupon_income + leftover) - new_bounds_cost
        extra_bonds += new_bonds
        extra_bonds_cost += new_bounds_cost

    coupon_income = bond.coupons[-1][1] * (bond_count + extra_bonds)
    coupon_income_tax = coupon_income * (TAX / 100)
    coupon_income -= coupon_income_tax

    repayment_sum = bond.denomination * bond_count
    repayment_income = repayment_sum - purchase_with_commision
    repayment_tax = 0
    if repayment_income > 0:
        repayment_tax = repayment_income * (TAX / 100)

    extra_bonds_repayment = bond.denomination * extra_bonds
    extra_bonds_income = extra_bonds_repayment - extra_bonds_cost
    extra_bonds_tax = 0
    if extra_bonds_income > 0:
        extra_bonds_tax = extra_bonds_income * (TAX / 100)

    final_income = (
        (repayment_sum - repayment_tax) +
        (extra_bonds_repayment - extra_bonds_tax) +
        coupon_income + leftover
    )
    profitability = final_income * 100 / purchase_with_commision - 100
    days_till_repayment = (bond.coupons[-1][0] - datetime.today()).days
    year_profitability = profitability * 365 / days_till_repayment

    return CalculationResult(
        purchase_with_commision,
        final_income,
        year_profitability
    )

def report(fixed, progressive):
    print('{:30} {:10} {:10}'.format(bond.name, 'F', 'P'))
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
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c', '--count', type=int, required=True, help='how many bonds to buy'
    )
    args = parser.parse_args()

    report(fixed_calculation(args.count), progressive_calculation(args.count))


