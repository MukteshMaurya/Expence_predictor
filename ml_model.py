from sklearn.linear_model import LinearRegression
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import calendar

from database import fetch_monthly_finance

# =====================================================
# PURCHASE DATE PREDICTION
# =====================================================

def predict_purchase_date(df, salary, item_price):

    if df.empty:
        return None, "No expense history found."

    monthly_expense = df["Amount"].mean()

    monthly_savings = salary - monthly_expense

    if monthly_savings <= 0:
        return None, "No savings available currently."

    months_needed = int(np.ceil(item_price / monthly_savings))

    predicted_date = (
        datetime.now() +
        timedelta(days=30 * months_needed)
    ).strftime("%d %B %Y")

    return predicted_date, months_needed


# =====================================================
# SMART PURCHASE PLANNER
# =====================================================

def smart_purchase_planner(
    df,
    salary,
    item_name,
    item_price,
    username
):

    if df.empty:

        return {
            "status": False,
            "message": "No expense history found."
        }

    total_expense = df["Amount"].sum()

    avg_monthly_expense = df["Amount"].mean()

    # Total savings from finance file
    finance_df = fetch_monthly_finance(username)

    if not finance_df.empty:
        current_savings = finance_df["Savings"].sum()
    else:
        current_savings = 0

    monthly_savings = salary - avg_monthly_expense

    if monthly_savings <= 0:

        return {
            "status": False,
            "message": "You currently have no monthly savings."
        }

    months_needed = int(
        np.ceil(item_price / monthly_savings)
    )

    predicted_date = (
        datetime.now() +
        timedelta(days=30 * months_needed)
    ).strftime("%d %B %Y")

    # Decision Engine

    if item_price <= current_savings:

        decision = "BUY NOW ✅"

    elif months_needed <= 3:

        decision = "WAIT A FEW MONTHS ⚠"

    else:

        decision = "EMI RECOMMENDED 📈"

    # Simple EMI

    emi_12 = round(item_price / 12, 2)
    emi_24 = round(item_price / 24, 2)

    if emi_12 <= salary * 0.20:

        emi_advice = (
            f"12 Month EMI Available "
            f"(₹{emi_12}/month)"
        )

    elif emi_24 <= salary * 0.20:

        emi_advice = (
            f"24 Month EMI Available "
            f"(₹{emi_24}/month)"
        )

    else:

        emi_advice = (
            "EMI may put pressure on your finances."
        )

    return {

        "status": True,

        "item_name": item_name,

        "item_price": item_price,

        "total_expense": round(
            total_expense,
            2
        ),

        "avg_monthly_expense": round(
            avg_monthly_expense,
            2
        ),

        "current_savings": round(
            current_savings,
            2
        ),

        "monthly_savings": round(
            monthly_savings,
            2
        ),

        "months_needed": months_needed,

        "purchase_date": predicted_date,

        "decision": decision,

        "emi_advice": emi_advice
    }


# =====================================================
# MONTHLY OVERSPENDING PREDICTION
# =====================================================

def predict_monthly_overspending(
    df,
    salary
):

    if df.empty or len(df) < 5:
        return None

    if "Date" not in df.columns:
        return None

    df["Date"] = pd.to_datetime(
        df["Date"]
    )

    now = datetime.now()

    current_month_df = df[
        (df["Date"].dt.month == now.month) &
        (df["Date"].dt.year == now.year)
    ]

    if current_month_df.empty:
        return None

    daily_spending = (
        current_month_df.groupby(
            current_month_df["Date"].dt.day
        )["Amount"]
        .sum()
        .reset_index()
    )

    daily_spending.columns = [
        "Day",
        "Amount"
    ]

    if len(daily_spending) < 3:
        return None

    X = daily_spending[["Day"]]
    y = daily_spending["Amount"]

    model = LinearRegression()

    model.fit(X, y)

    days_in_month = calendar.monthrange(
        now.year,
        now.month
    )[1]

    future_days = np.arange(
        1,
        days_in_month + 1
    ).reshape(-1, 1)

    predictions = model.predict(
        future_days
    )

    predictions = np.maximum(
        predictions,
        0
    )

    predicted_total = predictions.sum()

    confidence = max(
        model.score(X, y) * 100,
        0
    )

    overspending = (
        predicted_total > salary
    )

    cumulative = 0

    overspend_day = None

    for day, amount in zip(
        range(1, days_in_month + 1),
        predictions
    ):

        cumulative += amount

        if cumulative > salary:

            overspend_day = day
            break

    return {

        "predicted_total": round(
            predicted_total,
            2
        ),

        "overspending": overspending,

        "overspend_day": overspend_day,

        "confidence": round(
            confidence,
            2
        )
    }