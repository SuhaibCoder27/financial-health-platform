import os
from psycopg2 import connect

def get_db_connection():
    # If running in cloud (Render/production) → skip DB
    if os.environ.get("RENDER"):
        return None

    return connect(
        dbname="mydb",
        user="postgres",
        password="2709",
        host="localhost",
        port="5432"
    )


def save_analysis(data):
    conn = get_db_connection()

    # 🚫 No DB in cloud → safely skip saving
    if conn is None:
        print("Cloud environment detected — skipping DB save")
        return

    cur = conn.cursor()

    total_revenue = int(data["total_revenue"])
    total_expenses = int(data["total_expenses"])
    profit = int(data["profit"])

    profit_margin = float(profit / total_revenue) if total_revenue else 0
    cash_flow_ratio = float(total_revenue / total_expenses) if total_expenses else 0
    debt_ratio = 0
    health_score = float(data["financial_health_score"])

    cur.execute("""
        INSERT INTO analysis_results (
            industry,
            total_revenue,
            total_expenses,
            profit,
            profit_margin,
            cash_flow_ratio,
            debt_ratio,
            financial_health_score,
            credit_rating
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        data["industry"],
        total_revenue,
        total_expenses,
        profit,
        profit_margin,
        cash_flow_ratio,
        debt_ratio,
        health_score,
        data["credit_rating"]
    ))

    conn.commit()
    cur.close()
    conn.close()
