import sqlite3

connection = sqlite3.connect("expense_splitter.db")
connection.execute("PRAGMA foreign_keys = ON")

cursor = connection.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS trips (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS trip_users(
	    trip_id INTEGER NOT NULL,
	    user_id INTEGER NOT NULL,
	
	    PRIMARY KEY(trip_id, user_id),
	
	    FOREIGN KEY (trip_id) REFERENCES trips(id),
	    FOREIGN KEY (user_id) REFERENCES users(id)
    )
""")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses(
	    id INTEGER PRIMARY KEY,
	    trip_id INTEGER NOT NULL,
	    name TEXT NOT NULL,
	    total_price TEXT NOT NULL,
	    paid_by INTEGER NOT NULL,
	    split_type TEXT NOT NULL,
	    expense_date TEXT NOT NULL,
	
	    FOREIGN KEY (trip_id) REFERENCES trips(id),
	    FOREIGN KEY (paid_by) REFERENCES users(id)
    )
""")


cursor.execute("""
    CREATE TABLE IF NOT EXISTS expense_users(
	    expense_id INTEGER NOT NULL,
	    user_id INTEGER NOT NULL,
	
	    PRIMARY KEY (expense_id, user_id),
	
	    FOREIGN KEY (expense_id) REFERENCES expenses(id),
	    FOREIGN KEY (user_id) REFERENCES users(id)
    )
""")


cursor.execute("""
    CREATE TABLE IF NOT EXISTS items (
	    id INTEGER PRIMARY KEY,
	    expense_id INTEGER NOT NULL,
	    name TEXT NOT NULL,
	    price TEXT NOT NULL,
	
	    FOREIGN KEY (expense_id) REFERENCES expenses(id)	
    )
""")


cursor.execute("""
    CREATE TABLE IF NOT EXISTS item_users(
	    item_id INTEGER NOT NULL,
	    user_id INTEGER NOT NULL,
	
	    PRIMARY KEY (item_id, user_id),
	
	    FOREIGN KEY (item_id) REFERENCES items(id),
	FOREIGN KEY (user_id) REFERENCES users(id)
    )
""")


connection.commit()
print(connection.execute("PRAGMA foreign_keys").fetchone())
connection.close()
