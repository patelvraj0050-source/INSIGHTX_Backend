"""INSIGHTX v0.4 professional BI layer utilities."""
from __future__ import annotations

import numpy as np
import pandas as pd


def _numeric(df: pd.DataFrame, column: str | None) -> pd.Series:
    if not column or column not in df.columns:
        return pd.Series(index=df.index, dtype=float)
    return pd.to_numeric(df[column], errors="coerce")


def kpi_hierarchy(df: pd.DataFrame, mapping: dict) -> dict:
    """Return a compact executive KPI hierarchy from detected business fields."""
    revenue = _numeric(df, mapping.get("revenue"))
    profit = _numeric(df, mapping.get("profit"))
    cost = _numeric(df, mapping.get("cost"))
    quantity = _numeric(df, mapping.get("quantity"))

    result = {
        "Financial performance": {},
        "Operational performance": {},
        "Profitability": {},
    }
    if revenue.notna().any():
        result["Financial performance"]["Total Revenue"] = float(revenue.sum())
        result["Financial performance"]["Average Transaction Value"] = float(revenue.mean())
    if quantity.notna().any():
        result["Operational performance"]["Total Quantity"] = float(quantity.sum())
        result["Operational performance"]["Average Quantity"] = float(quantity.mean())
    if cost.notna().any():
        result["Operational performance"]["Total Cost"] = float(cost.sum())
    if profit.notna().any():
        result["Profitability"]["Total Profit"] = float(profit.sum())
        result["Profitability"]["Average Profit"] = float(profit.mean())
    if revenue.notna().any() and profit.notna().any() and revenue.sum() != 0:
        result["Profitability"]["Profit Margin"] = float(profit.sum() / revenue.sum() * 100)
    return {group: values for group, values in result.items() if values}


def contribution_table(df: pd.DataFrame, dimension: str, metric: str) -> pd.DataFrame:
    """Rank segments by value and calculate share and cumulative contribution."""
    if dimension not in df.columns or metric not in df.columns:
        return pd.DataFrame()
    data = pd.DataFrame({
        "Segment": df[dimension].fillna("Unknown").astype(str),
        "Value": pd.to_numeric(df[metric], errors="coerce"),
    }).dropna(subset=["Value"])
    if data.empty:
        return pd.DataFrame()
    out = data.groupby("Segment", as_index=False)["Value"].sum().sort_values("Value", ascending=False)
    total = out["Value"].sum()
    out["Share %"] = np.where(total != 0, out["Value"] / total * 100, 0.0)
    out["Cumulative Share %"] = out["Share %"].cumsum()
    out["Rank"] = np.arange(1, len(out) + 1)
    return out[["Rank", "Segment", "Value", "Share %", "Cumulative Share %"]].reset_index(drop=True)


def executive_summary(df: pd.DataFrame, mapping: dict) -> list[str]:
    """Generate cautious, data-derived executive statements."""
    statements: list[str] = []
    revenue_col = mapping.get("revenue")
    profit_col = mapping.get("profit")
    dimension = mapping.get("dimension")

    revenue = _numeric(df, revenue_col)
    profit = _numeric(df, profit_col)
    if revenue.notna().any():
        statements.append(f"The dataset contains {len(df):,} records with total revenue of {revenue.sum():,.2f}.")
    if revenue.notna().any() and profit.notna().any() and revenue.sum() != 0:
        margin = profit.sum() / revenue.sum() * 100
        statements.append(f"Overall profit margin is {margin:.2f}% based on the available revenue and profit fields.")
    if dimension and dimension in df.columns and revenue_col:
        ranked = contribution_table(df, dimension, revenue_col)
        if not ranked.empty:
            top = ranked.iloc[0]
            statements.append(f"The leading {dimension} segment is '{top['Segment']}', contributing {top['Share %']:.2f}% of total revenue.")
            if len(ranked) >= 3:
                top_three = ranked.head(3)["Share %"].sum()
                statements.append(f"The top three {dimension} segments together contribute {top_three:.2f}% of total revenue.")
    return statements


def recommendations(df: pd.DataFrame, mapping: dict) -> list[dict]:
    """Produce transparent recommendation cards based on observed patterns."""
    output: list[dict] = []
    revenue_col = mapping.get("revenue")
    profit_col = mapping.get("profit")
    dimension = mapping.get("dimension")

    if dimension and revenue_col:
        ranked = contribution_table(df, dimension, revenue_col)
        if len(ranked) >= 2:
            output.append({
                "priority": "Focus",
                "title": f"Protect the leading {dimension} segment",
                "detail": f"'{ranked.iloc[0]['Segment']}' generates {ranked.iloc[0]['Share %']:.2f}% of revenue. Review retention, availability, and service levels for this segment.",
            })
            output.append({
                "priority": "Explore",
                "title": f"Investigate lower-contribution {dimension} segments",
                "detail": f"The bottom segment contributes {ranked.iloc[-1]['Share %']:.2f}% of revenue. Check whether pricing, distribution, or demand explains the gap.",
            })

    if revenue_col and profit_col:
        revenue = _numeric(df, revenue_col)
        profit = _numeric(df, profit_col)
        valid = pd.DataFrame({"revenue": revenue, "profit": profit}).dropna()
        if not valid.empty and valid["revenue"].sum() != 0:
            margin = valid["profit"].sum() / valid["revenue"].sum() * 100
            if margin < 0:
                output.append({"priority": "Risk", "title": "Review negative profitability", "detail": "Aggregate profit is negative relative to revenue. Inspect costs, discounts, returns, and loss-making segments."})
            elif margin < 10:
                output.append({"priority": "Watch", "title": "Monitor thin margins", "detail": f"The aggregate margin is {margin:.2f}%. Analyze discounting and cost drivers before scaling volume."})
            else:
                output.append({"priority": "Opportunity", "title": "Use margin as a growth guardrail", "detail": f"The aggregate margin is {margin:.2f}%. Compare segment-level margins to find growth areas that preserve profitability."})
    return output
