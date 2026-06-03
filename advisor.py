import pandas as pd


def analyze_finances(df, salary):

    if df.empty:

        return {
            "status": "No expense data found.",
            "recommendations": [],
            "health_score": 0,
            "savings": salary
        }

    total_expense = df["Amount"].sum()
    
    
    months_count = df["Month"].nunique()

    total_income = salary * months_count

    savings = total_income - total_expense

    savings_ratio = (
    (savings / total_income) * 100
    if total_income > 0 else 0
)

    recommendations = []

    # =====================================================
    # CATEGORY ANALYSIS
    # =====================================================

    category_summary = (
        df.groupby("Category")["Amount"]
        .sum()
        .to_dict()
    )

    # =====================================================
    # FOOD ANALYSIS
    # =====================================================

    food_expense = category_summary.get("Food", 0)

    if food_expense > salary * 0.30:

        recommendations.append(
            "⚠ Food expenses are too high. Try reducing outside food orders."
        )

    else:

        recommendations.append(
            "✅ Food spending is under control."
        )

    # =====================================================
    # SHOPPING ANALYSIS
    # =====================================================

    shopping_expense = category_summary.get("Shopping", 0)

    if shopping_expense > salary * 0.20:

        recommendations.append(
            "⚠ Shopping expenses are high. Avoid unnecessary purchases."
        )

    else:

        recommendations.append(
            "✅ Shopping expenses are balanced."
        )

    # =====================================================
    # ENTERTAINMENT ANALYSIS
    # =====================================================

    entertainment = category_summary.get(
        "Entertainment",
        0
    )

    if entertainment > salary * 0.15:

        recommendations.append(
            "⚠ Entertainment expenses are high."
        )

    # =====================================================
    # SAVINGS ANALYSIS
    # =====================================================

    if savings_ratio < 10:

        recommendations.append(
            "❌ Your savings ratio is very low."
        )

    elif savings_ratio < 20:

        recommendations.append(
            "⚠ Try improving your monthly savings."
        )

    else:

        recommendations.append(
            "✅ Good savings performance."
        )

    # =====================================================
    # INVESTMENT ADVICE
    # =====================================================

    if savings > 5000:

        invest_amount = round(savings * 0.40, 2)

        recommendations.append(
            f"📈 Suggested SIP Investment: ₹{invest_amount}"
        )

    # =====================================================
    # EMERGENCY FUND
    # =====================================================

    emergency_fund = round(salary * 6, 2)

    recommendations.append(
        f"🛡 Recommended Emergency Fund: ₹{emergency_fund}"
    )

    # =====================================================
    # OVESPENDING CHECK
    # =====================================================

    if total_expense > salary:

        recommendations.append(
            "🚨 You are overspending your monthly income."
        )

    # =====================================================
    # FINANCIAL HEALTH SCORE
    # =====================================================

    health_score = 100

    if total_expense > salary:
        health_score -= 40

    if savings_ratio < 10:
        health_score -= 30

    if food_expense > salary * 0.30:
        health_score -= 15

    if shopping_expense > salary * 0.20:
        health_score -= 15

    health_score = max(0, health_score)

    # =====================================================
    # SMART BUDGET RECOMMENDATION
    # =====================================================

    recommended_budget = {
        "Needs": round(salary * 0.50, 2),
        "Wants": round(salary * 0.30, 2),
        "Savings": round(salary * 0.20, 2)
    }

    return {

        "status": "Analysis Completed",
        
        "total_income": round(total_income, 2),

        "total_expense": round(total_expense, 2),

        "savings": round(savings, 2),

        "savings_ratio": round(savings_ratio, 2),

        "health_score": health_score,

        "category_summary": category_summary,

        "recommended_budget": recommended_budget,

        "recommendations": recommendations
    }

