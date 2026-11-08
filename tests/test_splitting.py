from decimal import Decimal
from splitting import split_amount, split_equally, split_by_item, who_owes_payer
from models import Expense, Item, User
import pytest


@pytest.fixture
def users():
    return {
        "Alex": User(name="Alex"),
        "Maria": User(name="Maria"),
        "Jack": User(name="Jack"),
        "Lora": User(name="Lora"),
    }


def test_split_amount_equally(users):
    result = split_amount(
        Decimal("90.00"), [users["Alex"], users["Maria"], users["Jack"]], users["Alex"]
    )

    expected = {
        users["Alex"]: Decimal("30.00"),
        users["Maria"]: Decimal("30.00"),
        users["Jack"]: Decimal("30.00"),
    }

    assert result == expected


def test_split_amount_with_remainder(users):
    result = split_amount(
        Decimal("100.00"), [users["Alex"], users["Maria"], users["Jack"]], users["Alex"]
    )

    expected = {
        users["Alex"]: Decimal("33.34"),
        users["Maria"]: Decimal("33.33"),
        users["Jack"]: Decimal("33.33"),
    }

    assert result == expected


def test_split_amount_remainder_when_payer_is_not_participant(users):
    result = split_amount(
        Decimal("100.00"), [users["Alex"], users["Maria"], users["Jack"]], users["Lora"]
    )

    expected = {
        users["Alex"]: Decimal("33.34"),
        users["Maria"]: Decimal("33.33"),
        users["Jack"]: Decimal("33.33"),
    }

    assert result == expected


def test_split_amount_with_one_user(users):
    result = split_amount(Decimal("100.00"), [users["Jack"]], users["Lora"])

    expected = {users["Jack"]: Decimal("100.00")}

    assert result == expected


def test_split_amount_with_empty_users_list(users):
    with pytest.raises(ValueError):
        split_amount(Decimal("100.00"), [], users["Lora"])


def test_split_equally_with_empty_expense_users(users):
    expense = Expense(
        name="Food",
        total_price=Decimal("100.00"),
        paid_by=users["Lora"],
        expense_users=[],
    )

    with pytest.raises(ValueError):
        split_equally(expense)


def test_split_equally(users):
    expense = Expense(
        name="Food",
        total_price=Decimal("100.00"),
        paid_by=users["Lora"],
        expense_users=[users["Alex"], users["Maria"], users["Jack"]],
    )

    result = split_equally(expense)

    expected = {
        users["Alex"]: Decimal("33.34"),
        users["Maria"]: Decimal("33.33"),
        users["Jack"]: Decimal("33.33"),
    }

    assert result == expected


def test_split_by_item_with_empty_items(users):
    expense = Expense(
        name="Food", total_price=Decimal("100.00"), paid_by=users["Lora"], items=[]
    )

    with pytest.raises(ValueError):
        split_by_item(expense)


def test_split_by_item_with_empty_shared_by(users):

    item = Item(name="Pizza", price=Decimal("100.00"), shared_by=[])

    expense = Expense(
        name="Food", total_price=Decimal("100.00"), paid_by=users["Lora"], items=[item]
    )

    with pytest.raises(ValueError):
        split_by_item(expense)


def test_split_by_item_with_one_item(users):
    item = Item(
        name="Pizza",
        price=Decimal("100.00"),
        shared_by=[users["Lora"], users["Alex"], users["Maria"]],
    )

    expense = Expense(
        name="Food", total_price=Decimal("100.00"), paid_by=users["Lora"], items=[item]
    )

    result = split_by_item(expense)

    expected = {
        users["Lora"]: Decimal("33.34"),
        users["Alex"]: Decimal("33.33"),
        users["Maria"]: Decimal("33.33"),
    }

    assert result == expected


def test_split_by_item_with_many_items(users):
    pizza = Item(
        name="Pizza",
        price=Decimal("32.00"),
        shared_by=[users["Lora"], users["Alex"], users["Maria"]],
    )

    pasta = Item(
        name="Pasta", price=Decimal("25.00"), shared_by=[users["Alex"], users["Lora"]]
    )

    expense = Expense(
        name="Food",
        total_price=Decimal("57.00"),
        paid_by=users["Lora"],
        items=[pasta, pizza],
    )

    result = split_by_item(expense)

    expected = {
        users["Lora"]: Decimal("23.18"),
        users["Alex"]: Decimal("23.16"),
        users["Maria"]: Decimal("10.66"),
    }

    assert result == expected


def test_who_owes_payer_where_payer_is_participant(users):
    expense = Expense(
        name="Food",
        total_price=Decimal("90.00"),
        paid_by=users["Lora"],
        expense_users=[users["Lora"], users["Alex"], users["Maria"]],
    )

    shares = {
        users["Lora"]: Decimal("30.00"),
        users["Alex"]: Decimal("30.00"),
        users["Maria"]: Decimal("30.00"),
    }

    result = who_owes_payer(expense, shares)

    expected = {users["Alex"]: Decimal("30.00"), users["Maria"]: Decimal("30.00")}

    assert result == expected


def test_who_owes_payer_where_payer_is_not_participant(users):
    expense = Expense(
        name="Food",
        total_price=Decimal("90.00"),
        paid_by=users["Jack"],
        expense_users=[users["Lora"], users["Alex"], users["Maria"]],
    )

    shares = {
        users["Lora"]: Decimal("30.00"),
        users["Alex"]: Decimal("30.00"),
        users["Maria"]: Decimal("30.00"),
    }

    result = who_owes_payer(expense, shares)

    expected = {
        users["Lora"]: Decimal("30.00"),
        users["Alex"]: Decimal("30.00"),
        users["Maria"]: Decimal("30.00"),
    }

    assert result == expected


def test_who_owes_payer_where_payer_is_only_participant(users):
    expense = Expense(
        name="Food",
        total_price=Decimal("90.00"),
        paid_by=users["Jack"],
        expense_users=[users["Jack"]],
    )

    shares = {users["Jack"]: Decimal("90.00")}

    result = who_owes_payer(expense, shares)

    expected = {}

    assert result == expected
