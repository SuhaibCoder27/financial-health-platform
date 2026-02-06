from psycopg2 import connect

def get_db_connection():
    return connect(
        dbname="mydb",
        user="postgres",
        password="2709",
        host="localhost",
        port="5432"
    )


def save_analysis(data):
    conn = get_db_connection()
    cur = conn.cursor()

    # ✅ convert numpy → python types
    total_revenue = int(data["total_revenue"])
    total_expenses = int(data["total_expenses"])
    profit = int(data["profit"])

    profit_margin = float(data["profit"] / data["total_revenue"]) if data["total_revenue"] else 0
    cash_flow_ratio = float(data["total_revenue"] / data["total_expenses"]) if data["total_expenses"] else 0
    debt_ratio = float(0)  # already handled in engine

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
