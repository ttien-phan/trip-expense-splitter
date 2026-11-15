import pytest
from storage import *
from models import User, Trip, Expense, Item
from database import create_tables
from decimal import Decimal
import sqlite3


def test_add_user(tmp_path):
    db_path = tmp_path / "test.db"
    create_tables(db_path)
    result = add_user("Alex", db_path)
    expected = "Alex"

    assert result.name == expected
    assert result.id is not None


def test_get_user(tmp_path):
    db_path = tmp_path / "test.db"
    create_tables(db_path)
    user = add_user("Alex", db_path)
    user_id = user.id
    result = get_user(user_id, db_path)

    assert result.name == "Alex"


def test_get_user_not_found(tmp_path):
    db_path = tmp_path / "test.db"
    create_tables(db_path)

    result = get_user(999, db_path)

    assert result is None


def test_get_all_users(tmp_path):
    db_path = tmp_path / "test.db"
    create_tables(db_path)
    alex = add_user("Alex", db_path)
    maria = add_user("Maria", db_path)
    jack = add_user("Jack", db_path)

    result = get_all_users(db_path)

    assert [user.name for user in result] == ["Alex", "Maria", "Jack"]


def test_add_trip(tmp_path):
    db_path = tmp_path / "test.db"
    create_tables(db_path)
    trip = Trip("Italy")
    result = add_trip(trip, db_path)
    trip_id = result.id

    assert result.name == "Italy"
    assert trip_id is not None


def test_get_trip(tmp_path):
    db_path = tmp_path / "test.db"
    create_tables(db_path)
    italy = Trip("Italy")
    trip = add_trip(italy, db_path)
    result = get_trip(trip.id, db_path)

    assert result.name == "Italy"
    assert result.id == trip.id


def test_get_trip_not_found(tmp_path):
    db_path = tmp_path / "test.db"
    create_tables(db_path)

    result = get_trip(999, db_path)

    assert result is None


def test_get_all_trips(tmp_path):
    db_path = tmp_path / "test.db"
    create_tables(db_path)
    italy = Trip("Italy")
    spain = Trip("Spain")
    france = Trip("France")

    add_trip(italy, db_path)
    add_trip(spain, db_path)
    add_trip(france, db_path)

    result = get_all_trips(db_path)

    assert [trip.name for trip in result] == ["Italy", "Spain", "France"]


def test_add_expense(tmp_path):
    db_path = tmp_path / "test.db"
    create_tables(db_path)
    alex = add_user("Alex", db_path)
    maria = add_user("Maria", db_path)
    jack = add_user("Jack", db_path)

    france = Trip("France")
    france = add_trip(france, db_path)

    dinner = Expense("Dinner", Decimal("40"), alex)

    result = add_expense(dinner, france, db_path)

    assert result.id is not None
    assert result.name == "Dinner"
    assert result.total_price == Decimal("40")
    assert result.paid_by == alex


def test_add_expense_user(tmp_path):
    db_path = tmp_path / "test.db"
    create_tables(db_path)
    alex = add_user("Alex", db_path)
    maria = add_user("Maria", db_path)
    jack = add_user("Jack", db_path)

    france = Trip("France")
    france = add_trip(france, db_path)

    dinner = Expense("Dinner", Decimal("40"), alex, expense_users=[alex, maria, jack])

    result = add_expense(dinner, france, db_path)
    saved_users = get_expense_users(result.id, db_path)

    assert result.expense_users == [alex, maria, jack]
    assert saved_users == [alex, maria, jack]


def test_add_expense_user_invalid_expense(tmp_path):
    db_path = tmp_path / "test.db"
    create_tables(db_path)
    alex = add_user("Alex", db_path)

    with closing(get_connection(db_path)) as connection:
        with connection:
            cursor = connection.cursor()
            with pytest.raises(sqlite3.IntegrityError):
                add_expense_user(cursor, 999, alex.id)


