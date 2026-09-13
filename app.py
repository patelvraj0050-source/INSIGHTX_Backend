import time
import streamlit as st
from src.ai_business_analyst import answer_question
import pandas as pd
from src.data_loader import load_dataframe
from src.profiler import profile_dataframe, dataset_summary
from src.cleaner import quality_report, clean_dataframe
from src.eda import numeric_summary, categorical_summary, correlation_matrix, detect_date_columns, time_series_summary
from src.kpi_engine import detect_business_columns, calculate_kpis, period_comparison, monthly_metrics, segment_analysis
from src.visualization import plot_time_series, plot_bar, plot_histogram, plot_correlation, plot_box, plot_scatter
from src.insights import generate_insights
from pipeline.etl import run_etl
from database.connection import get_engine, test_connection
from database.warehouse import load_star_schema
from database.queries import QUERIES, run_query
from src.advanced_analytics import numeric_anomalies, monthly_forecast, regression_summary, segment_summary
from src.bi_layer import kpi_hierarchy, contribution_table, executive_summary, recommendations

# Public deployment API URL can be configured with INSIGHTX_API_URL.

st.markdown('\n<style>\n:root {\n  --ix-black: #08090b;\n  --ix-panel: #111318;\n  --ix-card: #17191f;\n  --ix-gold: #f5b942;\n  --ix-yellow: #ffd166;\n  --ix-muted-gold: #b8892d;\n  --ix-text: #f5f5f5;\n  --ix-muted: #9b9da5;\n  --ix-border: rgba(245,185,66,.24);\n}\n\n/* Royal Amber atmosphere */\n.stApp {\n  background:\n    radial-gradient(circle at 88% 8%, rgba(245,185,66,.08), transparent 28rem),\n    radial-gradient(circle at 8% 92%, rgba(184,137,45,.06), transparent 24rem),\n    var(--ix-black);\n  color: var(--ix-text);\n}\n\n/* Premium glass panels */\ndiv[data-testid="stMetric"],\ndiv[data-testid="stExpander"],\ndiv[data-testid="stFileUploader"],\ndiv[data-testid="stDataFrame"],\ndiv[data-testid="stAlert"] {\n  border: 1px solid var(--ix-border);\n  border-radius: 16px;\n  background: linear-gradient(145deg, rgba(23,25,31,.96), rgba(12,13,17,.96));\n  box-shadow: 0 0 0 1px rgba(245,185,66,.025), 0 12px 35px rgba(0,0,0,.18);\n}\n\n/* Gold metric accents */\ndiv[data-testid="stMetric"] {\n  position: relative;\n  overflow: hidden;\n  transition: transform .25s ease, border-color .25s ease, box-shadow .25s ease;\n}\ndiv[data-testid="stMetric"]::before {\n  content: "";\n  position: absolute;\n  inset: 0 auto 0 0;\n  width: 3px;\n  background: linear-gradient(#ffd166, #b8892d);\n}\ndiv[data-testid="stMetric"]:hover {\n  transform: translateY(-3px);\n  border-color: rgba(255,209,102,.65);\n  box-shadow: 0 12px 34px rgba(245,185,66,.10);\n}\n\n/* Animated section entrances */\nsection.main > div {\n  animation: ix-page-enter .65s ease both;\n}\n@keyframes ix-page-enter {\n  from { opacity: 0; transform: translateY(10px); }\n  to { opacity: 1; transform: translateY(0); }\n}\n\n/* Buttons */\n.stButton > button {\n  border: 1px solid rgba(245,185,66,.48) !important;\n  border-radius: 12px !important;\n  background: linear-gradient(135deg, #f5b942, #b8892d) !important;\n  color: #08090b !important;\n  font-weight: 750 !important;\n  transition: transform .2s ease, box-shadow .2s ease, filter .2s ease !important;\n  box-shadow: 0 5px 18px rgba(245,185,66,.12) !important;\n}\n.stButton > button:hover {\n  transform: translateY(-2px) scale(1.01);\n  filter: brightness(1.08);\n  box-shadow: 0 8px 26px rgba(245,185,66,.25) !important;\n}\n.stButton > button:active {\n  transform: translateY(0) scale(.98);\n}\n\n/* Sidebar and navigation */\nsection[data-testid="stSidebar"] {\n  background: linear-gradient(180deg, #101116 0%, #08090b 100%);\n  border-right: 1px solid var(--ix-border);\n}\nsection[data-testid="stSidebar"] * {\n  transition: color .2s ease, background .2s ease;\n}\n\n/* Dataset drop zone */\ndiv[data-testid="stFileUploader"] {\n  padding: 14px;\n  position: relative;\n  overflow: hidden;\n}\ndiv[data-testid="stFileUploader"]::before {\n  content: "DROP DATASET HERE";\n  display: block;\n  text-align: center;\n  letter-spacing: .18em;\n  font-size: .68rem;\n  font-weight: 800;\n  color: var(--ix-yellow);\n  opacity: .9;\n  padding: 10px 0 4px;\n  animation: ix-drop-pulse 2.2s ease-in-out infinite;\n}\ndiv[data-testid="stFileUploader"] section {\n  border: 1px dashed rgba(245,185,66,.55) !important;\n  border-radius: 14px !important;\n  background: linear-gradient(135deg, rgba(245,185,66,.07), rgba(255,209,102,.015)) !important;\n  transition: border-color .2s ease, background .2s ease, transform .2s ease;\n}\ndiv[data-testid="stFileUploader"] section:hover {\n  border-color: var(--ix-yellow) !important;\n  background: rgba(245,185,66,.12) !important;\n  transform: translateY(-2px);\n}\n@keyframes ix-drop-pulse {\n  0%,100% { opacity: .55; letter-spacing: .16em; }\n  50% { opacity: 1; letter-spacing: .22em; }\n}\n\n/* File uploader icon/button */\ndiv[data-testid="stFileUploader"] button {\n  border-color: rgba(245,185,66,.5) !important;\n  color: var(--ix-yellow) !important;\n}\n\n/* Inputs */\n.stTextInput input, .stSelectbox div[data-baseweb="select"] > div,\n.stTextArea textarea {\n  background: #111318 !important;\n  border-color: rgba(245,185,66,.2) !important;\n  border-radius: 11px !important;\n}\n.stTextInput input:focus, .stTextArea textarea:focus {\n  border-color: var(--ix-gold) !important;\n  box-shadow: 0 0 0 1px var(--ix-gold), 0 0 22px rgba(245,185,66,.10) !important;\n}\n\n/* Animated gold progress */\n.stProgress > div > div > div > div {\n  background: linear-gradient(90deg, #b8892d, #ffd166, #f5b942) !important;\n  background-size: 200% 100%;\n  animation: ix-progress-shimmer 1.6s linear infinite;\n}\n@keyframes ix-progress-shimmer {\n  from { background-position: 200% 0; }\n  to { background-position: -200% 0; }\n}\n\n/* Cursor: gold pointer asset, with a subtle glow */\n* {\n  cursor: url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'32\' height=\'32\' viewBox=\'0 0 32 32\'%3E%3Cpath d=\'M5 3l8 23 5-8 9-3z\' fill=\'%23ffd166\' stroke=\'%2308090b\' stroke-width=\'2\'/%3E%3Ccircle cx=\'23\' cy=\'23\' r=\'4\' fill=\'%23f5b942\' opacity=\'.8\'/%3E%3C/svg%3E") 3 3, auto;\n}\nbutton, a, input, textarea, select, [role="button"] {\n  cursor: url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'32\' height=\'32\' viewBox=\'0 0 32 32\'%3E%3Cpath d=\'M5 3l8 23 5-8 9-3z\' fill=\'%23f5b942\' stroke=\'%2308090b\' stroke-width=\'2\'/%3E%3Ccircle cx=\'23\' cy=\'23\' r=\'5\' fill=\'%23ffd166\' opacity=\'.9\'/%3E%3C/svg%3E") 3 3, pointer;\n}\n\n/* Reduced-motion accessibility */\n@media (prefers-reduced-motion: reduce) {\n  *, *::before, *::after {\n    animation-duration: .01ms !important;\n    animation-iteration-count: 1 !important;\n    transition-duration: .01ms !important;\n    scroll-behavior: auto !important;\n  }\n}\n</style>\n', unsafe_allow_html=True)

