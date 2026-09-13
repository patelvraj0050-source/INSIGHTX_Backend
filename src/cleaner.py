import pandas as pd
def _outlier_count(s):
    if not pd.api.types.is_numeric_dtype(s): return 0
    x=s.dropna()
    if len(x)<8 or x.nunique()<4: return 0
    q1,q3=x.quantile([.25,.75]); iqr=q3-q1
    return 0 if iqr==0 else int(((x<q1-1.5*iqr)|(x>q3+1.5*iqr)).sum())
def quality_report(df):
    r=[]; out=0
    for c in df.columns:
        s=df[c]; o=_outlier_count(s); out+=o; miss=int(s.isna().sum())
        r.append({"Column":c,"Missing":miss,"Missing %":round(s.isna().mean()*100,2),"Duplicates":int(s.duplicated().sum()),"Outliers (IQR)":o,"Unique":int(s.nunique(dropna=True)),"Status":"⚠ Review" if miss or o else "✓ Good"})
    z=pd.DataFrame(r)
    return {"missing_cells":int(df.isna().sum().sum()),"duplicate_rows":int(df.duplicated().sum()),"outlier_cells":out,"columns_with_issues":int((z.Status!="✓ Good").sum()),"column_report":z}
def clean_dataframe(df):
    out=df.copy(); actions=[]; before=len(out); out=out.drop_duplicates()
    if before-len(out): actions.append(f"Removed {before-len(out):,} exact duplicate rows.")
    for c in out.select_dtypes(include="number").columns:
        if out[c].isna().any():
            n=int(out[c].isna().sum()); out[c]=out[c].fillna(out[c].median()); actions.append(f"Filled {n:,} missing numeric values in '{c}' with the median.")
    return out,actions
