from dataclasses import dataclass, field
from decimal import Decimal
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class User:
    name: str
    id: UUID = field(default_factory=uuid4)


@dataclass
class Item:
    name: str
    price: Decimal
    shared_by: list[User] = field(default_factory=list)


@dataclass
class Expense:
    name: str
    total_price: Decimal
    paid_by: User
    expense_users: list[User] = field(default_factory=list)
    items: list[Item] = field(default_factory=list)
    expense_date: datetime = field(default_factory=datetime.now)


@dataclass
class Trip:
    name: str
    trip_users: list[User] = field(default_factory=list)
    trip_expenses: list[Expense] = field(default_factory=list)

    def add_user(self, user: User):
        self.trip_users.append(user)

    def add_expense(self, expense: Expense):
        self.trip_expenses.append(expense)

    def remove_expense(self, expense: Expense):
        self.trip_expenses.remove(expense)

    def remove_user(self, user: User):
        self.trip_users.remove(user)