st.set_page_config(page_title='INSIGHTX — Business Intelligence', page_icon='✦', layout='wide', initial_sidebar_state='collapsed')

# ----------------------------- Premium product UI -----------------------------
CSS = r'''
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Inter:wght@400;500;600;700;800&display=swap');
:root { --ink:#eef2ff; --muted:#8e9ab7; --line:rgba(255,255,255,.09); --panel:rgba(18,24,43,.72); --accent:#7c5cff; --accent2:#20d6c7; }
html, body, [class*="css"] { font-family: Inter, sans-serif; }
.stApp { background: radial-gradient(circle at 50% -10%, rgba(124,92,255,.20), transparent 35%), radial-gradient(circle at 85% 30%, rgba(32,214,199,.08), transparent 25%), #070a12; color:var(--ink); }
section[data-testid="stSidebar"] { background:rgba(7,10,18,.96); border-right:1px solid var(--line); }
.block-container { padding-top:2rem; padding-bottom:3rem; max-width:1450px; }
.hero { min-height:72vh; display:flex; align-items:center; justify-content:center; position:relative; overflow:hidden; }
.hero:before,.hero:after { content:""; position:absolute; border:1px solid rgba(124,92,255,.16); border-radius:50%; animation:pulse 5s ease-in-out infinite; }
.hero:before { width:520px;height:520px; }.hero:after { width:760px;height:760px; animation-delay:1.3s; }
@keyframes pulse { 0%,100%{transform:scale(.94);opacity:.3} 50%{transform:scale(1.04);opacity:.75} }
.hero-inner { text-align:center; position:relative; z-index:2; max-width:850px; }
.brand { font-size:clamp(3.6rem,9vw,7.2rem); line-height:.9; letter-spacing:-.08em; font-weight:800; margin:0; background:linear-gradient(110deg,#fff 15%,#bdb0ff 48%,#6ff6e7 90%); -webkit-background-clip:text; color:transparent; }
.kicker { font-family:'DM Mono',monospace; color:#8996b4; letter-spacing:.18em; text-transform:uppercase; font-size:.72rem; margin:1.4rem 0; }
.tagline { font-size:1.25rem; color:#c8d0e3; margin:0 auto 2rem; max-width:650px; }
.quote { color:#77839f; font-size:.88rem; font-style:italic; margin:1.2rem 0 2.3rem; }
.core { width:112px;height:112px;margin:0 auto 2rem;border-radius:50%; background:radial-gradient(circle at 35% 30%,#fff, #9e8cff 12%,#7c5cff 35%,#16122e 68%); box-shadow:0 0 45px rgba(124,92,255,.55), inset 0 0 30px rgba(255,255,255,.25); animation:float 3.5s ease-in-out infinite; position:relative; }
.core:after { content:""; position:absolute; inset:-20px; border:1px dashed rgba(111,246,231,.45); border-radius:50%; animation:spin 12s linear infinite; }
@keyframes float {50%{transform:translateY(-10px) scale(1.03)}} @keyframes spin {to{transform:rotate(360deg)}}
.upload-card { max-width:700px; margin:0 auto; padding:2rem; border:1px solid rgba(124,92,255,.3); background:linear-gradient(145deg,rgba(20,26,48,.78),rgba(10,14,26,.72)); border-radius:24px; box-shadow:0 25px 80px rgba(0,0,0,.35); }
div[data-testid="stFileUploader"] { border:1px dashed rgba(124,92,255,.5); border-radius:18px; padding:.6rem; background:rgba(124,92,255,.05); }
.process-wrap { min-height:68vh; display:flex; align-items:center; justify-content:center; }
.process-card { width:min(760px,92vw); text-align:center; padding:3rem; border:1px solid var(--line); background:rgba(12,17,31,.88); border-radius:28px; box-shadow:0 30px 100px rgba(0,0,0,.5); }
.process-title { font-size:2rem; font-weight:700; margin:.5rem 0; }.process-sub { color:var(--muted); }
.scan { height:3px; width:100%; overflow:hidden; background:#171d30; border-radius:10px; margin:2rem 0; }.scan span { display:block;height:100%;width:35%;background:linear-gradient(90deg,transparent,#7c5cff,#20d6c7,transparent);animation:scan 1.2s linear infinite; }
@keyframes scan {from{transform:translateX(-120%)}to{transform:translateX(330%)}}
.step-grid { display:grid;grid-template-columns:repeat(4,1fr);gap:.65rem; margin-top:1.5rem; }.step {padding:.75rem;border:1px solid var(--line);border-radius:12px;color:#66728e;font-size:.72rem}.step.on{color:#e9edff;border-color:rgba(124,92,255,.5);background:rgba(124,92,255,.08)}
.topbar {display:flex;justify-content:space-between;align-items:end;padding:.6rem 0 1.4rem;border-bottom:1px solid var(--line);margin-bottom:1.4rem}.topbrand{font-size:1.8rem;font-weight:800;letter-spacing:-.05em}.identity{font-size:.7rem;color:#7f8ba6;letter-spacing:.12em;text-transform:uppercase;text-align:right}.identity b{color:#dfe5f5}.section-label{font-family:'DM Mono',monospace;font-size:.68rem;color:#75819c;letter-spacing:.16em;text-transform:uppercase;margin-bottom:.4rem}
div[data-testid="stMetric"] { background:linear-gradient(145deg,rgba(19,25,44,.85),rgba(11,15,27,.7)); border:1px solid var(--line); padding:1rem 1.1rem; border-radius:16px; }
.stTabs [data-baseweb="tab-list"] { gap:.35rem; background:rgba(9,13,24,.75); padding:.4rem; border-radius:14px; border:1px solid var(--line); }.stTabs [data-baseweb="tab"] { border-radius:10px; color:#8792ab; }.stTabs [aria-selected="true"] { background:rgba(124,92,255,.16); color:white; }
[data-testid="stDataFrame"] { border:1px solid var(--line); border-radius:14px; overflow:hidden; }
footer { visibility:hidden; }
@media(max-width:800px){.step-grid{grid-template-columns:repeat(2,1fr)}.hero{min-height:80vh}.brand{font-size:4.5rem}.topbar{align-items:flex-start}.identity{font-size:.58rem}}
</style>
'''
st.markdown(CSS, unsafe_allow_html=True)


