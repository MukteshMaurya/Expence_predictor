import re
import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
from ml_model import smart_purchase_planner

from auth import signup_user, login_user

from database import (
    insert_expense,
    fetch_expenses,
    clear_expenses,
    delete_expense,
    update_salary,
    update_monthly_finance,
    fetch_monthly_finance
)
from style import load_css

from advisor import analyze_finances

# =====================================================
# DASHBOARD METRICS
# =====================================================

def show_dashboard_analytics(
    df_month,
    all_expenses,
    salary,
    active_month,
    category_limits,
    sym,
    username,
    categories
):

    total_expenses = (
        df_month["Amount"].sum()
        if not df_month.empty else 0
    )

    remaining_balance = salary - total_expenses

    savings_rate = (
        (remaining_balance / salary) * 100
        if salary > 0 else 0
    )

    # =====================================
    # DASHBOARD METRICS
    # =====================================

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Income",
        f"{sym}{salary:,.2f}"
    )

    col2.metric(
        "Expenses",
        f"{sym}{total_expenses:,.2f}"
    )

    col3.metric(
        "Savings",
        f"{sym}{remaining_balance:,.2f}",
        delta=f"{savings_rate:.1f}%"
    )

    if remaining_balance < 0:
        st.error("🚨 You are overspending!")

    st.markdown("---")

    # =====================================
    # ADD EXPENSE
    # =====================================

    st.subheader("➕ Add Expense")

    with st.form(
        "expense_form",
        clear_on_submit=True
    ):

        desc = st.text_input("Description")

        amount = st.number_input(
            "Amount",
            min_value=0.01,
            step=10.0
        )

        category = st.selectbox(
            "Category",
            categories
        )

        submit = st.form_submit_button(
            "Add Expense",
            use_container_width=True
        )

        if submit:

            if desc.strip():

                insert_expense(
                    username,
                    active_month,
                    desc,
                    amount,
                    category
                )

                st.success("Expense added successfully.")
                st.rerun()

            else:
                st.error("Please enter description.")

    st.markdown("---")

    # =====================================
    # BUDGET ANALYTICS
    # =====================================

    st.subheader("📊 Budget Analytics")

    if not df_month.empty:

        summary = (
            df_month.groupby("Category")["Amount"]
            .sum()
            .reset_index()
        )

        summary["Budget Limit"] = (
            summary["Category"]
            .map(category_limits)
            .fillna(0)
        )

        fig = px.bar(
            summary,
            x="Category",
            y=["Budget Limit", "Amount"],
            barmode="group",
            title="Budget vs Actual Spending"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        for _, row in summary.iterrows():

            if row["Amount"] > row["Budget Limit"]:

                st.warning(
                    f"⚠ {row['Category']} exceeded budget limit."
                )

    else:

        st.info("No expenses available for analytics.")

    st.markdown("---")

    # =====================================
    # TRANSACTION HISTORY
    # =====================================

    st.subheader("📜 Transaction History")

    if not df_month.empty:

        st.dataframe(
            df_month,
            use_container_width=True,
            hide_index=True
        )

        colA, colB = st.columns(2)

        with colA:

            delete_id = st.number_input(
                "Delete Expense ID",
                min_value=1,
                step=1
            )
            
            delete_id=int(delete_id)

            if st.button("Delete Expense"):

                delete_expense(
                    username,
                    delete_id
                )

                st.success("Expense deleted successfully.")
                st.rerun()

        with colB:

            if st.button("Clear All Expenses"):

                clear_expenses(username)

                st.success("All expenses cleared.")
                st.rerun()

    else:

        st.info("No transaction history available.")
        
        
def show_purchase_planner(
    all_expenses,
    salary,
    sym
):
    st.markdown("---")

    st.subheader("🛒 Smart Purchase Planner")

    st.write(
        "Enter the item you want to buy and let AI predict "
        "when you can comfortably afford it."
    )

    item_name = st.text_input(
        "Item Name (Laptop, Bike, Mobile, TV etc.)"
    )

    item_price = st.number_input(
    "Item Price",
    min_value=0.0,
    value=1000.0,
    step=500.0
)

    if st.button("Predict Purchase Time"):

        if item_name.strip() == "":

            st.warning("Please enter item name.")

        else:

            result = smart_purchase_planner(
                all_expenses,
                st.session_state.salary,
                item_name,
                item_price,
                st.session_state.username
            )

            if not result["status"]:

                st.error(result["message"])

            else:

                st.success(
                    f"You may buy {result['item_name']} around "
                    f"{result['purchase_date']}"
                )

                col1, col2, col3 = st.columns(3)

                with col1:

                    st.metric(
                        "Current Savings",
                        f"{sym}{result['current_savings']:,.2f}"
                    )

                with col2:

                    st.metric(
                        "Monthly Savings",
                        f"{sym}{result['monthly_savings']:,.2f}"
                    )

                with col3:

                    st.metric(
                        "Months Needed",
                        result["months_needed"]
                    )

                st.markdown("### 📊 Purchase Analysis")

                st.write(
                    f"**Total Expenses:** "
                    f"{sym}{result['total_expense']:,.2f}"
                )

                st.write(
                    f"**Average Monthly Expense:** "
                    f"{sym}{result['avg_monthly_expense']:,.2f}"
                )

                st.write(
                    f"**Target Price:** "
                    f"{sym}{result['item_price']:,.2f}"
                )

                st.write(
                    f"**Expected Purchase Date:** "
                    f"{result['purchase_date']}"
                )

                st.markdown("### 💳 EMI Advice")

                st.info(result["emi_advice"])

                st.markdown("### 🤖 AI Decision")

                if "BUY NOW" in result["decision"]:

                    st.success(result["decision"])

                elif "WAIT" in result["decision"]:

                    st.warning(result["decision"])

                else:

                    st.error(result["decision"])
                    
                    
def show_ai_advisor(
    all_expenses,
    salary,
    sym
):
    finance_df = fetch_monthly_finance(
    st.session_state.username
)
    st.markdown("---")

    st.subheader("🧠 AI Financial Advisor")

    analysis = analyze_finances(
        all_expenses,
        st.session_state.salary
    )

    st.success(analysis["status"])
    
    
    colx1, colx2, colx3 = st.columns(3)

    colx1.metric(
    "Total Income",
    f"{sym}{analysis['total_income']:,.2f}"
)

    colx2.metric(
        "Total Expenses",
        f"{sym}{analysis['total_expense']:,.2f}"
    )

    colx3.metric(
        "Savings",
        f"{sym}{analysis['savings']:,.2f}"
    )

    st.metric(
        "Financial Health",
        f"{analysis['health_score']}%"
)    # =====================================================
    # SAVINGS RATIO
    # =====================================================

    st.markdown("### 💰 Savings Ratio")

    progress_value = analysis["savings_ratio"]

    if progress_value < 0:
        progress_value = 0

    if progress_value > 100:
        progress_value = 100

    st.progress(int(progress_value))

    st.write(
        f"Savings Ratio: "
        f"{analysis['savings_ratio']}%"
    )

    if analysis["savings"] < 0:

        st.error(
            "⚠ You are currently spending more than your income."
        )

    else:

        st.success(
            "✅ Your savings are in a healthy range."
        )

    # =====================================================
    # CATEGORY ANALYSIS
    # =====================================================

    st.markdown("### 📊 Expense Breakdown")

    if analysis["category_summary"]:

        category_df = pd.DataFrame(
            list(
                analysis["category_summary"].items()
            ),
            columns=["Category", "Amount"]
        )

        st.dataframe(
            category_df,
            use_container_width=True
        )

        pie_fig = px.pie(
            category_df,
            names="Category",
            values="Amount",
            title="Expense Distribution"
        )

        st.plotly_chart(
            pie_fig,
            use_container_width=True
        )

    # =====================================================
    # RECOMMENDED BUDGET
    # =====================================================

    st.markdown("### 💡 Recommended Budget")

    budget_df = pd.DataFrame(
        list(
            analysis["recommended_budget"].items()
        ),
        columns=[
            "Budget Type",
            "Suggested Amount"
        ]
    )

    st.dataframe(
        budget_df,
        use_container_width=True
    )

    # =====================================================
    # SMART RECOMMENDATIONS
    # =====================================================

    st.markdown("### 🤖 AI Recommendations")

    for rec in analysis["recommendations"]:

        if "⚠" in rec or "❌" in rec or "🚨" in rec:

            st.warning(rec)

        elif "✅" in rec:

            st.success(rec)

        else:

            st.info(rec)

    
    

    
# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="AI Finance Advisor",
    page_icon="📈",
    layout="wide"
)

