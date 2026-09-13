import pandas as pd
def semantic_type(s):
    if pd.api.types.is_datetime64_any_dtype(s): return "Datetime"
    if pd.api.types.is_numeric_dtype(s): return "Numeric"
    if pd.api.types.is_bool_dtype(s): return "Boolean"
    return "Categorical/Text"
def profile_dataframe(df):
    r=[]
    for c in df.columns:
        s=df[c]; r.append({"Column":c,"Data Type":str(s.dtype),"Semantic Type":semantic_type(s),"Missing":int(s.isna().sum()),"Missing %":round(s.isna().mean()*100,2),"Unique":int(s.nunique(dropna=True)),"Cardinality %":round(s.nunique(dropna=True)/max(len(df),1)*100,2),"Example":"" if s.dropna().empty else str(s.dropna().iloc[0])[:80]})
    return pd.DataFrame(r)
def dataset_summary(df): return {"rows":len(df),"columns":df.shape[1],"missing_cells":int(df.isna().sum().sum()),"duplicate_rows":int(df.duplicated().sum())}
