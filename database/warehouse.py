
import pandas as pd
from sqlalchemy import text

DDL = [
    """CREATE TABLE IF NOT EXISTS dim_date (
        date_key INTEGER PRIMARY KEY,
        full_date DATE UNIQUE NOT NULL,
        year INTEGER NOT NULL,
        quarter INTEGER NOT NULL,
        month INTEGER NOT NULL,
        month_name VARCHAR(20) NOT NULL,
        week INTEGER NOT NULL
    )""",
    """CREATE TABLE IF NOT EXISTS dim_customer (
        customer_key BIGSERIAL PRIMARY KEY,
        customer_id VARCHAR(255) UNIQUE NOT NULL,
        customer_segment VARCHAR(255)
    )""",
    """CREATE TABLE IF NOT EXISTS dim_product (
        product_key BIGSERIAL PRIMARY KEY,
        product_name VARCHAR(255) UNIQUE NOT NULL,
        category VARCHAR(255)
    )""",
    """CREATE TABLE IF NOT EXISTS dim_region (
        region_key BIGSERIAL PRIMARY KEY,
        region_name VARCHAR(255) UNIQUE NOT NULL,
        state_name VARCHAR(255)
    )""",
    """CREATE TABLE IF NOT EXISTS fact_sales (
        sales_key BIGSERIAL PRIMARY KEY,
        order_id VARCHAR(255),
        date_key INTEGER REFERENCES dim_date(date_key),
        customer_key BIGINT REFERENCES dim_customer(customer_key),
        product_key BIGINT REFERENCES dim_product(product_key),
        region_key BIGINT REFERENCES dim_region(region_key),
        sales NUMERIC,
        quantity NUMERIC,
        discount NUMERIC,
        cost NUMERIC,
        profit NUMERIC
    )"""
]

def initialize_warehouse(engine):
    with engine.begin() as conn:
        for statement in DDL:
            conn.execute(text(statement))

def _append_unique(engine, table, frame, unique_col):
    if frame.empty:
        return
    try:
        frame.to_sql(table, engine, if_exists="append", index=False, method="multi")
    except Exception:
        # Safe for repeated demo loads: existing dimension keys are retained.
        pass

def load_star_schema(df, mapping, engine):
    initialize_warehouse(engine)
    x = df.copy()
    date_col = mapping.get("date")
    customer_col = mapping.get("customer_id")
    product_col = mapping.get("product")
    category_col = mapping.get("category")
    region_col = mapping.get("region")
    state_col = mapping.get("state")
    order_col = mapping.get("order_id")

    if customer_col:
        cols = [customer_col] + ([mapping.get("customer_segment")] if mapping.get("customer_segment") else [])
        c = x[[z for z in cols if z]].copy()
        c[customer_col] = c[customer_col].astype(str)
        c = c.drop_duplicates(customer_col)
        c = c.rename(columns={customer_col: "customer_id"})
        if mapping.get("customer_segment"):
            c = c.rename(columns={mapping["customer_segment"]: "customer_segment"})
        _append_unique(engine, "dim_customer", c, "customer_id")

    if product_col:
        cols = [product_col] + ([category_col] if category_col else [])
        p = x[cols].dropna(subset=[product_col]).copy()
        p[product_col] = p[product_col].astype(str)
        p = p.drop_duplicates(product_col).rename(columns={product_col: "product_name"})
        if category_col:
            p = p.rename(columns={category_col: "category"})
        _append_unique(engine, "dim_product", p, "product_name")

    if region_col:
        cols = [region_col] + ([state_col] if state_col else [])
        r = x[cols].dropna(subset=[region_col]).copy()
        r[region_col] = r[region_col].astype(str)
        r = r.drop_duplicates(region_col).rename(columns={region_col: "region_name"})
        if state_col:
            r = r.rename(columns={state_col: "state_name"})
        _append_unique(engine, "dim_region", r, "region_name")

    if date_col:
        dates = pd.to_datetime(x[date_col], errors="coerce").dropna().dt.normalize().drop_duplicates()
        d = pd.DataFrame({"full_date": dates})
        d["date_key"] = d["full_date"].dt.strftime("%Y%m%d").astype(int)
        d["year"] = d["full_date"].dt.year
        d["quarter"] = d["full_date"].dt.quarter
        d["month"] = d["full_date"].dt.month
        d["month_name"] = d["full_date"].dt.month_name()
        d["week"] = d["full_date"].dt.isocalendar().week.astype(int)
        _append_unique(engine, "dim_date", d, "date_key")

    # Full-file refresh keeps the demo deterministic and prevents duplicate facts.
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE fact_sales RESTART IDENTITY"))

    fact = pd.DataFrame(index=x.index)
    fact["order_id"] = x[order_col].astype(str) if order_col else None
    if date_col:
        dt = pd.to_datetime(x[date_col], errors="coerce").dt.normalize()
        fact["date_key"] = dt.dt.strftime("%Y%m%d").where(dt.notna()).astype("Int64")
    else:
        fact["date_key"] = None

    def lookup_keys(table, source_col, value_col, key_col):
        if not source_col:
            return pd.Series([None] * len(x), index=x.index)
        lookup = pd.read_sql(f"SELECT {value_col}, {key_col} FROM {table}", engine)
        return x[source_col].astype(str).map(dict(zip(lookup[value_col].astype(str), lookup[key_col])))

    fact["customer_key"] = lookup_keys("dim_customer", customer_col, "customer_id", "customer_key")
    fact["product_key"] = lookup_keys("dim_product", product_col, "product_name", "product_key")
    fact["region_key"] = lookup_keys("dim_region", region_col, "region_name", "region_key")

    for target, source in [
        ("sales", mapping.get("revenue")), ("quantity", mapping.get("quantity")),
        ("discount", mapping.get("discount")), ("cost", mapping.get("cost")),
        ("profit", mapping.get("profit"))
    ]:
        fact[target] = pd.to_numeric(x[source], errors="coerce") if source else None

    fact = fact[["order_id","date_key","customer_key","product_key","region_key",
                 "sales","quantity","discount","cost","profit"]]
    fact.to_sql("fact_sales", engine, if_exists="append", index=False, method="multi")
    return len(fact)
