import pandas as pd
def numeric_summary(df):
    cols=df.select_dtypes(include="number").columns
    if len(cols)==0:return pd.DataFrame()
    x=df[cols].describe().T.reset_index().rename(columns={"index":"Column"}); x["Missing"]=df[cols].isna().sum().values; x["Skewness"]=[df[c].skew() for c in cols]; return x.round(3)
def categorical_summary(df):
    rows=[]
    for c in df.select_dtypes(include=["object","category","bool"]).columns:
        vc=df[c].value_counts(dropna=True); mode=df[c].mode(dropna=True)
        rows.append({"Column":c,"Unique":int(df[c].nunique(dropna=True)),"Missing":int(df[c].isna().sum()),"Top Value":mode.iloc[0] if not mode.empty else "","Top Frequency":int(vc.iloc[0]) if not vc.empty else 0})
    return pd.DataFrame(rows)
def correlation_matrix(df): return df.select_dtypes(include="number").corr()
def detect_date_columns(df):
    out=[]
    for c in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[c]): out.append(c)
        elif df[c].dtype=="object" and pd.to_datetime(df[c],errors="coerce").notna().mean()>=.85: out.append(c)
    return out
def time_series_summary(df,date_col,numeric_cols):
    x=df.copy(); x[date_col]=pd.to_datetime(x[date_col],errors="coerce"); x=x.dropna(subset=[date_col]).set_index(date_col); cols=[c for c in numeric_cols if c in x.columns]
    return pd.DataFrame() if x.empty or not cols else x[cols].resample("ME").sum().reset_index().rename(columns={date_col:"Period"})
