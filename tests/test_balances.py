from decimal import Decimal
from models import User, Trip, SplitType, Expense, Item
from balances import (
    calculate_balances,
    get_debt,
    get_user_total_debt,
    get_total_owed_to_user,
    get_user_balance,
    get_user_all_debt,
    get_user_all_owed
)
import pytest


@pytest.fixture
def users():
    return {
        "Alex": User(name="Alex"),
        "Maria": User(name="Maria"),
        "Jack": User(name="Jack"),
        "Lora": User(name="Lora")
    }


@pytest.fixture
def balances(users):
    return {
        (users["Alex"], users["Maria"]): Decimal("30.00"),
        (users["Jack"], users["Alex"]): Decimal("20.00"),
        (users["Jack"], users["Lora"]): Decimal("25.00"),
        (users["Alex"], users["Lora"]): Decimal("25.00")
    }


def create_expense(name, payer, participants, total_price, items=None):
    return Expense(
        name=name,
        paid_by=payer,
        split_type=SplitType.BY_ITEM if items else SplitType.EQUAL,
        expense_users=participants,
        total_price=total_price,
        items=items if items else []
    )


def test_calculate_balances():
    trip = Trip(name="Portugal")

    result = calculate_balances(trip)
    expected = {}

    assert result == expected


def test_calculate_balances_with_equal_split(users):
    expense = create_expense(
        "Dinner",
        users["Alex"],
        [users["Alex"], users["Jack"], users["Lora"]],
        Decimal("61.00")
    )

    trip = Trip(name="Portugal", trip_expenses=[expense])

    result = calculate_balances(trip)
    expected = {
        (users["Jack"], users["Alex"]): Decimal("20.33"),
        (users["Lora"], users["Alex"]): Decimal("20.33")
    }

    assert result == expected


def test_calculate_balances_with_item_split(users):
    pizza = Item(
        name="Pizza", 
        price=Decimal("30.00"), 
        shared_by=[users["Alex"], users["Jack"]]
    )

    salad = Item(
        name="Salad", 
        price=Decimal("20.00"), 
        shared_by=[users["Maria"], users["Jack"]]
    )

    drinks = Item(
        name="Drinks",
        price=Decimal("10.00"),
        shared_by=[users["Alex"], users["Jack"], users["Maria"]]
    )

    expense = create_expense(
        "Dinner",
        users["Alex"],
        [users["Alex"], users["Jack"], users["Maria"]],
        Decimal("60.00"),
        [pizza, salad, drinks],
    )

    trip = Trip(name="Portugal", trip_expenses=[expense])

    result = calculate_balances(trip)
    expected = {
        (users["Jack"], users["Alex"]): Decimal("28.33"),
        (users["Maria"], users["Alex"]): Decimal("13.33")
    }

    assert result == expected


def test_calculate_balances_aggregates_same_debts(users):
    expense1 = create_expense(
        "Dinner", 
        users["Alex"], 
        [users["Alex"], users["Jack"]], 
        Decimal("60.00")
    )

    expense2 = create_expense(
        "Lunch",
        users["Alex"],
        [users["Alex"], users["Jack"]],
        Decimal("40.00")
    )

    trip = Trip(name="Portugal", trip_expenses=[expense1, expense2])

    result = calculate_balances(trip)

    expected = {(users["Jack"], users["Alex"]): Decimal("50.00")}

    assert result == expected


def test_get_debt(users, balances):
    result = get_debt(balances, users["Alex"], users["Maria"])
    expected = Decimal("30.00")

    assert result == expected


def test_get_debt_returns_zero(users, balances):
    result = get_debt(balances, users["Jack"], users["Maria"])
    expected = Decimal("0.00")

    assert result == expected


def test_get_user_total_debt(users, balances):
    result = get_user_total_debt(balances, users["Jack"])
    expected = Decimal("45.00")

    assert result == expected


def test_get_user_total_debt_returns_zero(users, balances):
    result = get_user_total_debt(balances, users["Lora"])
    expected = Decimal("0.00")

    assert result == expected


def test_get_total_owed_to_user(users, balances):
    result = get_total_owed_to_user(balances, users["Lora"])
    expected = Decimal("50.00")

    assert result == expected


def test_get_total_owed_to_user_returns_zero(users, balances):
    result = get_total_owed_to_user(balances, users["Jack"])
    expected = Decimal("0.00")

    assert result == expected


def test_get_user_balance_with_negative_balance(users, balances):
    result = get_user_balance(balances, users["Alex"])
    expected = Decimal("-35.00")

    assert result == expected


def test_get_user_balance_with_positive_balance(users, balances):
    result = get_user_balance(balances, users["Lora"])
    expected = Decimal("50.00")

    assert result == expected


def test_get_user_all_debt(users, balances):
    result = get_user_all_debt(balances, users["Alex"])

    expected = {users["Maria"]: Decimal("30.00"), users["Lora"]: Decimal("25.00")}

    assert result == expected


def test_get_user_all_owed(users, balances):
    result = get_user_all_owed(balances, users["Lora"])
    expected = {
        users["Jack"]: Decimal("25.00"),
        users["Alex"]: Decimal("25.00"),
    }

    assert result == expected
