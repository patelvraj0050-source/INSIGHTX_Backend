import pandas as pd
from src.kpi_engine import detect_business_columns,calculate_kpis
def test_kpi_engine():
    df=pd.DataFrame({"Revenue":[100,200,300],"Profit":[10,40,60],"Order ID":["A","B","C"],"Quantity":[1,2,3],"Region":["West","East","West"]})
    k=calculate_kpis(df,detect_business_columns(df))
    assert "Revenue" in k and "Profit" in k and "Profit Margin" in k