def landing():
    st.markdown('''
    <div class="hero"><div class="hero-inner">
      <div class="kicker">Business Intelligence & Analytics Platform</div>
      <div class="core"></div>
      <h1 class="brand">INSIGHTX</h1>
      <p class="tagline">Turn a raw dataset into a clear business story — automatically.</p>
      <div class="quote">“Turning data into insight, and insight into better decisions.”</div>
      <div class="upload-card">
        <div class="section-label">Start with your data</div>
        <p style="color:#d8def0;font-size:1.05rem;margin-bottom:.3rem"><b>Drop your dataset into INSIGHTX</b></p>
        <p style="color:#77839f;font-size:.82rem">CSV or Excel · Your analysis stays inside this session</p>
    ''', unsafe_allow_html=True)
    uploaded = st.file_uploader('Upload Dataset', type=['csv','xlsx','xls'], label_visibility='collapsed')
    st.markdown('''<div style="margin-top:1rem;color:#59647d;font-size:.68rem;letter-spacing:.12em;text-transform:uppercase">Built by <b style="color:#aeb8d0">VRAJ PATEL</b></div></div></div></div>''', unsafe_allow_html=True)
    return uploaded


def processing(uploaded):
    st.markdown('''<div class="process-wrap"><div class="process-card"><div class="kicker">INSIGHTX Intelligence Engine</div><div class="core"></div><div class="process-title">Reading your data</div><div class="process-sub">Turning rows and columns into business intelligence.</div><div class="scan"><span></span></div><div class="step-grid"><div class="step on">01 · Structure</div><div class="step on">02 · Quality</div><div class="step on">03 · Metrics</div><div class="step on">04 · Insights</div></div></div></div>''', unsafe_allow_html=True)
    bar = st.progress(0, text='Initializing intelligence engine…')
    steps = [(12,'Mapping dataset structure…'),(32,'Checking data quality…'),(55,'Detecting business metrics…'),(76,'Building performance signals…'),(92,'Generating insight layer…'),(100,'Intelligence ready.')]
    for value, text in steps:
        time.sleep(.28 if value < 100 else .18)
        bar.progress(value, text=text)
    time.sleep(.35)
    bar.empty()


