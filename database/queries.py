import pandas as pd
from sqlalchemy import text

QUERIES = {
    "Revenue by Region": """
        SELECT r.region_name AS region,
               ROUND(SUM(f.sales),2) AS revenue,
               ROUND(SUM(f.profit),2) AS profit
        FROM fact_sales f
        JOIN dim_region r ON f.region_key=r.region_key
        GROUP BY r.region_name
        ORDER BY revenue DESC
    """,
    "Monthly Revenue": """
        SELECT d.year, d.month, d.month_name,
               ROUND(SUM(f.sales),2) AS revenue,
               ROUND(SUM(f.profit),2) AS profit
        FROM fact_sales f
        JOIN dim_date d ON f.date_key=d.date_key
        GROUP BY d.year,d.month,d.month_name
        ORDER BY d.year,d.month
    """,
    "Top Products": """
        SELECT p.product_name,
               ROUND(SUM(f.sales),2) AS revenue,
               ROUND(SUM(f.profit),2) AS profit
        FROM fact_sales f
        JOIN dim_product p ON f.product_key=p.product_key
        GROUP BY p.product_name
        ORDER BY revenue DESC
        LIMIT 10
    """
}

def run_query(engine, name):
    return pd.read_sql(text(QUERIES[name]), engine)