def test_add_expense_item(tmp_path):
    db_path = tmp_path / "test.db"
    create_tables(db_path)
    alex = add_user("Alex", db_path)
    maria = add_user("Maria", db_path)
    jack = add_user("Jack", db_path)

    france = Trip("France")
    france = add_trip(france, db_path)

    pizza = Item("Pizza", Decimal("25"), shared_by=[maria, alex])
    salad = Item("Salad", Decimal("15"), shared_by=[jack])

    dinner = Expense("Dinner", Decimal("40"), alex, items=[pizza, salad])

    result = add_expense(dinner, france, db_path)
    saved_items = get_expense_items(result.id, db_path)

    assert [item.price for item in saved_items] == [Decimal("25"), Decimal("15")]
    assert [item.name for item in saved_items] == ["Pizza", "Salad"]
    assert set(saved_items[0].shared_by) == {maria, alex}
    assert set(saved_items[1].shared_by) == {jack}


def test_add_expense_item_invalid_user(tmp_path):
    db_path = tmp_path / "test.db"
    create_tables(db_path)
    alex = add_user("Alex", db_path)

    france = Trip("France")
    france = add_trip(france, db_path)

    user = User("Unknown", 999)

    pizza = Item("Pizza", Decimal("25"), shared_by=[user])
    dinner = Expense("Dinner", Decimal("40"), alex)

    result = add_expense(dinner, france, db_path)
    with closing(get_connection(db_path)) as connection:
        with connection:
            cursor = connection.cursor()
            with pytest.raises(sqlite3.IntegrityError):
                add_expense_item(cursor, result.id, pizza)


def test_get_expenses(tmp_path):
    db_path = tmp_path / "test.db"
    create_tables(db_path)
    alex = add_user("Alex", db_path)

    france = Trip("France")
    france = add_trip(france, db_path)

    pizza = Item("Pizza", Decimal("25"))
    salad = Item("Salad", Decimal("15"))

    dinner = Expense("Dinner", Decimal("40"), alex, items=[pizza, salad])

    expense = add_expense(dinner, france, db_path)
    result = get_expenses(france.id, db_path)

    assert len(result) == 1
    assert result[0].name == "Dinner"
    assert result[0].total_price == Decimal("40")
    assert result[0].id is not None
    assert len(result[0].items) == 2
    assert [item.name for item in result[0].items] == ["Pizza", "Salad"]


def test_add_trip_users(tmp_path):
    db_path = tmp_path / "test.db"
    create_tables(db_path)

    alex = add_user("Alex", db_path)
    maria = add_user("Maria", db_path)
    jack = add_user("Jack", db_path)

    france = Trip("France")
    france = add_trip(france, db_path)

    with closing(get_connection(db_path)) as connection:
        with connection:
            cursor = connection.cursor()

            add_trip_user(cursor, france.id, alex.id)
            add_trip_user(cursor, france.id, maria.id)
            add_trip_user(cursor, france.id, jack.id)

    result = get_trip_users(france.id, db_path)

    assert result == [alex, maria, jack]


def test_add_trip_user_duplicate(tmp_path):
    db_path = tmp_path / "test.db"
    create_tables(db_path)

    alex = add_user("Alex", db_path)

    france = Trip("France")
    france = add_trip(france, db_path)

    with closing(get_connection(db_path)) as connection:
        with connection:
            cursor = connection.cursor()

            add_trip_user(cursor, france.id, alex.id)
            with pytest.raises(sqlite3.IntegrityError):
                add_trip_user(cursor, france.id, alex.id)


def test_add_trip_user_invalid_user(tmp_path):
    db_path = tmp_path / "test.db"
    create_tables(db_path)

    france = Trip("France")
    france = add_trip(france, db_path)

    with closing(get_connection(db_path)) as connection:
        with connection:
            cursor = connection.cursor()

            with pytest.raises(sqlite3.IntegrityError):
                add_trip_user(cursor, france.id, 999)


def test_add_trip_user_invalid_trip(tmp_path):
    db_path = tmp_path / "test.db"
    create_tables(db_path)

    alex = add_user("Alex", db_path)

    with closing(get_connection(db_path)) as connection:
        with connection:
            cursor = connection.cursor()
            with pytest.raises(sqlite3.IntegrityError):
                add_trip_user(cursor, 999, alex.id)
