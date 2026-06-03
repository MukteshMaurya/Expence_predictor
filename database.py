import pandas as pd
import os

DATA_FOLDER = "user_data"

if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

def get_user_file(username):
    return os.path.join(DATA_FOLDER, f"{username}.csv")

def init_user_file(username):

    file_path = get_user_file(username)

    if not os.path.exists(file_path):

        df = pd.DataFrame(
            columns=[
                "ID",
                "Date",
                "Month",
                "Description",
                "Amount",
                "Category"
            ]
        )

        df.to_csv(file_path, index=False)
from datetime import datetime

def insert_expense(
    username,
    month,
    desc,
    amount,
    category
):
    file_path = get_user_file(username)

    init_user_file(username)

    df = pd.read_csv(file_path)

    if df.empty:
        new_id = 1
    else:
        new_id = int(df["ID"].max()) + 1

    new_row = {
        "ID": new_id,
        "Date": datetime.now().strftime("%d-%m-%Y"),
        "Month": month,
        "Description": desc,
        "Amount": float(amount),
        "Category": category
    }

    df = pd.concat(
        [df, pd.DataFrame([new_row])],
        ignore_index=True
    )

    df.to_csv(
        file_path,
        index=False
    )
    
def fetch_expenses(username):

    file_path = get_user_file(username)

    init_user_file(username)

    df = pd.read_csv(file_path)

    # Old CSV compatibility
    if "Date" not in df.columns:
        df["Date"] = ""

        cols = [
            "ID",
            "Date",
            "Month",
            "Description",
            "Amount",
            "Category"
        ]

        df = df[cols]

        df.to_csv(file_path, index=False)

    if df.empty:

        return pd.DataFrame(
            columns=[
                "ID",
                "Date",
                "Month",
                "Description",
                "Amount",
                "Category"
            ]
        )

    return df
def clear_expenses(username):

    file_path = get_user_file(username)

    df = pd.DataFrame(
        columns=[
            "ID",
            "Date",
            "Month",
            "Description",
            "Amount",
            "Category"
        ]
    )

    df.to_csv(
        file_path,
        index=False
    )
def delete_expense(username, expense_id):

    file_path = get_user_file(username)

    if not os.path.exists(file_path):
        return

    df = pd.read_csv(file_path)

    expense_id = int(expense_id)

    df = df[df["ID"] != expense_id]

    df.to_csv(file_path, index=False)
import json
import os

USER_FILE = "users.json"

def update_salary(username, new_salary):
    if not os.path.exists(USER_FILE):
        return False

    with open(USER_FILE, "r") as f:
        users = json.load(f)

    if username in users:
        users[username]["salary"] = new_salary

        with open(USER_FILE, "w") as f:
            json.dump(users, f, indent=4)

        return True

    return False


# ---------------- MONTHLY FINANCE ----------------

def get_finance_file(username):
    return os.path.join(DATA_FOLDER, f"{username}_finance.csv")


def init_finance_file(username):
    file_path = get_finance_file(username)

    if not os.path.exists(file_path):
        df = pd.DataFrame(
            columns=[
                "ID",
                "Date",
                "Month",
                "Description",
                "Amount",
                "Category"
            ]
)

        df.to_csv(file_path, index=False)


def update_monthly_finance(username, month, income, expenses):

    init_finance_file(username)

    file_path = get_finance_file(username)

    df = pd.read_csv(file_path)

    savings = income - expenses

    # If month already exists -> update
    if month in df["Month"].values:

        df.loc[df["Month"] == month, "Income"] = income
        df.loc[df["Month"] == month, "Expenses"] = expenses
        df.loc[df["Month"] == month, "Savings"] = savings

    else:
        new_row = {
            "Month": month,
            "Income": income,
            "Expenses": expenses,
            "Savings": savings
        }

        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    df.to_csv(file_path, index=False)


def fetch_monthly_finance(username):

    init_finance_file(username)

    file_path = get_finance_file(username)

    return pd.read_csv(file_path)