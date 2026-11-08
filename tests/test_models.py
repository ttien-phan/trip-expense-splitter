import pytest
from models import User, Trip, Expense, Item
from decimal import Decimal


@pytest.fixture
def users():
    return {"Alex": User(name="Alex"), 
            "Maria": User(name="Maria")}


def test_add_user(users):
    trip = Trip(name="Portugal")
    trip.add_user(users["Alex"])
    assert users["Alex"] in trip.trip_users


def test_add_expense(users):
    expense = Expense(name="Taxi", 
                      total_price=Decimal("15.00"), 
                      paid_by=users["Alex"])
    trip = Trip(name="Portugal")

    trip.add_expense(expense)

    assert expense in trip.trip_expenses


def test_remove_expense_not_in_trip(users):
    expense = Expense(name="Taxi", 
                      total_price=Decimal("15.00"), 
                      paid_by=users["Alex"])
    expense2 = Expense(name="Lunch", 
                      total_price=Decimal("25.00"), 
                      paid_by=users["Alex"])
    
    trip = Trip(name="Portugal",
                trip_expenses=[expense])
    with pytest.raises(ValueError):
        trip.remove_expense(expense2)


def test_remove_expense(users):
    expense = Expense(name="Taxi", 
                      total_price=Decimal("15.00"), 
                      paid_by=users["Alex"])
    trip = Trip(name="Portugal",
                trip_expenses=[expense])
    trip.remove_expense(expense)
    assert expense not in trip.trip_expenses


def test_remove_user_not_in_trip(users):
    trip = Trip(name="Portugal")

    with pytest.raises(ValueError):
        trip.remove_user(users["Alex"])


def test_remove_user_who_paid_expense(users):
    expense = Expense(name="Taxi", 
                      total_price=Decimal("15.00"), 
                      paid_by=users["Alex"])
    trip = Trip(name="Portugal",
                trip_expenses=[expense],
                trip_users=[users["Alex"]])

    with pytest.raises(ValueError):
        trip.remove_user(users["Alex"])


def test_remove_user_who_participates_in_expense(users):
    expense = Expense(name="Taxi", 
                      total_price=Decimal("15.00"), 
                      paid_by=users["Maria"],
                      expense_users=[users["Alex"]])
    trip = Trip(name="Portugal",
                trip_users=[users["Alex"]],
                trip_expenses=[expense])

    with pytest.raises(ValueError):
        trip.remove_user(users["Alex"])


def test_remove_user_who_shares_item(users):
    pizza = Item(name="Pizza",
                shared_by=[users["Alex"], users["Maria"]],
                price=Decimal("25.00"))
    expense = Expense(name="Lunch", 
                      total_price=Decimal("25.00"), 
                      paid_by=users["Maria"],
                      items=[pizza])
    trip = Trip(name="Portugal",
                trip_users=[users["Alex"]],
                trip_expenses=[expense])

    with pytest.raises(ValueError):
        trip.remove_user(users["Alex"])


def test_remove_user(users):
    pizza = Item(name="Pizza",
                shared_by=[users["Maria"]],
                price=Decimal("25.00"))
    expense = Expense(name="Lunch", 
                      total_price=Decimal("25.00"), 
                      paid_by=users["Maria"],
                      items=[pizza])
    trip = Trip(name="Portugal",
                trip_users=[users["Alex"]],
                trip_expenses=[expense])

    trip.remove_user(users["Alex"])

    assert users["Alex"] not in trip.trip_users