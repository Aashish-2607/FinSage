import streamlit as st
import pandas as pd
from app.database.models import initialize_database

from app.auth import login_user, register_user
from app.accounts.service import (
    get_accounts,
    create_account,
    create_institution,
)
from app.accounts.balance import get_account_balance
from app.transactions.service import (
    create_transaction,
    get_transactions,
    get_transaction_summary,
    update_transaction,
    delete_transaction,
    restore_transaction,
)

from app.categories.manager import (
    get_categories,
    create_category,
)

from datetime import date

# ============================================================
# DATABASE INITIALIZATION
# ============================================================

initialize_database()


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="FinSage",
    page_icon="💰",
    layout="wide",
)


# ============================================================
# SESSION STATE
# ============================================================

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "user_name" not in st.session_state:
    st.session_state.user_name = None


# ============================================================
# LOGIN / REGISTER
# ============================================================

if st.session_state.user_id is None:

    st.title("💰 FinSage")

    st.subheader(
        "Your Personal Finance Tracker"
    )

    st.write(
        "Track your money, understand your spending, "
        "and make smarter financial decisions."
    )

    st.divider()

    login_tab, register_tab = st.tabs(
        [
            "🔐 Login",
            "📝 Create Account",
        ]
    )

    # --------------------------------------------------------
    # LOGIN
    # --------------------------------------------------------

    with login_tab:

        st.subheader("Welcome back")

        with st.form("login_form"):

            email = st.text_input(
                "Email",
                placeholder="you@example.com",
            )

            password = st.text_input(
                "Password",
                type="password",
            )

            login_button = st.form_submit_button(
                "Login",
                use_container_width=True,
            )

        if login_button:

            if not email or not password:

                st.error(
                    "Please enter your email and password."
                )

            else:

                user = login_user(
                    email=email,
                    password=password,
                )

                if user is None:

                    st.error(
                        "Invalid email or password."
                    )

                else:

                    st.session_state.user_id = user["id"]

                    st.session_state.user_name = user[
                        "name"
                    ]

                    st.rerun()

    # --------------------------------------------------------
    # REGISTER
    # --------------------------------------------------------

    with register_tab:

        st.subheader(
            "Create your FinSage account"
        )

        with st.form("register_form"):

            name = st.text_input(
                "Name",
                placeholder="Your name",
            )

            email = st.text_input(
                "Email",
                placeholder="you@example.com",
            )

            password = st.text_input(
                "Password",
                type="password",
            )

            confirm_password = st.text_input(
                "Confirm Password",
                type="password",
            )

            register_button = st.form_submit_button(
                "Create Account",
                use_container_width=True,
            )

        if register_button:

            if not name or not email or not password:

                st.error(
                    "Please fill in all fields."
                )

            elif password != confirm_password:

                st.error(
                    "Passwords do not match."
                )

            else:

                try:

                    user_id = register_user(
                        name=name,
                        email=email,
                        password=password,
                    )

                    st.session_state.user_id = user_id

                    st.session_state.user_name = name

                    st.rerun()

                except ValueError as error:

                    st.error(str(error))


# ============================================================
# AUTHENTICATED APPLICATION
# ============================================================