try:
    load_css()
except:
    pass


# =====================================================
# SESSION STATE
# =====================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "salary" not in st.session_state:
    st.session_state.salary = 0.0

if "currency" not in st.session_state:
    st.session_state.currency = "₹"


# =====================================================
# CONSTANTS
# =====================================================

CURRENCY_SYMBOLS = {
    "USD ($)": "$",
    "EUR (€)": "€",
    "GBP (£)": "£",
    "INR (₹)": "₹",
    "JPY (¥)": "¥"
}

CATEGORIES = [
    "Housing",
    "Food",
    "Utilities",
    "Entertainment",
    "Transport",
    "Shopping",
    "Other"
]


# =====================================================
# AUTH NAVIGATION
# =====================================================

if not st.session_state.logged_in:

    menu = st.sidebar.selectbox(
        "Navigation Menu",
        ["Login", "Signup"]
    )


# =====================================================
# SIGNUP PAGE
# =====================================================

if not st.session_state.logged_in and menu == "Signup":

    st.title("📝 Create Your Account")

    col1, col2 = st.columns(2)

    with col1:

        name = st.text_input("Full Name")
        email = st.text_input("Email Address")
        phone = st.text_input("Phone Number")

    with col2:

        username = st.text_input("Username")

        currency_sel = st.selectbox(
            "Preferred Currency",
            list(CURRENCY_SYMBOLS.keys())
        )

        salary = st.number_input(
            "Monthly Salary",
            min_value=0.0,
            step=100.0
        )

        password = st.text_input(
            "Password",
            type="password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password"
        )

    if st.button(
        "Create Account",
        use_container_width=True
    ):

        username_pattern = r"^[A-Za-z0-9_]+$"

        email_pattern = r"^[a-zA-Z0-9._%+-]+@gmail\.com$"

        if not all([
            name,
            email,
            phone,
            username,
            password
        ]):

            st.error("Please fill all fields.")

        elif not re.match(username_pattern, username):

            st.error(
                "Username can contain only letters, numbers and underscore."
            )

        elif not re.match(email_pattern, email):

            st.error("Email must end with @gmail.com")

        elif not phone.isdigit() or len(phone) != 10:

            st.error("Phone number must contain 10 digits.")

        elif password != confirm_password:

            st.error("Passwords do not match.")

        elif salary <= 0:

            st.error("Salary must be greater than 0.")

        else:

            symbol = CURRENCY_SYMBOLS[currency_sel]

            success, msg = signup_user(
                name,
                email,
                phone,
                username,
                password,
                salary,
                symbol
            )

            if success:

                st.success(msg)

                st.info("Now login to continue.")

            else:

                st.error(msg)


