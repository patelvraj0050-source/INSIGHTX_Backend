"""
INSIGHTX v0.5 - AI Business Analyst engine.

This module intentionally uses deterministic, validated analytics rather than
inventing figures. It translates a small set of natural-language business
questions into safe dataframe operations and produces explainable answers.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, Optional

import pandas as pd


@dataclass
class AnalystResult:
    intent: str
    answer: str
    evidence: Dict[str, Any]
    confidence: str = "High"


def _money(value: float) -> str:
    return f"{value:,.2f}"


def _find_column(df: pd.DataFrame, candidates):
    lowered = {str(c).strip().lower(): c for c in df.columns}
    for candidate in candidates:
        if candidate in lowered:
            return lowered[candidate]
    for c in df.columns:
        name = str(c).strip().lower()
        if any(candidate in name for candidate in candidates):
            return c
    return None


def _base_columns(df):
    return {
        "revenue": _find_column(df, ["revenue", "sales", "amount", "total"]),
        "profit": _find_column(df, ["profit", "net profit", "margin"]),
        "date": _find_column(df, ["date", "order date", "transaction date"]),
        "region": _find_column(df, ["region", "territory", "area"]),
        "product": _find_column(df, ["product", "product name", "item"]),
        "category": _find_column(df, ["category", "product category"]),
        "customer": _find_column(df, ["customer", "customer id", "client"]),
    }


def answer_question(df: pd.DataFrame, question: str) -> AnalystResult:
    q = question.lower().strip()
    cols = _base_columns(df)
    revenue = cols["revenue"]
    profit = cols["profit"]

    if df is None or df.empty:
        return AnalystResult("no_data", "Please upload a non-empty dataset first.", {} , "Low")

    if not revenue:
        return AnalystResult(
            "unsupported_schema",
            "I could not find a revenue or sales column in this dataset. "
            "Please use a dataset containing a sales/revenue measure.",
            {"available_columns": list(map(str, df.columns))},
            "Low",
        )

    numeric_revenue = pd.to_numeric(df[revenue], errors="coerce")
    total_revenue = float(numeric_revenue.sum())
    count = int(numeric_revenue.notna().sum())

    # Top products
    if ("top" in q or "best" in q or "highest" in q) and ("product" in q or "item" in q):
        group_col = cols["product"] or cols["category"]
        if group_col:
            tmp = pd.DataFrame({"group": df[group_col].astype(str), "value": numeric_revenue})
            top = tmp.groupby("group", dropna=False)["value"].sum().sort_values(ascending=False).head(5)
            if len(top):
                lines = "; ".join(f"{idx}: {_money(val)}" for idx, val in top.items())
                return AnalystResult(
                    "top_products",
                    f"Top contributors by revenue are {lines}.",
                    {"rows": [{"name": str(i), "revenue": float(v)} for i, v in top.items()]},
                )

    # Regional performance
    if "region" in q or "territory" in q or "area" in q:
        group_col = cols["region"]
        if group_col:
            tmp = pd.DataFrame({"group": df[group_col].astype(str), "value": numeric_revenue})
            grouped = tmp.groupby("group", dropna=False)["value"].sum().sort_values(ascending=False)
            if len(grouped):
                leader = str(grouped.index[0])
                share = float(grouped.iloc[0] / total_revenue * 100) if total_revenue else 0
                return AnalystResult(
                    "regional_performance",
                    f"{leader} is the leading region by revenue at {_money(grouped.iloc[0])}, "
                    f"representing {share:.1f}% of total revenue.",
                    {"leader": leader, "revenue": float(grouped.iloc[0]), "share_percent": share},
                )

    # Profitability
    if "profit" in q or "profitable" in q or "margin" in q:
        if profit:
            p = pd.to_numeric(df[profit], errors="coerce")
            total_profit = float(p.sum())
            margin = total_profit / total_revenue * 100 if total_revenue else 0
            return AnalystResult(
                "profitability",
                f"Total profit is {_money(total_profit)} with an estimated profit-to-revenue "
                f"ratio of {margin:.1f}%.",
                {"total_profit": total_profit, "profit_ratio_percent": margin},
            )
        return AnalystResult(
            "missing_profit",
            "I found revenue/sales but no profit column, so profitability cannot be calculated.",
            {},
            "Medium",
        )

    # Monthly trend / change
    if ("month" in q or "trend" in q or "change" in q or "last month" in q) and cols["date"]:
        dates = pd.to_datetime(df[cols["date"]], errors="coerce")
        tmp = pd.DataFrame({"period": dates.dt.to_period("M").astype(str), "value": numeric_revenue})
        monthly = tmp.groupby("period")["value"].sum().sort_index()
        if len(monthly) >= 2:
            latest = float(monthly.iloc[-1])
            previous = float(monthly.iloc[-2])
            delta = latest - previous
            pct = delta / previous * 100 if previous else 0
            direction = "increased" if delta >= 0 else "decreased"
            return AnalystResult(
                "monthly_change",
                f"Revenue {direction} by {_money(abs(delta))} ({pct:.1f}%) from "
                f"{monthly.index[-2]} to {monthly.index[-1]}.",
                {"monthly": monthly.to_dict(), "latest": latest, "previous": previous, "change": delta, "change_percent": pct},
            )

    # Anomaly-style question
    if "anomal" in q or "unusual" in q or "outlier" in q:
        s = numeric_revenue.dropna()
        if len(s) >= 5 and float(s.std()) > 0:
            z = (s - s.mean()) / s.std()
            outliers = df.loc[z.abs() >= 3].copy()
            return AnalystResult(
                "anomalies",
                f"I found {len(outliers)} potential revenue outlier(s) using an absolute z-score threshold of 3.",
                {"count": int(len(outliers)), "threshold": 3},
            )
        return AnalystResult("anomalies", "There is not enough variation or data to detect reliable outliers.", {} , "Medium")

    # Overall summary fallback
    return AnalystResult(
        "overview",
        f"The dataset contains {len(df):,} rows and {len(df.columns):,} columns. "
        f"Total revenue/sales is {_money(total_revenue)} across {count:,} usable records.",
        {"rows": int(len(df)), "columns": int(len(df.columns)), "total_revenue": total_revenue, "usable_records": count},
    )
