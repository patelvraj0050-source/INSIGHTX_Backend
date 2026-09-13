import pandas as pd
def load_dataframe(f):
    n=f.name.lower()
    if n.endswith(".csv"):
        try: df=pd.read_csv(f)
        except UnicodeDecodeError: f.seek(0); df=pd.read_csv(f,encoding="latin1")
    elif n.endswith((".xlsx",".xls")): df=pd.read_excel(f)
    else: raise ValueError("Unsupported file type.")
    df.columns=[str(c).strip() for c in df.columns]
    return df
