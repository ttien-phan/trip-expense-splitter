from balances import get_user_balance, calculate_balances



def calculate_transfers(trip):
    debtors = []
    creditors = []
    transfers = []

    balances = calculate_balances(trip)

    for user in trip.trip_users:
        balance = get_user_balance(balances, user)
        if balance > 0:
            creditors.append((user, balance))
        elif balance < 0:
            debtors.append((user, abs(balance)))

    while debtors and creditors:
        debtor, debt = debtors[0]
        creditor, credit = creditors[0]

        amount = min(debt, credit)
        transfers.append((debtor, creditor, amount))

        debt -= amount
        credit -= amount

        if debt == 0:
            del debtors[0]
        else:
            debtors[0] = (debtor, debt)

        if credit == 0:
            del creditors[0]
        else:
            creditors[0] = (creditor, credit)

    return transfers

