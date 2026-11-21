from dataclasses import dataclass, field
from decimal import Decimal
from datetime import datetime
from enum import Enum


@dataclass(frozen=True)
class User:
    name: str
    id: int


@dataclass
class Item:
    name: str
    price: Decimal
    id: int | None = None
    shared_by: list[User] = field(default_factory=list)


class SplitType(Enum):
    EQUAL = "equal"
    BY_ITEM = "by_item"


@dataclass
class Expense:
    name: str
    total_price: Decimal
    paid_by: User
    id: int | None = None
    split_type: SplitType = SplitType.EQUAL
    expense_users: list[User] = field(default_factory=list)
    items: list[Item] = field(default_factory=list)
    expense_date: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if self.split_type == SplitType.BY_ITEM:
            if not self.items:
                raise ValueError("BY_ITEM expense must contain at least one item")

            items_total = sum(item.price for item in self.items)
            if items_total != self.total_price:
                raise ValueError(
                    f"Items total {items_total} does not match expense total {self.total_price}"
                )


@dataclass
class Repayment:
    paid_by: User
    paid_to: User
    amount: Decimal
    id: int | None = None
    repayment_date: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if self.paid_by == self.paid_to:
            raise ValueError("User cannot pay themselves")

        if self.amount <= Decimal("0"):
            raise ValueError("Amount must be more than 0")


@dataclass
class Trip:
    name: str
    id: int | None = None
    trip_users: list[User] = field(default_factory=list)
    trip_expenses: list[Expense] = field(default_factory=list)
    trip_repayments: list[Repayment] = field(default_factory=list)

    def add_user(self, user: User):
        self.trip_users.append(user)

    def add_expense(self, expense: Expense):
        self.trip_expenses.append(expense)

    def add_repayment(self, repayment: Repayment):
        self.trip_repayments.append(repayment)

    def remove_expense(self, expense: Expense):
        if expense not in self.trip_expenses:
            raise ValueError("Expense is not part of this trip")

        self.trip_expenses.remove(expense)

    def remove_user(self, user: User):
        if user not in self.trip_users:
            raise ValueError("User is not a member of this trip")

        if any(
            user == repayment.paid_by or user == repayment.paid_to
            for repayment in self.trip_repayments
        ):
            raise ValueError("Cannot remove a user who participated in repayments")

        if any(
            user in expense.expense_users
            or expense.paid_by == user
            or any(user in item.shared_by for item in expense.items)
            for expense in self.trip_expenses
        ):
            raise ValueError("Cannot remove a user who participated in expenses")

        self.trip_users.remove(user)
