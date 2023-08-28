import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from stocknews import StockNews
from alpha_vantage.fundamentaldata import FundamentalData


# Set Streamlit theme
st.set_page_config(layout="wide")  # Uncomment this line for wider layout

st.title('Stock Dashboard')
ticker = st.sidebar.text_input('Ticker')
start_date = st.sidebar.date_input('Start Date')
end_date = st.sidebar.date_input('End Date')

data = yf.download(ticker, start=start_date, end=end_date)
fig = px.line(data, x=data.index, y=data['Adj Close'], title=ticker)
fig.update_layout(width=1100, height=600)
st.plotly_chart(fig)

fig_candlestick = go.Figure(data=[go.Candlestick(x=data.index,
                                                  open=data['Open'],
                                                  high=data['High'],
                                                  low=data['Low'],
                                                  close=data['Close'])])
fig_candlestick.update_layout(title=f'{ticker} Candlestick Chart')
fig_candlestick.update_layout(width=1100, height=600)
st.plotly_chart(fig_candlestick)

# Create buttons in the sidebar for different sections
if st.sidebar.button("Pricing Data"):
    st.header('Price Movements')
    data2 = data.copy()
    data2['% Change'] = data['Adj Close'] / data['Adj Close'].shift(1)
    data2.dropna(inplace=True)
    st.write(data2)
    annual_return = data2['% Change'].mean() * 252 * 100
    st.write('Annual Return is', annual_return, '%')
    stdev = np.std(data2['% Change']) * np.sqrt(252)
    st.write('Standard Deviation is', stdev * 100, '%')
    st.write('Risk Adj. Return is', annual_return / (stdev * 100))

if st.sidebar.button("Fundamental Data"):
    st.subheader('Fundamental Data')
    key='f63c3ffb79d9df79'  # Replace with your Alpha Vantage API key
    fd = FundamentalData(key, output_format='pandas')
    
    st.subheader('Balance Sheet')
    balance_sheet = fd.get_balance_sheet_annual(ticker)[0]
    st.write(balance_sheet)
    
    st.subheader('Income Statement')
    income_statement = fd.get_income_statement_annual(ticker)[0]
    st.write(income_statement)
    
    st.subheader('Cash Flow Statement')
    cash_flow = fd.get_cash_flow_annual(ticker)[0]
    st.write(cash_flow)

if st.sidebar.button("Top 10 News"):
    st.header(f'News of {ticker}')
    sn = StockNews(ticker, save_news=False)
    df_news = sn.read_rss()
    for i in range(10):
        with st.expander(f'News {i + 1} - {df_news["published"][i]}'):
            st.write(df_news['title'][i])
            st.write(df_news['summary'][i])
            title_sentiment = df_news['sentiment_title'][i]
            st.write(f'Title Sentiment: {title_sentiment}')
            news_sentiment = df_news['sentiment_summary'][i]
            st.write(f'News Sentiment: {news_sentiment}')
