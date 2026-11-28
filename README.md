# Expense Splitter

A Python web application for managing shared expenses during trips.
Users can create trips, add participants, record expenses, and see who owes whom.

## Features

- Create trips and add participants.
- Record shared expenses.
- Split expenses equally or by individual items.
- Handle rounding to cents.
- Calculate balances for each participant.
- Suggest transfers to settle debts.
- Record repayments and view repayment history.
- Store data in an SQLite database.

## Technologies

- Python 3.14
- Streamlit
- SQLite
- Pytest

## Project Structure

```text
trip-expense-splitter/
├── app.py          # Streamlit user interface
├── models.py       # Data models
├── database.py     # SQLite database setup
├── storage.py      # Data storage operations
├── splitting.py    # Expense splitting logic
├── balances.py     # Balance calculations
├── transfers.py    # Suggested transfers
├── tests/          # Automated tests
├── requirements.txt
└── README.md
```

## How to Run

Clone the repository:

```bash
git clone https://github.com/ttien-phan/trip-expense-splitter.git
cd trip-expense-splitter
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Start the application:

```bash
streamlit run app.py
```

The SQLite database and required tables are created automatically when the application starts.

## Running Tests

```bash
python -m pytest -v
```
