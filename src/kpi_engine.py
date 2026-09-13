import pandas as pd

def _find(df, keys, num=False):
    for c in df.columns:
        n = str(c).strip().lower().replace('_', ' ')
        if any(k in n for k in keys) and (not num or pd.api.types.is_numeric_dtype(df[c])):
            return c

def detect_business_columns(df):
    nums = df.select_dtypes(include='number').columns.tolist()
    dim = None
    preferred_dims = ['region','state','category','product','segment','customer segment','city','country']
    for key in preferred_dims:
        hit = next((c for c in df.columns if key in str(c).strip().lower()), None)
        if hit and hit not in nums and 2 <= df[hit].nunique(dropna=True) <= 100:
            dim = hit; break
    if dim is None:
        for c in df.columns:
            if c not in nums and 2 <= df[c].nunique(dropna=True) <= min(100, max(2, int(len(df)*.2))):
                dim = c; break
    return {
        'revenue': _find(df,['revenue','sales','amount','turnover'],1),
        'profit': _find(df,['profit','net income','earnings'],1),
        'cost': _find(df,['cost','expense','cogs'],1),
        'quantity': _find(df,['quantity','qty','units','volume'],1),
        'discount': _find(df,['discount'],1),
        'order_id': _find(df,['order id','order_id','transaction id','transaction_id','invoice']),
        'customer_id': _find(df,['customer id','customer_id','client id','client_id']),
        'date': _find(df,['order date','transaction date','date','time','month','year']),
        'dimension': dim,
        'numeric': nums[0] if nums else None,
    }

def _fmt(x):
    if pd.isna(x): return '—'
    if abs(x) >= 1e9: return f'{x/1e9:.2f}B'
    if abs(x) >= 1e6: return f'{x/1e6:.2f}M'
    if abs(x) >= 1e3: return f'{x/1e3:.2f}K'
    return f'{x:,.2f}'

def calculate_kpis(df,m):
    r={}; rev,pro,qty,oid,cid=m.get('revenue'),m.get('profit'),m.get('quantity'),m.get('order_id'),m.get('customer_id')
    if rev: r['Revenue']=_fmt(df[rev].sum())
    if pro: r['Profit']=_fmt(df[pro].sum())
    if rev and pro and df[rev].sum()!=0: r['Profit Margin']=f'{df[pro].sum()/df[rev].sum()*100:.2f}%'
    r['Orders' if oid else 'Records']=f'{df[oid].nunique():,}' if oid else f'{len(df):,}'
    if cid: r['Customers']=f'{df[cid].nunique():,}'
    if qty: r['Units']=f'{df[qty].sum():,.0f}'
    if rev and oid and df[oid].nunique(): r['Avg Order Value']=_fmt(df[rev].sum()/df[oid].nunique())
    return r

def monthly_metrics(df,m):
    dc,rev,pro,qty=m.get('date'),m.get('revenue'),m.get('profit'),m.get('quantity')
    if not dc: return pd.DataFrame()
    d=pd.to_datetime(df[dc],errors='coerce'); x=df.loc[d.notna()].copy(); x['_date']=d[d.notna()]; x['_period']=x['_date'].dt.to_period('M')
    agg={}
    if rev: agg[rev]='sum'
    if pro: agg[pro]='sum'
    if qty: agg[qty]='sum'
    if not agg: return pd.DataFrame()
    t=x.groupby('_period').agg(agg).sort_index().rename_axis('Period').reset_index(); t['Period']=t['Period'].astype(str)
    if rev and pro: t['Margin %']=t[pro].div(t[rev].replace(0,pd.NA))*100
    if rev: t['Revenue Growth %']=t[rev].pct_change()*100
    return t

def segment_analysis(df, dimension, metric, top_n=15):
    if not dimension or not metric or dimension not in df.columns or metric not in df.columns: return pd.DataFrame()
    x=df.groupby(dimension,dropna=False)[metric].sum().sort_values(ascending=False).head(top_n).reset_index()
    total=df[metric].sum()
    x['Contribution %']=x[metric].div(total)*100 if total else 0
    x['Rank']=range(1,len(x)+1)
    return x

def period_comparison(df,m):
    t=monthly_metrics(df,m)
    if len(t)<2 or not m.get('revenue'): return {}
    prev,cur=t[m['revenue']].iloc[-2],t[m['revenue']].iloc[-1]
    return {'Revenue MoM':'N/A' if prev==0 else f'{(cur-prev)/abs(prev)*100:+.2f}%', 'Latest Month':str(t['Period'].iloc[-1])}
