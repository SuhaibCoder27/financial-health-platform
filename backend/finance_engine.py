import pandas as pd
import os
from sklearn.linear_model import LinearRegression
from bank_api import fetch_bank_data
from gst_api import fetch_gst_data


# -------- SMART COLUMN FINDER -------- #
def get_column(df, names):
    for n in names:
        if n in df.columns:
            return n
    return None


# -------- MAIN ANALYSIS -------- #
def financial_analysis(file_path, industry="Retail"):

    ext = os.path.splitext(file_path)[1].lower()
    df = pd.read_csv(file_path) if ext == ".csv" else pd.read_excel(file_path)

    # ✅ FULL DATA CLEANING
    df = df.dropna(how="all")
    df = df.fillna(0)

    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.fillna(0)

    revenue_col = get_column(df, ["revenue", "cash_in", "income", "sales"])
    expense_col = get_column(df, ["expenses", "cash_out", "cost", "spending"])
    receivable_col = get_column(df, ["accounts_receivable", "receivables"])
    payable_col = get_column(df, ["accounts_payable", "payables"])
    loan_col = get_column(df, ["loan_amount", "loan_balance", "debt"])
    inventory_col = get_column(df, ["inventory_value", "inventory"])

    total_revenue = df[revenue_col].sum() if revenue_col else 0
    total_expenses = df[expense_col].sum() if expense_col else 0
    profit = total_revenue - total_expenses

    profit_margin = profit / total_revenue if total_revenue else 0
    cash_flow_ratio = total_revenue / total_expenses if total_expenses else 0
    debt_ratio = df[loan_col].mean() / total_revenue if loan_col and total_revenue else 0

    health_score = round(
        profit_margin * 40 +
        cash_flow_ratio * 30 +
        (1 - debt_ratio) * 30,
        2
    )

    if revenue_col and len(df) > 1:
        df["month_index"] = range(1, len(df) + 1)
        model = LinearRegression()
        model.fit(df[["month_index"]], df[revenue_col])
        forecast = model.predict([[len(df) + 1]])[0]
    else:
        forecast = 0

    avg_receivable = df[receivable_col].mean() if receivable_col else 0
    avg_payable = df[payable_col].mean() if payable_col else 0
    working_gap = avg_receivable - avg_payable

    avg_inventory = df[inventory_col].mean() if inventory_col else 0

    estimated_gst = total_revenue * 0.18
    tax_deduction = total_revenue * 0.02
    net_tax = estimated_gst - tax_deduction

    fetch_bank_data()
    fetch_gst_data()

    if health_score >= 75:
        rating = "Low Risk"
    elif health_score >= 50:
        rating = "Medium Risk"
    else:
        rating = "High Risk"

    risks = []
    recs = []

    if working_gap > 0:
        risks.append("Receivables blocking cash flow")
        recs.append("Improve collections")

    if cash_flow_ratio < 1.2:
        risks.append("High expenses")
        recs.append("Control costs")

    if debt_ratio > 0.4:
        risks.append("High debt exposure")
        recs.append("Reduce liabilities")

    if not risks:
        risks.append("Stable financial position")
        recs.append("Maintain strategy")

    summary = (
        f"The {industry} business generated total revenue of {int(total_revenue)} "
        f"with net profit of {int(profit)}. Health score {health_score} indicating {rating}. "
        f"Strong long-term potential."
    )

    return {
        "industry": industry,
        "total_revenue": int(total_revenue),
        "total_expenses": int(total_expenses),
        "profit": int(profit),
        "financial_health_score": health_score,
        "forecasted_revenue_next_month": int(forecast),
        "avg_inventory": int(avg_inventory),
        "estimated_gst": int(estimated_gst),
        "tax_deduction": int(tax_deduction),
        "net_tax_payable": int(net_tax),
        "tax_compliance_status": "Compliant (Estimated)",
        "credit_rating": rating,
        "banking_api_data": {},
        "gst_filing_data": {},
        "investor_summary": summary,
        "risks": risks,
        "recommendations": recs
    }
