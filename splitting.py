from models import Expense
from decimal import Decimal, ROUND_DOWN


def split_equally(expense: Expense):
    if not expense.expense_users:
        raise ValueError("Expense users list is empty")

    shares = split_amount(expense.total_price, expense.expense_users, expense.paid_by)
    return shares


def split_by_item(expense: Expense):
    if not expense.items:
        raise ValueError("Expense items list is empty")

    shares = {}

    for item in expense.items:
        if not item.shared_by:
            raise ValueError(f"No users assigned to item: {item.name}")

        item_shares = split_amount(item.price, item.shared_by, expense.paid_by)

        for user, amount in item_shares.items():
            if user not in shares:
                shares[user] = Decimal("0.00")
            shares[user] += amount

    return shares


def split_amount(total_price, users, payer):
    shares = {}

    one_share = (total_price / len(users)).quantize(
        Decimal("0.01"), rounding=ROUND_DOWN
    )
    remainder = total_price - (one_share * len(users))
    remainder_receiver = payer if payer in users else users[0]

    for user in users:
        if user == remainder_receiver:
            shares[user] = one_share + remainder
        else:
            shares[user] = one_share

    return shares


def who_owes_payer(expense, shares):
    debts = {}
    for user in shares:
        if user != expense.paid_by:
            debts[user] = shares[user]

    return debts