# Landing first; dashboard is deliberately hidden until data is supplied.
if 'processed_upload_key' not in st.session_state:
    st.session_state.processed_upload_key = None

with st.sidebar:
    st.markdown('### INSIGHTX')
    st.caption('Business Intelligence & Analytics Platform')
    st.caption('Built by VRAJ PATEL')

uploaded = landing()
if uploaded is None:
    st.stop()

upload_key = f'{uploaded.name}:{uploaded.size}'
if st.session_state.processed_upload_key != upload_key:
    processing(uploaded)
    st.session_state.processed_upload_key = upload_key
    st.rerun()

try:
    df = load_dataframe(uploaded)
except Exception as e:
    st.error(f'Could not read the dataset: {e}')
    st.stop()
if df.empty:
    st.warning('The dataset contains no rows.')
    st.stop()

m = detect_business_columns(df)
k = calculate_kpis(df, m)

st.markdown('''<div class="topbar"><div><div class="section-label">Intelligence workspace</div><div class="topbrand">INSIGHTX</div></div><div class="identity">Business Intelligence & Analytics<br><b>BUILT BY VRAJ PATEL</b></div></div>''', unsafe_allow_html=True)

# Keep the full v0.1.2 analytical engine intact behind the new product shell.
tabs = st.tabs(['✦ Executive Overview','◌ Data Quality','⌁ EDA','▦ KPI Intelligence','◈ Segment Analysis','↗ Trend Intelligence','✧ Insights','⚙ Data Engineering','▣ BI Command Center','◎ Advanced Analytics','🤖 AI Business Analyst','⊞ Data'])
with tabs[0]:
    s=dataset_summary(df); st.markdown('<div class="section-label">Executive command center</div>',unsafe_allow_html=True); 

    st.subheader('Your data, translated into business signals')
    a,b,c,d=st.columns(4); a.metric('Rows',f"{s['rows']:,}"); b.metric('Columns',s['columns']); c.metric('Missing Cells',f"{s['missing_cells']:,}"); d.metric('Duplicate Rows',f"{s['duplicate_rows']:,}")
    if k:
        st.write('### Business Snapshot'); cards=st.columns(min(6,len(k)))
        for i,(n,v) in enumerate(k.items()): cards[i%len(cards)].metric(n,v)
    st.write('### Detected Business Fields'); st.json(m)
    st.dataframe(profile_dataframe(df),use_container_width=True,hide_index=True)
