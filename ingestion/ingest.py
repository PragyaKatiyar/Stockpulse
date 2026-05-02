import yfinance as yf
import pandas as pd
import os
import schedule
import time
from datetime import datetime

#configuration
TICKERS = ['AAPL', 'GOOGL', 'MSFT' , 'NVDA' , 'TSLA' , 'AMZN'] # List of stock tickers to ingest
RAW_DATA_DIR = '/data/raw' # Directory to save raw data

def fetch_stock_data(ticker):
    print(f"[{datetime.now()}] Fetching stock data ...")
    for ticker in TICKERS:
        try:
            #Download last 5 days of stock data
            df = yf.download(ticker, period='5d' , interval='1d')
            if df.empty:
                print(f"No data found for {ticker}")
                continue
            #Add ticker column
            df['Ticker'] = ticker
            df.reset_index(inplace=True)

            #Save to CSV
            filename = f"{ticker}_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
            filepath = os.path.join(RAW_DATA_DIR, filename)
            df.to_csv(filepath , index=False)
            print(f"Saved data for {ticker} to {filepath}")


        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            return None
    
    print("Done!\n")

#Run once immediately when container starts
fetch_stock_data()

#Schedule to run every day at 6 pm
schedule.every().day.at("18:00").do(fetch_stock_data)

print("Scheduler running - will fetch stock data every day at 6 pm")
while True:
    schedule.run_pending()
    time.sleep(60) # Sleep for 1 minute before checking again