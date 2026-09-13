-- INSIGHTX v0.2 analytical SQL
SELECT r.region_name, SUM(f.sales) AS revenue, SUM(f.profit) AS profit,
ROUND(SUM(f.profit) / NULLIF(SUM(f.sales),0) * 100, 2) AS margin_pct
FROM fact_sales f JOIN dim_region r ON f.region_key=r.region_key
GROUP BY r.region_name ORDER BY revenue DESC;

SELECT d.year, d.month, d.month_name, SUM(f.sales) AS revenue, SUM(f.profit) AS profit
FROM fact_sales f JOIN dim_date d ON f.date_key=d.date_key
GROUP BY d.year,d.month,d.month_name ORDER BY d.year,d.month;
