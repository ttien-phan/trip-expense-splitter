from models import User, Trip, Expense, SplitType, Item
from database import get_connection
from contextlib import closing
from dataclasses import replace
from decimal import Decimal
from datetime import datetime


def add_user(name: str) -> User:

    with closing(get_connection()) as connection:
        with connection:
            cursor = connection.cursor()
            cursor.execute(
                """ 
            INSERT INTO users(name)
            VALUES (?);
            """,
                (name,),
            )
            user_id = cursor.lastrowid
    return User(name, user_id)


def get_user(user_id):
    with closing(get_connection()) as connection:
        with connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT * FROM users
                WHERE id = ?
                """,
                (user_id,),
            )
            result = cursor.fetchone()

    if result is not None:
        return User(result[1], result[0])

    return None


def get_all_users():
    with closing(get_connection()) as connection:
        with connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT * FROM users
                """)
            result = cursor.fetchall()

    users = []
    for i in result:
        users.append(User(i[1], i[0]))

    return users


def add_trip(trip: Trip):

    with closing(get_connection()) as connection:
        with connection:
            cursor = connection.cursor()
            cursor.execute(
                """ 
            INSERT INTO trips(name)
            VALUES (?);
            """,
                (trip.name,),
            )
            trip_id = cursor.lastrowid
    return Trip(trip.name, trip_id)


def get_trip(trip_id):
    with closing(get_connection()) as connection:
        with connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT * FROM trips
                WHERE id = ?
                """,
                (trip_id,),
            )
            result = cursor.fetchone()

    if result is not None:
        return Trip(result[1], result[0])

    return None


def get_all_trips():
    with closing(get_connection()) as connection:
        with connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT * FROM trips
                """)
            result = cursor.fetchall()

    trips = []
    for i in result:
        trips.append(Trip(i[1], i[0]))

    return trips


def add_expense(expense: Expense, trip: Trip):
    with closing(get_connection()) as connection:
        with connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                    INSERT INTO expenses (
                    trip_id,
                    name,
                    total_price,
                    paid_by,
                    split_type,
                    expense_date
                )
                VALUES (?,?,?,?,?,?);
            """,
                (
                    trip.id,
                    expense.name,
                    str(expense.total_price),
                    expense.paid_by.id,
                    expense.split_type.value,
                    expense.expense_date.isoformat(),
                ),
            )

            expense_id = cursor.lastrowid
            for user in expense.expense_users:
                add_expense_user(cursor, expense_id, user.id)

            saved_items = []
            for item in expense.items:
                saved_item = add_expense_item(cursor, expense_id, item)
                saved_items.append(saved_item)

            expense.items = saved_items
                
            return replace(expense, id=expense_id)



def add_expense_user(cursor, expense_id, user_id):
    cursor.execute(
        """
        INSERT INTO expense_users (expense_id, user_id)
        VALUES (?, ?);
        """, (expense_id, user_id),
    )


def add_expense_item(cursor, expense_id, item):
    cursor.execute(
        """
        INSERT INTO items(expense_id, name, price)
            VALUES (?,?,?);
        """, (expense_id, item.name, str(item.price))
    )

    item_id = cursor.lastrowid
        
    for user in item.shared_by:
        cursor.execute(
            """
            INSERT INTO item_users(item_id, user_id)
            VALUES (?,?);
        """,
            (item_id, user.id),
        )
    return replace(item, id=item_id)
    



def get_expenses(trip_id):
    with closing(get_connection()) as connection:
        with connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT * FROM expenses
                WHERE trip_id = ?
                """,
                (trip_id,),
            )
            result = cursor.fetchall()
    expenses = []
    for i in result:
        expenses.append(Expense(i[2], 
                        Decimal(i[3]), 
                        get_user(i[4]), 
                        i[0], 
                        split_type=SplitType(i[5]), 
                        expense_date=datetime.fromisoformat(i[6]),
                        expense_users=get_expense_users(i[0]),
                        items=get_expense_items(i[0])
                        )
                    )
    return expenses


def get_expense_users(expense_id):
    with closing(get_connection()) as connection:
        with connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT user_id FROM expense_users
                WHERE expense_id = ?
            """, (expense_id,))

            result = cursor.fetchall()

        users = []
        for user_id in result:
            users.append(get_user(user_id[0]))

    return users



def get_item_users(item_id):
    with closing(get_connection()) as connection:
        with connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT user_id FROM item_users
                WHERE item_id = ?
            """, (item_id,))

            result = cursor.fetchall()

        users = []
        for user_id in result:
            users.append(get_user(user_id[0]))

    return users


def get_expense_items(expense_id):
    with closing(get_connection()) as connection:
        with connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT * FROM items
                WHERE expense_id = ?
                """, (expense_id,)
            )

            result = cursor.fetchall()

    items = []
    for row in result:
        users = get_item_users(row[0])
        items.append(Item(name=row[2], 
                        price=Decimal(row[3]),
                        id=row[0],
                        shared_by=users
                        ))
    return items