import pandas as pd
import os
from sklearn.linear_model import LinearRegression
from bank_api import fetch_bank_data
from gst_api import fetch_gst_data


# ---------------- SMART COLUMN DETECTOR ---------------- #
def get_column(df, possible_names, optional=False):
    for col in possible_names:
        if col in df.columns:
            return col
    if optional:
        return None
    return None   # never crash


# ---------------- MAIN FINANCIAL ENGINE ---------------- #
def financial_analysis(file_path, industry="Retail"):

    ext = os.path.splitext(file_path)[1].lower()
    df = pd.read_csv(file_path) if ext == ".csv" else pd.read_excel(file_path)

    # ---------- CLEAN CSV SAFELY ---------- #
    df = df.dropna(how="all")   # remove empty rows
    df = df.fillna(0)           # fill missing cells with 0

    # ---------- AUTO MAP COLUMNS ---------- #
    revenue_col = get_column(df, ["revenue", "cash_in", "income", "sales"])
    expense_col = get_column(df, ["expenses", "cash_out", "cost", "spending"])

    receivable_col = get_column(df, ["accounts_receivable", "receivables"], optional=True)
    payable_col = get_column(df, ["accounts_payable", "payables"], optional=True)

    loan_col = get_column(df, ["loan_amount", "loan_balance", "debt"], optional=True)
    inventory_col = get_column(df, ["inventory_value", "inventory"], optional=True)

    # ---------- CORE CALCULATIONS ---------- #
    total_revenue = df[revenue_col].sum() if revenue_col else 0
    total_expenses = df[expense_col].sum() if expense_col else 0

    profit = total_revenue - total_expenses

    profit_margin = profit / total_revenue if total_revenue else 0
    cash_flow_ratio = total_revenue / total_expenses if total_expenses else 0

    debt_ratio = (
        df[loan_col].mean() / total_revenue
        if loan_col and total_revenue else 0
    )

    financial_health_score = round(
        (profit_margin * 40)
        + (cash_flow_ratio * 30)
        + ((1 - debt_ratio) * 30),
        2
    )

    # ---------- REVENUE FORECAST ---------- #
    if revenue_col:
        df["month_index"] = range(1, len(df) + 1)
        model = LinearRegression()
        model.fit(df[["month_index"]], df[revenue_col])
        forecasted_revenue = model.predict([[len(df) + 1]])[0]
    else:
        forecasted_revenue = 0

    # ---------- WORKING CAPITAL ---------- #
    avg_receivable = df[receivable_col].mean() if receivable_col else 0
    avg_payable = df[payable_col].mean() if payable_col else 0
    working_capital_gap = avg_receivable - avg_payable

    # ---------- INVENTORY ---------- #
    avg_inventory = df[inventory_col].mean() if inventory_col else 0

    # ---------- TAX ESTIMATION ---------- #
    estimated_gst = total_revenue * 0.18
    tax_deduction = total_revenue * 0.02
    net_tax_payable = estimated_gst - tax_deduction

    # ---------- EXTERNAL APIs ---------- #
    banking_api_data = fetch_bank_data()
    gst_filing_data = fetch_gst_data()

    # ---------- CREDIT RATING ---------- #
    if financial_health_score >= 75:
        credit_rating = "Low Risk"
    elif financial_health_score >= 50:
        credit_rating = "Medium Risk"
    else:
        credit_rating = "High Risk"

    # ---------- RISK ENGINE ---------- #
    risks = []
    recommendations = []

    if working_capital_gap > 0:
        risks.append("High receivables locking business cash flow")
        recommendations.append("Improve collection cycle and invoice follow-ups")

    if cash_flow_ratio < 1.2:
        risks.append("Expenses approaching revenue levels")
        recommendations.append("Reduce operational costs and boost sales")

    if debt_ratio > 0.4:
        risks.append("Heavy dependency on loans")
        recommendations.append("Reduce debt and restructure liabilities")

    if not risks:
        risks.append("Financial position is stable")
        recommendations.append("Maintain current performance strategy")

    # ---------- INVESTOR SUMMARY ---------- #
    investor_summary = (
        f"The {industry} business generated total revenue of {int(total_revenue)} "
        f"with net profit of {int(profit)}. "
        f"It maintains a financial health score of {financial_health_score}, "
        f"indicating {credit_rating} investment risk. "
        f"With steady growth forecasts and manageable liabilities, "
        f"the business shows strong long-term potential."
    )

    # ---------- FINAL OUTPUT ---------- #
    return {
        "industry": industry,
        "total_revenue": int(total_revenue),
        "total_expenses": int(total_expenses),
        "profit": int(profit),
        "financial_health_score": financial_health_score,
        "forecasted_revenue_next_month": int(forecasted_revenue),
        "avg_inventory": int(avg_inventory),
        "estimated_gst": int(estimated_gst),
        "tax_deduction": int(tax_deduction),
        "net_tax_payable": int(net_tax_payable),
        "tax_compliance_status": "Compliant (Estimated)",
        "credit_rating": credit_rating,
        "banking_api_data": banking_api_data,
        "gst_filing_data": gst_filing_data,
        "investor_summary": investor_summary,
        "risks": risks,
        "recommendations": recommendations,
    }
