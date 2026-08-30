# 💰 FinSage

### Personal Finance Tracker & Analytics Dashboard

FinSage is a Python-based personal finance management application that helps users track their income and expenses, manage accounts and categories, analyze financial activity, and generate actionable financial insights.

🔴 **Live Demo:** https://finsage-26.streamlit.app/

---

## 🚀 Overview

FinSage provides a simple and interactive way to manage personal finances from a single dashboard.

Users can create their own account, add financial accounts, record income and expenses, organize transactions using custom categories, analyze spending patterns, and receive automated insights based on their financial activity.

The application is designed with **user-specific data isolation**, ensuring that each user's financial data is associated with their own account.

---

## ✨ Features

### 🔐 Authentication
- User registration and login
- Password-based authentication
- User-specific data access
- Automatic database initialization

### 🏦 Account Management
- Create financial accounts
- Add bank/institution information
- Support multiple account types
- Track opening and current balances

### 🏷️ Category Management
- Built-in transaction categories
- Create custom categories
- Separate categories for income and expenses

### 💸 Transaction Management
- Add income and expense transactions
- Assign transactions to accounts and categories
- Add merchants and descriptions
- Edit existing transactions
- Soft-delete transactions
- Restore deleted transactions
- View complete transaction history

### 🔍 Transaction Filtering
Filter transactions by:
- Income / Expense
- Account
- Category
- Date range

### 📊 Analytics
- Total income
- Total expenses
- Net cash flow
- Expense breakdown by category
- Income vs expense trend
- Top spending categories

### 🧠 Financial Insights
FinSage automatically generates explainable insights such as:
- Cash-flow status
- Highest spending category
- Largest expense
- Uncategorized transactions
- Average expense
- Spending recommendations

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core application logic |
| Streamlit | Web application interface |
| SQLite | Local data persistence |
| Pandas | Data analysis and processing |
| Git | Version control |
| GitHub | Source code hosting |
| Streamlit Community Cloud | Deployment |

---

## 🏗️ Project Structure

```text
FinSage/
│
├── app.py
│
├── app/
│   ├── database/
│   │   ├── connection.py
│   │   └── models.py
│   │
│   ├── auth/
│   │   └── ...
│   │
│   ├── accounts/
│   │   └── ...
│   │
│   ├── categories/
│   │   └── ...
│   │
│   └── transactions/
│       └── ...
│
├── data/
│   └── finsage.db
│
├── tests/
│
├── requirements.txt
├── init_db.py
├── .gitignore
└── README.md
