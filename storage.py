from models import Repayment, User, Trip, Expense, SplitType, Item
from database import get_connection
from contextlib import closing
from dataclasses import replace
from decimal import Decimal
from datetime import datetime


def add_user(name: str, db_path="expense_splitter.db") -> User:

    with closing(get_connection(db_path)) as connection:
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


def get_user(user_id, db_path="expense_splitter.db"):
    with closing(get_connection(db_path)) as connection:
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


def get_all_users(db_path="expense_splitter.db"):
    with closing(get_connection(db_path)) as connection:
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


def add_trip(trip: Trip, db_path="expense_splitter.db"):

    with closing(get_connection(db_path)) as connection:
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


def get_trip(trip_id, db_path="expense_splitter.db"):
    with closing(get_connection(db_path)) as connection:
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


def get_all_trips(db_path="expense_splitter.db"):
    with closing(get_connection(db_path)) as connection:
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


def add_expense(expense: Expense, trip: Trip, db_path="expense_splitter.db"):
    with closing(get_connection(db_path)) as connection:
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
        """,
        (expense_id, user_id),
    )


def add_expense_item(cursor, expense_id, item):
    cursor.execute(
        """
        INSERT INTO items(expense_id, name, price)
            VALUES (?,?,?);
        """,
        (expense_id, item.name, str(item.price)),
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


def get_expenses(trip_id, db_path="expense_splitter.db"):
    with closing(get_connection(db_path)) as connection:
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
        expenses.append(
            Expense(
                i[2],
                Decimal(i[3]),
                get_user(i[4], db_path),
                i[0],
                split_type=SplitType(i[5]),
                expense_date=datetime.fromisoformat(i[6]),
                expense_users=get_expense_users(i[0], db_path),
                items=get_expense_items(i[0], db_path),
            )
        )
    return expenses


def get_expense_users(expense_id, db_path="expense_splitter.db"):
    with closing(get_connection(db_path)) as connection:
        with connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT user_id FROM expense_users
                WHERE expense_id = ?
            """,
                (expense_id,),
            )

            result = cursor.fetchall()

        users = []
        for user_id in result:
            users.append(get_user(user_id[0], db_path))

    return users


def get_item_users(item_id, db_path="expense_splitter.db"):
    with closing(get_connection(db_path)) as connection:
        with connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT user_id FROM item_users
                WHERE item_id = ?
            """,
                (item_id,),
            )

            result = cursor.fetchall()

        users = []
        for user_id in result:
            users.append(get_user(user_id[0], db_path))

    return users


def get_expense_items(expense_id, db_path="expense_splitter.db"):
    with closing(get_connection(db_path)) as connection:
        with connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT * FROM items
                WHERE expense_id = ?
                """,
                (expense_id,),
            )

            result = cursor.fetchall()

    items = []
    for row in result:
        users = get_item_users(row[0], db_path)
        items.append(
            Item(name=row[2], price=Decimal(row[3]), id=row[0], shared_by=users)
        )
    return items


def add_trip_user(cursor, trip_id, user_id):
    cursor.execute(
        """
        INSERT INTO trip_users (trip_id, user_id)
        VALUES (?, ?);
        """,
        (trip_id, user_id),
    )


def get_trip_users(trip_id, db_path="expense_splitter.db"):
    with closing(get_connection(db_path)) as connection:
        with connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT user_id FROM trip_users
                WHERE trip_id = ?
            """,
                (trip_id,),
            )

            result = cursor.fetchall()

        users = []
        for user_id in result:
            users.append(get_user(user_id[0], db_path))

    return users


def add_repayment(repayment: Repayment, trip: Trip, db_path="expense_splitter.db"):
    with closing(get_connection(db_path)) as connection:
        with connection:
            cursor = connection.cursor()
            cursor.execute(
            """
            INSERT INTO repayments(
                trip_id,
                paid_by,
                paid_to,
                amount,
                repayment_date
            )
            VALUES(?,?,?,?,?)
            """, 
                (trip.id, repayment.paid_by.id, repayment.paid_to.id, str(repayment.amount), repayment.repayment_date.isoformat())
            )

            repayment_id = cursor.lastrowid

    return replace(repayment, id=repayment_id)


def get_repayments(trip_id, db_path="expense_splitter.db"):
    with closing(get_connection(db_path)) as connection:
        with connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT * FROM repayments
                WHERE trip_id = ?
                """, (trip_id,)
            )
            result = cursor.fetchall()

    repayments = []
    for i in result:
        repayments.append(
            Repayment(
                paid_by=get_user(i[2], db_path),
                paid_to=get_user(i[3], db_path),
                amount=Decimal(i[4]),
                id=i[0],
                repayment_date=datetime.fromisoformat(i[5])
            )
        )

    return repayments