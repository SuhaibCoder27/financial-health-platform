CREATE TABLE IF NOT EXISTS analysis_results (
    id SERIAL PRIMARY KEY,
    total_revenue BIGINT,
    total_expenses BIGINT,
    profit BIGINT,
    profit_margin FLOAT,
    cash_flow_ratio FLOAT,
    debt_ratio FLOAT,
    financial_health_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