# =====================================================
# LOGIN PAGE
# =====================================================

elif not st.session_state.logged_in and menu == "Login":

    st.title("🔐 Login")

    username = st.text_input("Username")

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button(
        "Login",
        use_container_width=True
    ):

        success, user_profile = login_user(
            username,
            password
        )

        if success:

            st.session_state.logged_in = True

            st.session_state.username = username

            st.session_state.salary = float(
                user_profile.get("salary", 0)
            )

            st.session_state.currency = user_profile.get(
                "currency",
                "₹"
            )

            st.success("Login successful.")

            st.rerun()

        else:

            st.error("Invalid credentials.")


# =====================================================
# MAIN DASHBOARD
# =====================================================

if st.session_state.logged_in:

    sym = st.session_state.currency

    st.title(
        f"💰 Welcome {st.session_state.username}"
    )

    # =====================================================
    # SIDEBAR
    # =====================================================

    st.sidebar.title("⚙ Settings")
    
    # =====================================
    # SIDEBAR NAVIGATION
    # =====================================

    page = st.sidebar.radio(
        "Navigation",
        [
            "Dashboard Analytics",
            "Smart Purchase Planner",
            "AI Financial Advisor"
        ]
    )
        


    current_year = datetime.datetime.now().year

    months_list = [
        f"{datetime.date(current_year, i, 1).strftime('%B')} {current_year}"
        for i in range(1, 13)
    ]

    active_month = st.sidebar.selectbox(
        "Select Month",
        months_list,
        index=datetime.datetime.now().month - 1
    )

    st.sidebar.markdown(
        f"### Salary: {sym}{st.session_state.salary:,.2f}"
    )

    # =====================================================
    # UPDATE SALARY
    # =====================================================

    st.sidebar.markdown("---")

    st.sidebar.subheader("Update Salary")

    new_salary = st.sidebar.number_input(
        "New Salary",
        min_value=0.0,
        value=float(st.session_state.salary),
        step=100.0
    )

    if st.sidebar.button("Update Salary"):

        if new_salary > 0:

            update_salary(
                st.session_state.username,
                new_salary
            )

            st.session_state.salary = new_salary

            st.sidebar.success("Salary updated.")

            st.rerun()

    # =====================================================
    # LOGOUT
    # =====================================================

    st.sidebar.markdown("---")

    if st.sidebar.button(
        "Logout",
        use_container_width=True
    ):

        st.session_state.logged_in = False
        st.session_state.username = ""

        st.rerun()

    # =====================================================
    # CATEGORY LIMITS
    # =====================================================

    st.sidebar.markdown("---")

    st.sidebar.subheader("Budget Limits")

    category_limits = {}

    for cat in CATEGORIES:

        category_limits[cat] = st.sidebar.number_input(
            f"{cat} Limit ({sym})",
            min_value=0.0,
            value=500.0,
            step=100.0
        )

    # =====================================================
    # LOAD DATA
    # =====================================================

    all_expenses = fetch_expenses(
        st.session_state.username
    )

    if not all_expenses.empty:

        df_month = all_expenses[
            all_expenses["Month"] == active_month
        ]

    else:

        df_month = pd.DataFrame(
            columns=[
                "ID",
                "Date",
                "Month",
                "Description",
                "Amount",
                "Category"
            ]
        )

    total_expenses = (
        df_month["Amount"].sum()
        if not df_month.empty else 0
    )

    remaining_balance = (
        st.session_state.salary - total_expenses
    )

    savings_rate = (
        (remaining_balance / st.session_state.salary) * 100
        if st.session_state.salary > 0 else 0
    )

    update_monthly_finance(
        st.session_state.username,
        active_month,
        st.session_state.salary,
        total_expenses
    )

    if page == "Dashboard Analytics":

        show_dashboard_analytics(
            df_month,
            all_expenses,
            st.session_state.salary,
            active_month,
            category_limits,
            sym,
            st.session_state.username,
            CATEGORIES
        )

    elif page == "AI Financial Advisor":

        show_ai_advisor(
            all_expenses,
            st.session_state.salary,
            sym
        )

    elif page == "Smart Purchase Planner":

        show_purchase_planner(
            all_expenses,
            st.session_state.salary,
            sym
        )