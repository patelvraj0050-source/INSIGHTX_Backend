"""INSIGHTX v0.3 advanced analytics utilities."""
import numpy as np
import pandas as pd


def numeric_anomalies(df, column, z_threshold=3.0):
    s = pd.to_numeric(df[column], errors="coerce")
    mean, std = s.mean(), s.std()
    out = df.copy()
    if pd.isna(std) or std == 0:
        out["anomaly_score"] = 0.0
        out["is_anomaly"] = False
        return out
    out["anomaly_score"] = ((s - mean) / std).abs()
    out["is_anomaly"] = out["anomaly_score"] >= z_threshold
    return out.sort_values("anomaly_score", ascending=False)


def monthly_forecast(df, date_col, value_col, periods=3):
    data = pd.DataFrame({"date": pd.to_datetime(df[date_col], errors="coerce"), "value": pd.to_numeric(df[value_col], errors="coerce")}).dropna()
    if data.empty:
        return pd.DataFrame()
    monthly = data.set_index("date")["value"].resample("MS").sum().reset_index()
    if len(monthly) < 2:
        return monthly.assign(type="actual")
    x = np.arange(len(monthly), dtype=float)
    coef = np.polyfit(x, monthly["value"].to_numpy(), 1)
    future_x = np.arange(len(monthly), len(monthly) + periods, dtype=float)
    future_dates = pd.date_range(monthly["date"].max() + pd.offsets.MonthBegin(1), periods=periods, freq="MS")
    forecast = pd.DataFrame({"date": future_dates, "value": np.polyval(coef, future_x), "type": "forecast"})
    actual = monthly.assign(type="actual")
    return pd.concat([actual, forecast], ignore_index=True)


def regression_summary(df, x_col, y_col):
    data = df[[x_col, y_col]].apply(pd.to_numeric, errors="coerce").dropna()
    if len(data) < 3 or data[x_col].nunique() < 2:
        return None
    slope, intercept = np.polyfit(data[x_col], data[y_col], 1)
    pred = slope * data[x_col] + intercept
    ss_res = ((data[y_col] - pred) ** 2).sum()
    ss_tot = ((data[y_col] - data[y_col].mean()) ** 2).sum()
    r2 = 1 - ss_res / ss_tot if ss_tot else 0.0
    return {"rows": len(data), "slope": float(slope), "intercept": float(intercept), "r2": float(r2)}


def segment_summary(df, dimension, metric):
    x = df[[dimension, metric]].copy()
    x[metric] = pd.to_numeric(x[metric], errors="coerce")
    x[dimension] = x[dimension].fillna("Unknown").astype(str)
    return x.groupby(dimension, as_index=False)[metric].agg(["count", "sum", "mean", "median"]).reset_index().sort_values("sum", ascending=False)
