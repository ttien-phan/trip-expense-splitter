from models import Expense
from decimal import Decimal


def split_equally(expense: Expense):
    if not expense.expense_users:
        raise ValueError("Expense users list is empty")

    one_share = expense.total_price / len(expense.expense_users)

    shares = {}
    for user in expense.expense_users:
        shares[user] = one_share
    return shares


def split_by_item(expense: Expense):
    if not expense.items:
        raise ValueError("Expense items list is empty")

    shares = {}

    for item in expense.items:
        if not item.shared_by:
            raise ValueError(f"No users assigned to item: {item.name}")

        one_share = item.price / len(item.shared_by)

        for user in item.shared_by:
            if user not in shares:
                shares[user] = Decimal("0")
            shares[user] = shares[user] + one_share

    return shares


def who_owes_payer(expense, shares):
    debts = {}
    for user in shares:
        if user != expense.paid_by:
            debts[user] = shares[user]

    return debts
