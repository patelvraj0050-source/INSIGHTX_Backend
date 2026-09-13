import plotly.express as px
def plot_histogram(df,c): return px.histogram(df,x=c,title=f"Distribution of {c}",marginal="box")
def plot_box(df,c): return px.box(df,y=c,title=f"Box Plot — {c}")
def plot_correlation(c): return px.imshow(c,text_auto=True,aspect="auto",title="Correlation Matrix")
def plot_bar(df,x,y,title): return px.bar(df,x=x,y=y,title=title)
def plot_scatter(df,x,y): return px.scatter(df,x=x,y=y,trendline="ols",title=f"{y} vs {x}")
def plot_time_series(df,m): return px.line(df,x="Period",y=m,markers=True,title=f"{m} Trend")
