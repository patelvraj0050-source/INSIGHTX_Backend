import pandas as pd

def _fmt(x):
    if pd.isna(x): return '—'
    if abs(x)>=1e9:return f'{x/1e9:.2f}B'
    if abs(x)>=1e6:return f'{x/1e6:.2f}M'
    if abs(x)>=1e3:return f'{x/1e3:.2f}K'
    return f'{x:,.2f}'

def generate_insights(df,m):
    out=[]; rev,pro,qty,dim=m.get('revenue'),m.get('profit'),m.get('quantity'),m.get('dimension')
    if rev: out.append({'title':'💰 Revenue Performance','text':f'Total {rev} is {_fmt(df[rev].sum())} across {len(df):,} records.'})
    if pro and rev and df[rev].sum()!=0:
        margin=df[pro].sum()/df[rev].sum()*100
        out.append({'title':'📈 Profitability','text':f'Overall profit margin is {margin:.2f}%. ' + ('Profitability looks healthy at an aggregate level.' if margin>10 else 'The margin is relatively thin; review pricing, discounting and cost drivers.')})
    if dim and rev:
        g=df.groupby(dim,dropna=False)[rev].sum().sort_values(ascending=False)
        if len(g) and g.sum()!=0:
            out.append({'title':'🏆 Top Segment','text':f'{g.index[0]} contributes {g.iloc[0]/g.sum()*100:.1f}% of total {rev}.'})
            if len(g)>1: out.append({'title':'⚠️ Concentration Risk','text':f'The top 2 {dim} groups contribute {(g.iloc[:2].sum()/g.sum()*100):.1f}% of total {rev}. Consider whether revenue is overly concentrated.'})
    if dim and pro and rev:
        g=df.groupby(dim,dropna=False)[[rev,pro]].sum(); g['margin']=g[pro].div(g[rev].replace(0,pd.NA))*100; g=g.dropna()
        if len(g):
            lo,hi=g['margin'].idxmin(),g['margin'].idxmax()
            out.append({'title':'🔎 Margin Range','text':f'Segment margins range from {g.loc[lo,"margin"]:.2f}% ({lo}) to {g.loc[hi,"margin"]:.2f}% ({hi}).'})
            weak=g[g['margin']<g['margin'].median()]
            if len(weak): out.append({'title':'🎯 Margin Opportunity','text':f'{len(weak)} segment(s) sit below the median segment margin. Investigate their discount, cost and product mix.'})
    if qty: out.append({'title':'📦 Volume','text':f'Total recorded units/quantity: {df[qty].sum():,.0f}.'})
    return out
