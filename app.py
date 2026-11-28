import streamlit as st

from decimal import Decimal
from database import create_tables
from models import Trip, Expense, Repayment, SplitType, Item
from storage import *
from balances import calculate_balances, get_user_balance
from transfers import calculate_transfers

create_tables()

st.title("Expense Splitter")
st.write("Welcome to Expense Splitter!")

trip_name = st.text_input("Enter trip name")

if st.button("Create trip"):
    if trip_name:
        trip = Trip(name=trip_name)
        saved_trip = add_trip(trip)
        st.success(f"Trip '{saved_trip.name}' created!")
    else:
        st.warning("Please enter a trip name.")

all_trips = get_all_trips()

if not all_trips:
    st.info("Please create a trip first.")
    st.stop()

trip_names = [f"{trip.name} (ID: {trip.id})" for trip in all_trips]

selected_trip = st.selectbox("Chose a trip", trip_names)
selected_trip_id = selected_trip.split("ID: ")[1].replace(")", "")
selected_trip_id = int(selected_trip_id)
selected_trip = get_trip(selected_trip_id)

st.write(f"Selected trip: {selected_trip.name}")

st.subheader("Trip members")

user_name = st.text_input("Enter member name")

if st.button("Add member"):
    if user_name:
        user = add_user(user_name)
        add_user_to_trip(user, selected_trip)
        st.success(f"{user.name} added to {selected_trip.name}!")
    else:
        st.warning("Please enter a member name.")

st.subheader("Members")

members = get_trip_users(selected_trip.id)

for member in members:
    st.write(member.name)

st.subheader("Add expense")

expense_name = st.text_input("Expense name")
expense_amount = st.number_input("Amount (€)", min_value=0.01)

split_type = st.selectbox(
    "How should the expense be split?",
    [SplitType.EQUAL, SplitType.BY_ITEM],
    format_func=lambda split: split.value
)

payer = st.selectbox(
    "Who paid?",
    members,
    format_func=lambda user: user.name
)

items = []

if split_type == SplitType.BY_ITEM:
    number_of_items = st.number_input(
        "Number of items",
        min_value=1,
        step=1
    )

    for i in range(int(number_of_items)):
        st.write(f"Item {i + 1}")

        item_name = st.text_input(
            "Item name",
            key=f"item_name_{i}"
        )

        item_price = st.number_input(
            "Item price (€)",
            min_value=0.01,
            key=f"item_price_{i}"
        )

        shared_by = st.multiselect(
            "Who shares this item?",
            members,
            format_func=lambda user: user.name,
            key=f"item_users_{i}"
        )

        items.append(
            Item(
                name=item_name,
                price=Decimal(str(item_price)),
                shared_by=shared_by
            )
        )

if st.button("Add expense"):
    if not expense_name:
        st.warning("Please enter expense name.")

    elif split_type == SplitType.BY_ITEM and (
        sum(item.price for item in items) != Decimal(str(expense_amount))
    ):
        st.warning("Items total must match expense amount.")

    elif split_type == SplitType.BY_ITEM and any(
        not item.name or not item.shared_by for item in items
    ):
        st.warning("Please enter item names and select participants.")

    else:
        expense = Expense(
            name=expense_name,
            total_price=Decimal(str(expense_amount)),
            paid_by=payer,
            expense_users=members,
            split_type=split_type,
            items=items
        )

        add_expense(expense, selected_trip)

        st.success(f"Expense '{expense_name}' added!")
        st.rerun()

st.subheader("Expenses")

expenses = get_expenses(selected_trip.id)

for expense in expenses:
    st.write(
        f"{expense.name} — {expense.total_price} € " f"(paid by {expense.paid_by.name})"
    )

selected_trip.trip_expenses = expenses
repayments = get_repayments(selected_trip.id)
selected_trip.trip_repayments = repayments

balances = calculate_balances(selected_trip)

st.subheader("Balances")

for member in members:
    balance = get_user_balance(balances, member)

    if balance > 0:
        st.write(f"{member.name} should receive {balance} €")

    elif balance < 0:
        st.write(f"{member.name} owes {abs(balance)} €")

    else:
        st.write(f"{member.name} is settled.")


st.subheader("Recommended transfers")
selected_trip.trip_users = members

transfers = calculate_transfers(selected_trip)

for debtor, creditor, amount in transfers:
    st.write(f"{debtor.name} pays {creditor.name}: {amount} €")


st.subheader("Repayment history")

with st.expander("Repayment history"):
    for repayment in repayments:
        st.write(
            f"{repayment.paid_by.name} paid "
            f"{repayment.paid_to.name}: "
            f"{repayment.amount} € "
            f"on {repayment.repayment_date.strftime('%d.%m.%Y %H:%M')}"
        )


st.subheader("Record repayment")

paid_by = st.selectbox(
    "Who paid back?",
    members,
    format_func=lambda user: user.name,
    key="repayment_paid_by",
)

other_members = [user for user in members if user != paid_by]

paid_to = st.selectbox(
    "Who received the money?",
    other_members,
    format_func=lambda user: user.name,
    key="repayment_paid_to",
)

repayment_amount = Decimal(str(st.number_input(
    "Repayment amount ", min_value=0.01, key="repayment_amount"))
)

if st.button("Record repayment"):

    transfer_amount = next(
        (
            amount
            for debtor, creditor, amount in transfers
            if debtor == paid_by and creditor == paid_to
        ),
        Decimal("0.00")
    )

    if transfer_amount == 0:
        st.warning("There is no recommended transfer between these users.")

    elif repayment_amount > transfer_amount:
        st.warning("Repayment cannot be greater than recommended transfer.")

    else:
        repayment = Repayment(
            paid_by=paid_by,
            paid_to=paid_to,
            amount=Decimal(str(repayment_amount))
        )

        add_repayment(repayment, selected_trip)

        st.success("Repayment recorded!")
        st.rerun()
