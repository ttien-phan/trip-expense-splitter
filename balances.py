from decimal import Decimal
from models import SplitType
from splitting import split_equally, split_by_item, who_owes_payer


def calculate_balances(trip):

    balances = {}

    for expense in trip.trip_expenses:
        if expense.split_type == SplitType.EQUAL:
            shares = split_equally(expense)

        elif expense.split_type == SplitType.BY_ITEM:
            shares = split_by_item(expense)

        debts = who_owes_payer(expense, shares)

        for key, value in debts.items():
            pair = (key, expense.paid_by)

            if pair not in balances:
                balances[pair] = Decimal("0.00")

            balances[pair] += value

    return balances


def get_debt(balances, debtor, creditor):
    return balances.get((debtor, creditor), Decimal("0.00"))


def get_user_total_debt(balances, debtor):
    total = Decimal("0.00")
    for key, value in balances.items():
        if debtor == key[0]:
            total += value

    return total


def get_total_owed_to_user(balances, creditor):
    total = Decimal("0.00")
    for key, value in balances.items():
        if creditor == key[1]:
            total += value

    return total


def get_user_balance(balances, user):
    debt = get_user_total_debt(balances, user)
    owed = get_total_owed_to_user(balances, user)

    return owed - debt


def get_user_all_debt(balances, user):
    debts = {}

    for key, value in balances.items():
        if user == key[0]:
            debts[key[1]] = value

    return debts


def get_user_all_owed(balances, user):
    owed_by_users = {}

    for key, value in balances.items():
        if user == key[1]:
            owed_by_users[key[0]] = value

    return owed_by_users