with tabs[1]:
    q=quality_report(df); st.subheader('Data Quality'); a,b,c,d=st.columns(4); a.metric('Missing Cells',f"{q['missing_cells']:,}"); b.metric('Duplicate Rows',f"{q['duplicate_rows']:,}"); c.metric('Numeric Outliers',f"{q['outlier_cells']:,}"); d.metric('Columns With Issues',q['columns_with_issues'])
    st.dataframe(q['column_report'],use_container_width=True,hide_index=True); st.write('### Conservative Cleaning Preview'); cleaned,actions=clean_dataframe(df)
    for x in actions: st.caption('• '+x)
    st.dataframe(cleaned.head(100),use_container_width=True,hide_index=True)
with tabs[2]:
    st.subheader('Exploratory Data Analysis'); num=numeric_summary(df); cat=categorical_summary(df); dates=detect_date_columns(df)
    if not num.empty:
        st.dataframe(num,use_container_width=True,hide_index=True); col=st.selectbox('Distribution',num['Column'].tolist()); a,b=st.columns(2); a.plotly_chart(plot_histogram(df,col),use_container_width=True); b.plotly_chart(plot_box(df,col),use_container_width=True)
        if len(num)>=2:
            cols=num['Column'].tolist(); x=st.selectbox('X variable',cols,key='x'); ys=[z for z in cols if z!=x] or cols; y=st.selectbox('Y variable',ys,key='y'); st.plotly_chart(plot_scatter(df,x,y),use_container_width=True)
    if not cat.empty: st.write('### Categorical Analysis'); st.dataframe(cat,use_container_width=True,hide_index=True)
    if len(num)>=2: st.plotly_chart(plot_correlation(correlation_matrix(df)),use_container_width=True)
    if dates:
        dc=st.selectbox('Date column',dates); td=time_series_summary(df,dc,num['Column'].tolist() if not num.empty else [])
        if not td.empty:
            metric=st.selectbox('Time-series metric',[x for x in td.columns if x!='Period']); st.plotly_chart(plot_time_series(td,metric),use_container_width=True)
