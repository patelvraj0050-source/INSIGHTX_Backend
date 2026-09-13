import pandas as pd

def validate_dataset(df, mapping):
    checks = [
        ("Schema", len(df.columns) > 0, f"{len(df.columns)} columns detected"),
        ("Records", len(df) > 0, f"{len(df):,} rows"),
        ("Duplicate rows", not df.duplicated().any(), f"{int(df.duplicated().sum()):,} duplicates"),
    ]
    numeric = df.select_dtypes(include="number").columns
    checks.append(("Numeric validity", True, f"{len(numeric)} numeric columns"))
    date_col = mapping.get("date")
    if date_col:
        valid_dates = pd.to_datetime(df[date_col], errors="coerce").notna().sum()
        checks.append(("Date validity", valid_dates > 0, f"{valid_dates:,} parseable dates"))
    else:
        checks.append(("Date field", False, "No recognizable date field"))
    return checks

def quality_score(checks, df):
    if not checks:
        return 0
    passed = sum(bool(x[1]) for x in checks)
    base = passed / len(checks) * 100
    missing_rate = float(df.isna().mean().mean()) if len(df) else 1
    return max(0, round(base - missing_rate * 10))