else:

    user_id = st.session_state.user_id
    user_name = st.session_state.user_name


    # ========================================================
    # SIDEBAR
    # ========================================================

    st.sidebar.title("💰 FinSage")

    st.sidebar.caption(
        f"Welcome, {user_name}"
    )

    st.sidebar.divider()

    page = st.sidebar.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "🏦 Accounts",
            "💸 Transactions",
            "📊 Analytics",
            "🧠 Insights",
        ],
    )

    st.sidebar.divider()

    if st.sidebar.button(
        "🚪 Logout",
        use_container_width=True,
    ):

        st.session_state.user_id = None
        st.session_state.user_name = None

        st.rerun()


    # ========================================================
    # DASHBOARD
    # ========================================================

    if page == "🏠 Dashboard":

        st.title("🏠 Dashboard")

        st.caption(
            f"Here's your financial overview, {user_name}."
        )

        # ----------------------------------------------------
        # Financial summary
        # ----------------------------------------------------

        summary = get_transaction_summary(
            user_id=user_id
        )

        accounts = get_accounts(
            user_id=user_id
        )

        total_balance = 0.0

        for account in accounts:

            balance = get_account_balance(
                account_id=account["id"],
                user_id=user_id,
            )

            balance_value = (
                balance["current_balance"]
                .replace("₹", "")
                .replace(",", "")
            )

            total_balance += float(
                balance_value
            )

        # ----------------------------------------------------
        # Metrics
        # ----------------------------------------------------

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "Total Balance",
                f"₹{total_balance:,.2f}",
            )

        with col2:

            st.metric(
                "Total Income",
                summary["total_income"],
            )

        with col3:

            st.metric(
                "Total Expenses",
                summary["total_expense"],
            )

        with col4:

            st.metric(
                "Net Cash Flow",
                summary["net_cash_flow"],
            )

        st.divider()

        # ----------------------------------------------------
        # Accounts
        # ----------------------------------------------------

        st.subheader("🏦 Your Accounts")

        if not accounts:

            st.info(
                "You don't have any accounts yet."
            )

            st.write(
                "Go to **Accounts** to add your first "
                "bank account."
            )

        else:

            account_columns = st.columns(
                min(len(accounts), 3)
            )

            for index, account in enumerate(
                accounts
            ):

                with account_columns[
                    index % len(account_columns)
                ]:

                    balance = get_account_balance(
                        account_id=account["id"],
                        user_id=user_id,
                    )

                    st.markdown(
                        f"""
                        ### {account['account_name']}

                        **{account['institution_name']}**

                        `{account['account_type']}`

                        Current Balance

                        ## {balance['current_balance']}
                        """
                    )

        st.divider()

        if not accounts:

            st.success(
                "Welcome to FinSage! "
                "Start by adding your first account."
            )


    # ========================================================
    # ACCOUNTS
    # ========================================================

    elif page == "🏦 Accounts":

        st.title("🏦 Accounts")

        st.caption(
            "Manage your bank accounts, cards, and other financial accounts."
        )

        st.divider()

        # ====================================================
        # GET USER'S ACCOUNTS
        # ====================================================

        accounts = get_accounts(
            user_id=user_id
        )

        # ====================================================
        # ADD ACCOUNT
        # ====================================================

        with st.expander(
            "➕ Add New Account",
            expanded=not accounts,
        ):

            st.subheader("Create an account")

            # ------------------------------------------------
            # Existing institutions belonging to this user
            # ------------------------------------------------

            existing_institutions = sorted(
                {
                    account["institution_name"]
                    for account in accounts
                }
            )

            institution_mode = st.radio(
                "Bank / Institution",
                [
                    "Select existing",
                    "Enter new",
                ],
                horizontal=True,
            )

            if institution_mode == "Select existing":

                if existing_institutions:

                    institution_name = st.selectbox(
                        "Select Institution",
                        existing_institutions,
                    )

                else:

                    st.info(
                        "You don't have any institutions yet. "
                        "Enter your bank name below."
                    )

                    institution_name = st.text_input(
                        "Bank / Institution Name",
                        placeholder="e.g. SBI, HDFC Bank, Canara Bank",
                    )

            else:

                institution_name = st.text_input(
                    "Bank / Institution Name",
                    placeholder="e.g. SBI, HDFC Bank, Canara Bank",
                )

            # ------------------------------------------------
            # Account details
            # ------------------------------------------------

            account_name = st.text_input(
                "Account Name",
                placeholder="e.g. Savings Account",
            )

            account_type = st.selectbox(
                "Account Type",
                [
                    "savings",
                    "current",
                    "credit_card",
                    "cash",
                    "investment",
                    "other",
                ],
            )

            opening_balance = st.number_input(
                "Opening Balance (₹)",
                min_value=0.0,
                value=0.0,
                step=100.0,
                format="%.2f",
            )

            create_button = st.button(
                "Create Account",
                type="primary",
                use_container_width=True,
            )

            if create_button:

                if not institution_name.strip():

                    st.error(
                        "Please enter your bank / institution name."
                    )

                elif not account_name.strip():

                    st.error(
                        "Please enter an account name."
                    )

                else:

                    try:

                        # ------------------------------------
                        # Find or create institution
                        # ------------------------------------

                        institution_id = create_institution(
                            user_id=user_id,
                            name=institution_name.strip(),
                        )

                        # ------------------------------------
                        # Create account
                        # ------------------------------------

                        create_account(
                            user_id=user_id,
                            institution_id=institution_id,
                            name=account_name.strip(),
                            account_type=account_type,
                            opening_balance=opening_balance,
                        )

                        st.success(
                            f"{account_name} created successfully!"
                        )

                        st.rerun()

                    except ValueError as error:

                        st.error(str(error))

                    except Exception as error:

                        st.error(
                            f"Unable to create account: {error}"
                        )

        st.divider()

        # ====================================================
        # DISPLAY ACCOUNTS
        # ====================================================

        st.subheader("Your Accounts")

        accounts = get_accounts(
            user_id=user_id
        )

        if not accounts:

            st.info(
                "You haven't added any accounts yet."
            )

            st.write(
                "Add your first bank account above "
                "to start tracking your finances."
            )

        else:

            columns = st.columns(
                min(len(accounts), 3)
            )

            for index, account in enumerate(accounts):

                with columns[
                    index % len(columns)
                ]:

                    balance = get_account_balance(
                        account_id=account["id"],
                        user_id=user_id,
                    )

                    st.markdown(
                        f"""
                        ### 🏦 {account['account_name']}

                        **{account['institution_name']}**

                        `{account['account_type']}`

                        **Current Balance**

                        ## {balance['current_balance']}
                        """
                    )


    # ========================================================
    # TRANSACTIONS
    # ========================================================

    elif page == "💸 Transactions":

        st.title("💸 Transactions")

        st.caption(
            f"Record and manage your income and expenses, {user_name}."
        )

        st.divider()

        # ====================================================
        # TRANSACTION SUMMARY
        # ====================================================

        summary = get_transaction_summary(
            user_id=user_id
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Total Income",
                summary["total_income"],
            )

        with col2:
            st.metric(
                "Total Expenses",
                summary["total_expense"],
            )

        with col3:
            st.metric(
                "Net Cash Flow",
                summary["net_cash_flow"],
            )

        st.divider()

        # ====================================================
        # GET USER'S ACCOUNTS
        # ====================================================

        accounts = get_accounts(
            user_id=user_id
        )

        # ====================================================
        # ADD TRANSACTION
        # ====================================================

        st.subheader("➕ Add Transaction")

        if not accounts:

            st.info(
                "You don't have any accounts yet. "
                "Go to Accounts and create an account first."
            )

        else:

            transaction_type = st.radio(
                "Transaction Type",
                [
                    "expense",
                    "income",
                ],
                horizontal=True,
                format_func=lambda value: (
                    "💸 Expense"
                    if value == "expense"
                    else "💰 Income"
                ),
            )
        # ------------------------------------------------
        # Add custom category
        # ------------------------------------------------

        with st.expander("➕ Add Custom Category"):

            new_category_name = st.text_input(
                "Category Name",
                placeholder="e.g. Gaming, Gym, Travel",
                key="new_category_name",
            )

            add_category = st.button(
                "Add Category",
                use_container_width=True,
            )

            if add_category:

                category_name = new_category_name.strip()

                if not category_name:

                    st.error(
                        "Please enter a category name."
                    )

                else:

                    try:

                        create_category(
                            user_id=user_id,
                            name=category_name,
                            category_type=transaction_type,
                        )

                        st.success(
                            f"Category '{category_name}' added!"
                        )

                        st.rerun()

                    except ValueError as error:

                        st.error(str(error))

                    except Exception as error:

                        st.error(
                            f"Unable to add category: {error}"
                        )
            

            # ------------------------------------------------
            # Categories for selected transaction type
            # ------------------------------------------------

            categories = get_categories(
                user_id=user_id,
                category_type=transaction_type,
            )

            # ------------------------------------------------
            # Account selection
            # ------------------------------------------------

            account_options = {
                account["id"]: (
                    f"{account['account_name']} "
                    f"({account['institution_name']})"
                )
                for account in accounts
            }

            selected_account_id = st.selectbox(
                "Account",
                options=list(account_options.keys()),
                format_func=lambda account_id:
                    account_options[account_id],
            )

            # ------------------------------------------------
            # Category selection
            # ------------------------------------------------

            category_options = {
                None: "No Category"
            }

            for category in categories:
                category_options[category["id"]] = category["name"]

            selected_category_id = st.selectbox(
                "Category",
                options=list(category_options.keys()),
                format_func=lambda category_id:
                    category_options[category_id],
            )

            # ------------------------------------------------
            # Amount
            # ------------------------------------------------

            amount = st.number_input(
                "Amount (₹)",
                min_value=0.0,
                value=0.0,
                step=100.0,
                format="%.2f",
            )

            # ------------------------------------------------
            # Date
            # ------------------------------------------------

            transaction_date = st.date_input(
                "Transaction Date",
                value=date.today(),
            )

            # ------------------------------------------------
            # Merchant
            # ------------------------------------------------

            merchant = st.text_input(
                "Merchant",
                placeholder="e.g. Swiggy, Amazon, Uber",
            )

            # ------------------------------------------------
            # Description
            # ------------------------------------------------

            description = st.text_input(
                "Description",
                placeholder="e.g. Dinner, Monthly salary",
            )

            save_transaction = st.button(
                "💾 Save Transaction",
                type="primary",
                use_container_width=True,
            )

            if save_transaction:

                if amount <= 0:

                    st.error(
                        "Amount must be greater than ₹0."
                    )

                else:

                    try:

                        create_transaction(
                            user_id=user_id,
                            account_id=selected_account_id,
                            category_id=selected_category_id,
                            amount=amount,
                            transaction_type=transaction_type,
                            transaction_date=str(
                                transaction_date
                            ),
                            description=(
                                description.strip()
                                if description.strip()
                                else None
                            ),
                            merchant=(
                                merchant.strip()
                                if merchant.strip()
                                else None
                            ),
                        )

                        st.success(
                            "Transaction added successfully!"
                        )

                        st.rerun()

                    except ValueError as error:

                        st.error(str(error))

                    except Exception as error:

                        st.error(
                            f"Unable to save transaction: {error}"
                        )

        st.divider()

        # ============================================================
        # TRANSACTION HISTORY
        # ============================================================

        st.divider()

        st.subheader("📋 Transaction History")

        # ============================================================
        # TRANSACTION FILTERS
        # ============================================================

        st.subheader("🔍 Filter Transactions")

        filter_col1, filter_col2, filter_col3 = st.columns(3)

        with filter_col1:

            filter_type = st.selectbox(
                "Type",
                ["All", "Income", "Expense"],
                key="filter_type",
            )

        with filter_col2:

            filter_account = st.selectbox(
                "Account",
                ["All Accounts"]
                + [
                    account["account_name"]
                    for account in accounts
                ],
                key="filter_account",
            )

        with filter_col3:

            filter_category = st.selectbox(
                "Category",
                ["All Categories"]
                + [
                    category["name"]
                    for category in get_categories(
                        user_id=user_id
                    )
                ],
                key="filter_category",
            )

        date_col1, date_col2, date_col3 = st.columns(3)

        with date_col1:

            filter_start_date = st.date_input(
                "From",
                value=None,
                key="filter_start_date",
            )

        with date_col2:

            filter_end_date = st.date_input(
                "To",
                value=None,
                key="filter_end_date",
            )

        with date_col3:

            st.write("")
            st.write("")

            clear_filters = st.button(
                "🔄 Clear Filters",
                use_container_width=True,
            )

        if clear_filters:
            st.rerun()


        # ============================================================
        # RESOLVE FILTER IDs
        # ============================================================

        selected_account_id = None

        if filter_account != "All Accounts":

            for account in accounts:

                if account["account_name"] == filter_account:

                    selected_account_id = account["id"]
                    break


        selected_category_id = None

        if filter_category != "All Categories":

            all_categories = get_categories(
                user_id=user_id
            )

            for category in all_categories:

                if category["name"] == filter_category:

                    selected_category_id = category["id"]
                    break


        selected_transaction_type = None

        if filter_type == "Income":
            selected_transaction_type = "income"

        elif filter_type == "Expense":
            selected_transaction_type = "expense"


        # ============================================================
        # GET FILTERED TRANSACTIONS
        # ============================================================

        transactions = get_transactions(
            user_id=user_id,
            account_id=selected_account_id,
            category_id=selected_category_id,
            transaction_type=selected_transaction_type,
            start_date=(
                str(filter_start_date)
                if filter_start_date
                else None
            ),
            end_date=(
                str(filter_end_date)
                if filter_end_date
                else None
            ),
        )

        if not transactions:

            st.info("No transactions yet.")

        else:

            for transaction in transactions:

                transaction_id = transaction["id"]

                transaction_type = transaction.get(
                    "transaction_type",
                    ""
                )

                amount = transaction.get(
                    "amount",
                    "₹0.00"
                )

                transaction_date = transaction.get(
                    "transaction_date",
                    ""
                )

                account_name = transaction.get(
                    "account_name",
                    "Unknown Account"
                )

                category_name = transaction.get(
                    "category_name",
                    "No Category"
                )

                merchant = transaction.get(
                    "merchant",
                    ""
                )

                description = transaction.get(
                    "description",
                    ""
                )

                if transaction_type == "expense":
                    type_icon = "💸"
                else:
                    type_icon = "💰"

                with st.expander(
                    f"{type_icon} {category_name} — {amount} — {transaction_date}"
                ):

                    st.write(
                        f"**Account:** {account_name}"
                    )

                    st.write(
                        f"**Merchant:** {merchant or '—'}"
                    )

                    st.write(
                        f"**Description:** {description or '—'}"
                    )

                    st.caption(
                        f"Transaction ID: {transaction_id}"
                    )

                    st.divider()

                    # ====================================================
                    # EDIT TRANSACTION
                    # ====================================================

                    st.subheader("✏️ Edit Transaction")

                    edit_amount = st.number_input(
                        "Amount (₹)",
                        min_value=0.01,
                        value=float(
                            str(amount)
                            .replace("₹", "")
                            .replace(",", "")
                        ),
                        step=1.0,
                        key=f"edit_amount_{transaction_id}",
                    )

                    edit_date = st.date_input(
                        "Transaction Date",
                        value=transaction_date,
                        key=f"edit_date_{transaction_id}",
                    )

                    edit_merchant = st.text_input(
                        "Merchant",
                        value=merchant or "",
                        key=f"edit_merchant_{transaction_id}",
                    )

                    edit_description = st.text_input(
                        "Description",
                        value=description or "",
                        key=f"edit_description_{transaction_id}",
                    )

                    if st.button(
                        "💾 Save Changes",
                        key=f"save_edit_{transaction_id}",
                        use_container_width=True,
                    ):

                        try:

                            update_transaction(
                                transaction_id=transaction_id,
                                user_id=user_id,
                                account_id=transaction["account_id"],
                                category_id=transaction.get("category_id"),
                                amount=edit_amount,
                                transaction_type=transaction_type,
                                transaction_date=str(edit_date),
                                description=(
                                    edit_description.strip()
                                    if edit_description.strip()
                                    else None
                                ),
                                merchant=(
                                    edit_merchant.strip()
                                    if edit_merchant.strip()
                                    else None
                                ),
                            )

                            st.success(
                                "Transaction updated successfully."
                            )

                            st.rerun()

                        except Exception as error:

                            st.error(
                                f"Unable to update transaction: {error}"
                            )
                    # ====================================================
                    # DELETE TRANSACTION
                    # ====================================================

                    st.divider()

                    st.subheader("🗑️ Delete Transaction")

                    delete_transaction_button = st.button(
                        "🗑️ Delete Transaction",
                        key=f"delete_transaction_{transaction_id}",
                        use_container_width=True,
                    )

                    if delete_transaction_button:

                        try:

                            delete_transaction(
                                transaction_id=transaction_id,
                                user_id=user_id,
                            )

                            st.success(
                                "Transaction deleted successfully."
                            )

                            st.rerun()

                        except Exception as error:

                            st.error(
                                f"Unable to delete transaction: {error}"
                            )
        # ============================================================
        # DELETED TRANSACTIONS
        # ============================================================

        st.divider()

        st.subheader("♻️ Deleted Transactions")

        deleted_transactions = get_transactions(
            user_id=user_id,
            include_deleted=True,
        )

        # Keep only deleted transactions
        deleted_transactions = [
            transaction
            for transaction in deleted_transactions
            if transaction.get("is_deleted", 0) == 1
        ]

        if not deleted_transactions:

            st.info("No deleted transactions.")

        else:

            for transaction in deleted_transactions:

                transaction_id = transaction["id"]

                transaction_type = transaction.get(
                    "transaction_type",
                    ""
                )

                amount = transaction.get(
                    "amount",
                    "₹0.00"
                )

                transaction_date = transaction.get(
                    "transaction_date",
                    ""
                )

                category_name = transaction.get(
                    "category_name"
                ) or "No Category"

                account_name = transaction.get(
                    "account_name",
                    "Unknown Account"
                )

                merchant = transaction.get(
                    "merchant"
                ) or "—"

                description = transaction.get(
                    "description"
                ) or "—"

                if transaction_type == "expense":
                    type_icon = "💸"
                else:
                    type_icon = "💰"

                with st.expander(
                    f"{type_icon} {category_name} — "
                    f"{amount} — {transaction_date}"
                ):

                    st.write(
                        f"**Account:** {account_name}"
                    )

                    st.write(
                        f"**Merchant:** {merchant}"
                    )

                    st.write(
                        f"**Description:** {description}"
                    )

                    st.caption(
                        f"Transaction ID: {transaction_id}"
                    )

                    if st.button(
                        "♻️ Restore Transaction",
                        key=f"restore_{transaction_id}",
                        use_container_width=True,
                    ):

                        try:

                            restore_transaction(
                                transaction_id=transaction_id,
                                user_id=user_id,
                            )

                            st.success(
                                "Transaction restored successfully."
                            )

                            st.rerun()

                        except Exception as error:

                            st.error(
                                f"Unable to restore transaction: {error}"
                            )                    
    # ========================================================
    # ANALYTICS
    # ========================================================

    elif page == "📊 Analytics":

        st.title("📊 Analytics")

        st.caption(
            f"Understand your financial activity, {user_name}."
        )

        # ====================================================
        # GET USER TRANSACTIONS
        # ====================================================

        analytics_transactions = get_transactions(
            user_id=user_id
        )

        if not analytics_transactions:

            st.info(
                "No transaction data available yet. "
                "Add some transactions to see your analytics."
            )

        else:

            # ====================================================
            # PREPARE DATA
            # ====================================================

            analytics_data = []

            for transaction in analytics_transactions:

                amount = float(
                    str(transaction["amount"])
                    .replace("₹", "")
                    .replace(",", "")
                )

                analytics_data.append(
                    {
                        "date": transaction["transaction_date"],
                        "type": transaction["transaction_type"],
                        "amount": amount,
                        "category": (
                            transaction.get("category_name")
                            or "Uncategorized"
                        ),
                    }
                )

            df = pd.DataFrame(analytics_data)

            # ====================================================
            # SUMMARY
            # ====================================================

            total_income = df.loc[
                df["type"] == "income",
                "amount"
            ].sum()

            total_expense = df.loc[
                df["type"] == "expense",
                "amount"
            ].sum()

            net_cash_flow = (
                total_income - total_expense
            )

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "💰 Total Income",
                    f"₹{total_income:,.2f}",
                )

            with col2:

                st.metric(
                    "💸 Total Expenses",
                    f"₹{total_expense:,.2f}",
                )

            with col3:

                st.metric(
                    "📈 Net Cash Flow",
                    f"₹{net_cash_flow:,.2f}",
                )

            st.divider()

            # ====================================================
            # EXPENSE BY CATEGORY
            # ====================================================

            st.subheader("💸 Expenses by Category")

            expense_df = df[
                df["type"] == "expense"
            ]

            if expense_df.empty:

                st.info(
                    "No expense data available."
                )

            else:

                category_expenses = (
                    expense_df
                    .groupby("category")["amount"]
                    .sum()
                    .sort_values(
                        ascending=False
                    )
                )

                st.bar_chart(
                    category_expenses
                )

            st.divider()

            # ====================================================
            # INCOME VS EXPENSE TREND
            # ====================================================

            st.subheader("📊 Income vs Expenses")

            trend_df = df.copy()

            trend_df["date"] = pd.to_datetime(
                trend_df["date"]
            )

            # Create separate income and expense values
            trend_df["income"] = trend_df.apply(
                lambda row:
                    row["amount"]
                    if row["type"] == "income"
                    else 0,
                axis=1,
            )

            trend_df["expense"] = trend_df.apply(
                lambda row:
                    row["amount"]
                    if row["type"] == "expense"
                    else 0,
                axis=1,
            )

            # Group by actual transaction date
            daily_summary = (
                trend_df
                .groupby("date")[["income", "expense"]]
                .sum()
                .sort_index()
            )

            # Make sure the index is datetime
            daily_summary.index = pd.to_datetime(
                daily_summary.index
            )

            st.line_chart(
                daily_summary,
                x_label="Date",
                y_label="Amount (₹)",
            )

            # ====================================================
            # TOP SPENDING CATEGORIES
            # ====================================================

            st.subheader("🏆 Top Spending Categories")

            if expense_df.empty:

                st.info(
                    "No spending data available."
                )

            else:

                top_categories = (
                    expense_df
                    .groupby("category")["amount"]
                    .sum()
                    .sort_values(
                        ascending=False
                    )
                    .head(5)
                )

                for index, (
                    category,
                    amount,
                ) in enumerate(
                    top_categories.items(),
                    start=1,
                ):

                    st.write(
                        f"**{index}. {category}** — "
                        f"₹{amount:,.2f}"
                    )
    #==========================================================
    # INSIGHTS
    #==========================================================

    elif page == "🧠 Insights":

        st.title("🧠 FinSage Insights")

        st.caption(
            "Simple, explainable observations from your financial activity."
        )

        # ============================================================
        # GET TRANSACTIONS
        # ============================================================

        insight_transactions = get_transactions(
            user_id=user_id
        )

        if not insight_transactions:

            st.info(
                "No transactions available yet. "
                "Add some transactions to generate insights."
            )

        else:

            # ========================================================
            # PREPARE DATA
            # ========================================================

            insight_data = []

            for transaction in insight_transactions:

                amount = float(
                    str(transaction["amount"])
                    .replace("₹", "")
                    .replace(",", "")
                )

                insight_data.append(
                    {
                        "amount": amount,
                        "type": transaction["transaction_type"],
                        "category": (
                            transaction.get("category_name")
                            or "Uncategorized"
                        ),
                        "merchant": (
                            transaction.get("merchant")
                            or "Unknown"
                        ),
                        "date": transaction["transaction_date"],
                    }
                )

            insight_df = pd.DataFrame(
                insight_data
            )

            # ========================================================
            # BASIC TOTALS
            # ========================================================

            total_income = insight_df.loc[
                insight_df["type"] == "income",
                "amount"
            ].sum()

            total_expense = insight_df.loc[
                insight_df["type"] == "expense",
                "amount"
            ].sum()

            net_cash_flow = (
                total_income - total_expense
            )

            expense_df = insight_df[
                insight_df["type"] == "expense"
            ]

            income_df = insight_df[
                insight_df["type"] == "income"
            ]

            # ========================================================
            # SUMMARY
            # ========================================================

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "💰 Income",
                    f"₹{total_income:,.2f}",
                )

            with col2:

                st.metric(
                    "💸 Expenses",
                    f"₹{total_expense:,.2f}",
                )

            with col3:

                st.metric(
                    "📈 Net Flow",
                    f"₹{net_cash_flow:,.2f}",
                )

            st.divider()

            # ========================================================
            # INSIGHT 1 — CASH FLOW
            # ========================================================

            st.subheader("💡 Cash Flow")

            if net_cash_flow > 0:

                st.success(
                    f"Your income is higher than your expenses "
                    f"by ₹{net_cash_flow:,.2f}."
                )

            elif net_cash_flow < 0:

                st.warning(
                    f"Your expenses are higher than your income "
                    f"by ₹{abs(net_cash_flow):,.2f}."
                )

            else:

                st.info(
                    "Your income and expenses are currently balanced."
                )

            # ========================================================
            # INSIGHT 2 — TOP SPENDING CATEGORY
            # ========================================================

            if not expense_df.empty:

                st.subheader("🏆 Top Spending Category")

                category_totals = (
                    expense_df
                    .groupby("category")["amount"]
                    .sum()
                    .sort_values(
                        ascending=False
                    )
                )

                top_category = (
                    category_totals.index[0]
                )

                top_category_amount = (
                    category_totals.iloc[0]
                )

                expense_percentage = (
                    top_category_amount
                    / total_expense
                    * 100
                    if total_expense > 0
                    else 0
                )

                st.info(
                    f"**{top_category}** is your highest "
                    f"spending category at "
                    f"₹{top_category_amount:,.2f} "
                    f"({expense_percentage:.1f}% of total expenses)."
                )

            # ========================================================
            # INSIGHT 3 — LARGEST EXPENSE
            # ========================================================

            if not expense_df.empty:

                st.subheader("💸 Largest Expense")

                largest_expense = expense_df.loc[
                    expense_df["amount"].idxmax()
                ]

                st.write(
                    f"Your largest recorded expense is "
                    f"**₹{largest_expense['amount']:,.2f}** "
                    f"for **{largest_expense['merchant']}**."
                )

                st.caption(
                    f"Category: {largest_expense['category']} • "
                    f"Date: {largest_expense['date']}"
                )

            # ========================================================
            # INSIGHT 4 — UNCATEGORIZED TRANSACTIONS
            # ========================================================

            uncategorized = insight_df[
                insight_df["category"] == "Uncategorized"
            ]

            if not uncategorized.empty:

                st.subheader("⚠️ Uncategorized Transactions")

                uncategorized_total = (
                    uncategorized["amount"].sum()
                )

                st.warning(
                    f"You have **{len(uncategorized)}** "
                    f"uncategorized transaction(s), "
                    f"totalling ₹{uncategorized_total:,.2f}. "
                    f"Adding categories will make your analytics "
                    f"more useful."
                )

            # ========================================================
            # INSIGHT 5 — TRANSACTION ACTIVITY
            # ========================================================

            st.subheader("📋 Activity Overview")

            activity_col1, activity_col2 = st.columns(2)

            with activity_col1:

                st.metric(
                    "Total Transactions",
                    len(insight_df),
                )

            with activity_col2:

                if not expense_df.empty:

                    average_expense = (
                        expense_df["amount"].mean()
                    )

                    st.metric(
                        "Average Expense",
                        f"₹{average_expense:,.2f}",
                    )

                else:

                    st.metric(
                        "Average Expense",
                        "₹0.00",
                    )

            # ========================================================
            # RECOMMENDATION
            # ========================================================

            st.divider()

            st.subheader("🎯 FinSage Recommendation")

            if total_expense == 0:

                st.info(
                    "Start recording your expenses to receive "
                    "personalized spending insights."
                )

            elif net_cash_flow < 0:

                st.warning(
                    "Your current expenses exceed your income. "
                    "Consider reviewing your highest spending "
                    "categories and reducing non-essential expenses."
                )

            elif (
                total_expense > 0
                and total_income > 0
                and total_expense / total_income > 0.8
            ):

                st.warning(
                    "Your expenses are taking up a large portion "
                    "of your recorded income. Consider keeping "
                    "a larger portion available as savings."
                )

            else:

                st.success(
                    "Your recorded cash flow is positive. "
                    "Keep tracking consistently to understand "
                    "your spending patterns over time."
                )