with tabs[3]:
    st.subheader('Business KPI Intelligence'); cards=st.columns(min(6,len(k)))
    for i,(n,v) in enumerate(k.items()): cards[i%len(cards)].metric(n,v)
    st.write('### Period Performance'); comp=period_comparison(df,m)
    if comp:
        cards=st.columns(len(comp))
        for i,(n,v) in enumerate(comp.items()): cards[i].metric(n,v)
    st.write('### Detected Business Fields'); st.json(m)
with tabs[4]:
    st.subheader('Segment Contribution & Ranking'); dim_options=[c for c in df.columns if df[c].nunique(dropna=True) <= min(100,max(2,int(len(df)*.2))) and not pd.api.types.is_numeric_dtype(df[c])]
    dim=st.selectbox('Business dimension',dim_options,index=dim_options.index(m['dimension']) if m.get('dimension') in dim_options else 0) if dim_options else None
    metric_options=[c for c in [m.get('revenue'),m.get('profit'),m.get('cost'),m.get('quantity')] if c]; metric=st.selectbox('Measure',metric_options) if metric_options else None
    if dim and metric:
        g=segment_analysis(df,dim,metric); st.dataframe(g,use_container_width=True,hide_index=True); st.plotly_chart(plot_bar(g,dim,metric,f'{metric} by {dim}'),use_container_width=True)
with tabs[5]:
    st.subheader('Trend Intelligence'); t=monthly_metrics(df,m)
    if t.empty: st.info('A recognizable date and numeric business metric are required.')
    else:
        st.dataframe(t,use_container_width=True,hide_index=True)
        if m.get('revenue'):
            st.plotly_chart(plot_time_series(t,'Revenue Growth %'),use_container_width=True); growth=t['Revenue Growth %'].dropna()
            if len(growth):
                best=t.loc[t[m['revenue']].idxmax(),'Period']; worst=t.loc[t[m['revenue']].idxmin(),'Period']; avg=growth.mean(); a,b,c=st.columns(3); a.metric('Best Revenue Month',str(best)); b.metric('Lowest Revenue Month',str(worst)); c.metric('Avg Monthly Growth',f'{avg:+.2f}%')
with tabs[6]:
    st.subheader('Automated Business Insights'); ins=generate_insights(df,m)
    if not ins: st.info('Not enough recognizable business fields for reliable insights.')
    for x in ins: st.markdown(f"#### {x['title']}"); st.write(x['text'])
