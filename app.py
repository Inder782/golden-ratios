import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import date
import numpy as np
from scipy.stats import linregress

st.title("Golden ratios")
st.markdown("#### Enter Stock Symbols")

#get the stock names
col1, col2, col3 = st.columns(3)
with col1:
    stock_1 = st.text_input("Stock1 Symbol:", value="")
with col2:
    stock_2 = st.text_input("Stock2 Symbol:", value="")
with col3:
    stock_3 = st.text_input("Stock3 Symbol:", value="")

#select either period like 1mo , 2mo or custom date range
mode=st.radio("Select data mode:",["Period","Date Range"])
timeframe_options = ["1mo", "3mo", "6mo", "1y", "5y", "max"]
period_selected=None
start_date=None
end_date=None

if mode=="Period":
    period_selected=st.selectbox("Select period",options=timeframe_options)
elif mode =="Date Range":
    start_default=date(2000,1,1)
    end_default=date.today()
    date_range=st.date_input("Select date range",
                         value=(start_default,end_default),
                         min_value=date(2000,1,1),max_value=date(2025,12,31))
    if len(date_range) ==2:
        start_date,end_date=date_range

#fetch data
if stock_1 and stock_2 and stock_3:
    if mode=="Period" and period_selected:
        data1 = yf.download(stock_1, period=period_selected, interval="1d", group_by="ticker")
        data2 = yf.download(stock_2, period=period_selected, interval="1d", group_by="ticker")
        data3 = yf.download(stock_3, period=period_selected, interval="1d", group_by="ticker")

    elif mode=="Date Range" and start_date and end_date:
        data1 = yf.download(stock_1, start=start_date,end=end_date,interval="1d", group_by="ticker")
        data2 = yf.download(stock_2, start=start_date,end=end_date,interval="1d", group_by="ticker")
        data3 = yf.download(stock_3, start=start_date,end=end_date,interval="1d", group_by="ticker")

    data1 = data1.reset_index()
    data2 = data2.reset_index()
    data3 = data3.reset_index()
    
    # For single ticker, columns are not MultiIndex after reset_index, just use 'Date' and 'Close'
    if isinstance(data1.columns, pd.MultiIndex):
        df1 = data1[[('Date', ''), (stock_1, 'Close')]].copy()
        df1.columns = ['Date', f'{stock_1}_Close']
        df2 = data2[[('Date', ''), (stock_2, 'Close')]].copy()
        df2.columns = ['Date', f'{stock_2}_Close']
        df3 = data3[[('Date', ''), (stock_3, 'Close')]].copy()
        df3.columns = ['Date', f'{stock_3}_Close']
    else:
        df1 = data1[['Date', 'Close']].rename(columns={'Close': f'{stock_1}_Close'})
        df2 = data2[['Date', 'Close']].rename(columns={'Close': f'{stock_2}_Close'})
        df3 = data3[['Date', 'Close']].rename(columns={'Close': f'{stock_3}_Close'})
    
    # Merge all three on 'Date'
    merged_df = pd.merge(df1, df2, on='Date', how='outer')
    merged_df = pd.merge(merged_df, df3, on='Date', how='outer')
    merged_df = merged_df.sort_values('Date')

    for stock in [stock_1,stock_2,stock_3]:
        closing_prices=f"{stock}_Close"
        merged_df[f"{stock}_return"]=merged_df[closing_prices].pct_change()*100
        merged_df[f"{stock}_lnR"]=np.log(merged_df[closing_prices]/merged_df[closing_prices].shift(1))
        merged_df[f"{stock}_ln^2"]=merged_df[f"{stock}_lnR"]**2

    #storing simpleReturns,Ln returns, Ln^2 returns, daily vol, yearly vol, veta , alpha for calc
    avg_returns={stock:merged_df[f"{stock}_return"].mean() for stock in [stock_1,stock_2,stock_3]}
    
    avg_ln_returns={stock:merged_df[f"{stock}_lnR"].mean() for stock in [stock_1,stock_2,stock_3]}
    avg_ln_sq_returns={stock:merged_df[f"{stock}_ln^2"].mean() for stock in [stock_1,stock_2,stock_3]}
    daily_vol={stock:np.sqrt(avg_ln_sq_returns[stock]-avg_ln_returns[stock]**2) for stock in [stock_1,stock_2,stock_3]}
    yearly_vol={stock:daily_vol[stock]*np.sqrt(365) for stock in [stock_1,stock_2,stock_3]}

    def get_ratios(stockA,stockB):
        df=merged_df[[f"{stockA}_return",f"{stockB}_return"]].dropna()
        X=df[f"{stockA}_return"]
        Y=df[f"{stockB}_return"]
        slope,intercept,r_value,p_value,std_err=linregress(X,Y)
        alpha= avg_returns[stockB]-slope*avg_returns[stockA]

        # Example risk-free rate
        risk_free = 0.06

        # Jensen's Alpha
        j_alphaA = avg_returns[stockA] - (risk_free + slope * (avg_returns[stockB] - risk_free))
        j_alphaB = avg_returns[stockB] - (risk_free + slope * (avg_returns[stockA] - risk_free))
        # Sharpe Ratio
        sharpeA = (avg_returns[stockA] - risk_free) / yearly_vol[stockA] if yearly_vol[stockA] != 0 else np.nan
        sharpeB = (avg_returns[stockB] - risk_free) / yearly_vol[stockB] if yearly_vol[stockB] != 0 else np.nan
        # Treynor Ratio
        treynorA = (avg_returns[stockA] - risk_free) / slope if slope != 0 else np.nan
        treynorB = (avg_returns[stockB] - risk_free) / slope if slope != 0 else np.nan

        ratios = {
        f"Beta ({stockA} vs {stockB})": slope,
        f"Alpha ({stockA} vs {stockB})": alpha,
        f"Jensen Alpha {stockA}": j_alphaA,
        f"Jensen Alpha {stockB}": j_alphaB,
        f"Sharpe Ratio {stockA}": sharpeA,
        f"Sharpe Ratio {stockB}": sharpeB,
        f"Treynor Ratio {stockA}": treynorA,
        f"Treynor Ratio {stockB}": treynorB,
        f"Correlation": r_value,
        }

        ratios_df=pd.DataFrame([ratios])
        return ratios_df
    #all stocks ratios
    ratios_a_b=get_ratios(stock_1,stock_2)
    ratios_b_c=get_ratios(stock_2,stock_3)
    ratios_a_c=get_ratios(stock_1,stock_3)

    def format_ratios_df(ratios_df, stockA, stockB):
        # Transpose so metrics are rows, stocks are columns
        ratios_df = ratios_df.T
        # Reset index to get metric names as a column
        ratios_df = ratios_df.reset_index()
        # Rename columns for clarity
        ratios_df.columns = ['Metric', f"{stockA} & {stockB}"]
        return ratios_df
    
    # Format each ratios DataFrame
    ratios_a_b_disp = format_ratios_df(ratios_a_b, stock_1, stock_2)
    ratios_b_c_disp = format_ratios_df(ratios_b_c, stock_2, stock_3)
    ratios_a_c_disp = format_ratios_df(ratios_a_c, stock_1, stock_3)

    df_option=st.selectbox(
        "Select Dataframe to display:",
        (
            "Returns Dataframe",
            f"{stock_1} & {stock_2} ratios",
            f"{stock_2} & {stock_3} ratios",
            f"{stock_1} & {stock_3} ratios",
        )
    )
    if df_option=="Returns Dataframe":
        st.subheader("Returns Dataframe")
        st.dataframe(merged_df)
    elif df_option== f"{stock_1} & {stock_2} ratios":
                st.subheader( f"{stock_1} & {stock_2} ratios")
                st.dataframe(ratios_a_b_disp)
    elif df_option== f"{stock_2} & {stock_3} ratios":
                 st.subheader( f"{stock_2} & {stock_3} ratios")
                 st.dataframe(ratios_b_c_disp)
    elif df_option== f"{stock_1} & {stock_3} ratios":
                 st.subheader( f"{stock_1} & {stock_3} ratios")
                 st.dataframe( ratios_a_c_disp)

else:
    st.info("Please enter a valid stock symbol")