with tabs[7]:
    st.subheader('Data Engineering')
    st.caption('ETL • validation • PostgreSQL • star schema • SQL analytics')
    etl_result, cleaned_df = run_etl(df, m)
    a,b,c,d = st.columns(4)
    a.metric('ETL Status', etl_result.status)
    b.metric('Raw Rows', f"{etl_result.raw_rows:,}")
    c.metric('Clean Rows', f"{etl_result.clean_rows:,}")
    d.metric('Quality Score', f"{etl_result.quality_score}/100")

    st.write('### Pipeline')
    pipeline_steps = [
        ('01', 'Extract', f"{etl_result.raw_rows:,} rows received"),
        ('02', 'Transform', f"{etl_result.removed_rows:,} rows removed/normalized"),
        ('03', 'Validate', f"{sum(bool(x[1]) for x in etl_result.checks)}/{len(etl_result.checks)} checks passed"),
        ('04', 'Load', 'Ready for PostgreSQL warehouse'),
    ]
    cols = st.columns(4)
    for i,(num,title,detail) in enumerate(pipeline_steps):
        cols[i].markdown(f"**{num} · {title}**")
        cols[i].caption(detail)

    st.write('### Validation Checks')
    st.dataframe(pd.DataFrame(etl_result.checks, columns=['Check','Passed','Detail']),
                 use_container_width=True, hide_index=True)

    st.write('### PostgreSQL')
    ok, msg = test_connection()
    if ok:
        st.success(msg)
        if st.button('Load Clean Dataset into Warehouse', type='primary'):
            try:
                loaded = load_star_schema(cleaned_df, m, get_engine())
                st.success(f"Warehouse load complete: {loaded:,} fact rows loaded.")
            except Exception as e:
                st.error(f"Warehouse load failed: {e}")
        if st.button('Run SQL Analytics'):
            try:
                engine = get_engine()
                for name in QUERIES:
                    st.markdown(f'#### {name}')
                    st.dataframe(run_query(engine, name), use_container_width=True, hide_index=True)
            except Exception as e:
                st.error(f"SQL analytics failed: {e}")
    else:
        st.info('PostgreSQL is optional in demo mode. Set INSIGHTX_DATABASE_URL to enable the warehouse and SQL layer.')
        st.code('INSIGHTX_DATABASE_URL=postgresql+psycopg2://insightx:insightx@localhost:5432/insightx')

    st.write('### Clean Data Preview')
    st.dataframe(cleaned_df.head(100), use_container_width=True, hide_index=True)

with tabs[8]:
    st.subheader('BI Command Center')
    st.caption('KPI hierarchy • contribution analysis • executive summary • recommendations')

    st.write('### 1. KPI Hierarchy')
    hierarchy = kpi_hierarchy(df, m)
    if hierarchy:
        for group, metrics in hierarchy.items():
            st.markdown(f'#### {group}')
            cols = st.columns(min(4, len(metrics)))
            for i, (label, value) in enumerate(metrics.items()):
                suffix = '%' if label == 'Profit Margin' else ''
                cols[i % len(cols)].metric(label, f'{value:,.2f}{suffix}')
    else:
        st.info('Recognizable numeric business fields are required for KPI hierarchy.')

    st.write('### 2. Contribution Analysis')
    dimensions = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c]) and df[c].nunique(dropna=True) <= 100]
    measures = [c for c in [m.get('revenue'), m.get('profit'), m.get('cost'), m.get('quantity')] if c]
    if dimensions and measures:
        ca_dim = st.selectbox('Contribution dimension', dimensions, key='bi_contribution_dimension')
        ca_metric = st.selectbox('Contribution measure', measures, key='bi_contribution_measure')
        contribution = contribution_table(df, ca_dim, ca_metric)
        if not contribution.empty:
            st.dataframe(contribution, use_container_width=True, hide_index=True)
            st.bar_chart(contribution.set_index('Segment')['Value'].head(15))
    else:
        st.info('A categorical dimension and numeric measure are required for contribution analysis.')

    st.write('### 3. Executive Summary')
    summary = executive_summary(df, m)
    if summary:
        for item in summary:
            st.markdown(f'- {item}')
    else:
        st.info('Not enough business fields for an executive summary.')

    st.write('### 4. Decision Recommendations')
    recs = recommendations(df, m)
    if recs:
        for rec in recs:
            st.markdown(f"**{rec['priority']} · {rec['title']}**")
            st.write(rec['detail'])
    else:
        st.info('Recommendations require recognizable revenue, profitability, or dimension fields.')

with tabs[9]:
    st.subheader('Advanced Analytics Lab')
    st.caption('Anomaly detection • forecasting • regression • segment intelligence')
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    date_cols = detect_date_columns(df)
    st.write('### 1. Anomaly Detection')
    if numeric_cols:
        anomaly_col = st.selectbox('Metric for anomaly detection', numeric_cols, key='anomaly_metric')
        threshold = st.slider('Z-score threshold', 1.5, 5.0, 3.0, 0.5)
        anomalies = numeric_anomalies(df, anomaly_col, threshold)
        st.metric('Detected anomalies', int(anomalies['is_anomaly'].sum()))
        st.dataframe(anomalies[anomalies['is_anomaly']].head(100), use_container_width=True, hide_index=True)
    else:
        st.info('Numeric columns are required for anomaly detection.')
    st.write('### 2. Revenue / Metric Forecast')
    if date_cols and numeric_cols:
        fc_date = st.selectbox('Date column', date_cols, key='forecast_date')
        fc_metric = st.selectbox('Metric column', numeric_cols, key='forecast_metric')
        horizon = st.slider('Forecast months', 1, 12, 3)
        forecast = monthly_forecast(df, fc_date, fc_metric, horizon)
        if not forecast.empty:
            st.line_chart(forecast.set_index('date')['value'])
            st.dataframe(forecast, use_container_width=True, hide_index=True)
    else:
        st.info('A date column and numeric metric are required for forecasting.')
    st.write('### 3. Linear Regression')
    if len(numeric_cols) >= 2:
        rx = st.selectbox('Predictor X', numeric_cols, key='reg_x')
        ry = st.selectbox('Target Y', [c for c in numeric_cols if c != rx], key='reg_y')
        result = regression_summary(df, rx, ry)
        if result:
            a,b,c = st.columns(3); a.metric('R²', f"{result['r2']:.3f}"); b.metric('Slope', f"{result['slope']:.4f}"); c.metric('Samples', result['rows'])
            st.caption('R² describes the strength of this simple linear relationship; it does not prove causation.')
        else:
            st.info('Not enough valid variation for regression.')
    st.write('### 4. Segment Statistics')
    dims = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c]) and df[c].nunique(dropna=True) <= 100]
    if dims and numeric_cols:
        sd = st.selectbox('Segment dimension', dims, key='stats_dim')
        sm = st.selectbox('Measure', numeric_cols, key='stats_metric')
        st.dataframe(segment_summary(df, sd, sm), use_container_width=True, hide_index=True)

with tabs[10]:
    st.subheader("AI Business Analyst")
    st.caption("Ask business questions in natural language. Answers are generated from the uploaded, validated dataset.")

    if "ai_question" not in st.session_state:
        st.session_state.ai_question = ""

    examples = [
        "Give me an overview of this dataset",
        "Which region has the highest revenue?",
        "What are the top products by revenue?",
        "Why did revenue change last month?",
        "What is the total profit and profit margin?",
        "Find unusual or anomalous sales",
    ]

    selected_example = st.selectbox("Try a sample question", ["Choose a question..."] + examples)
    question = st.text_input(
        "Ask your business question",
        value=selected_example if selected_example != "Choose a question..." else "",
        placeholder="e.g. Which region contributes the most revenue?",
    )

    if st.button("Analyze Question", type="primary"):
        if not question.strip():
            st.warning("Enter a business question first.")
        else:
            with st.spinner("Running verified analytics..."):
                result = answer_question(df, question)
            st.markdown(f"**Intent detected:** `{result.intent}`")
            st.markdown(f"**Confidence:** `{result.confidence}`")
            st.success(result.answer)
            with st.expander("Show evidence and calculation context"):
                st.json(result.evidence)

with tabs[11]:
    st.subheader('Data Explorer'); st.dataframe(df,use_container_width=True,hide_index=True); st.download_button('Download Dataset as CSV',df.to_csv(index=False).encode(),'insightx_dataset.csv','text/csv')

st.divider(); st.caption('INSIGHTX v0.5 • Built by VRAJ PATEL • Business Intelligence & Analytics Platform')
