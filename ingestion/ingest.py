import requests
import pandas as pd
import os
import schedule
import time
from datetime import datetime
import psycopg2

#configuration
TICKERS = ['AAPL', 'GOOGL', 'MSFT' , 'NVDA' , 'TSLA' , 'AMZN'] # List of stock tickers to ingest
RAW_DATA_DIR = '/data/raw' # Directory to save raw data

DB_HOST = os.environ.get('DB_HOST')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_NAME = os.environ.get('DB_NAME')
API_KEY = os.environ.get('TWELVE_DATA_API_KEY')

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME
    )

def wait_for_db():
    """Wait for the database to be ready before proceeding"""
    print("Waiting for database to be ready...")
    retries = 0
    while retries < 10:
        try:
            conn = get_db_connection()
            conn.close()
            print("Database is ready!")
            return
        except Exception as e:
            retries += 1
            print(f"  Not ready yet, retrying in 3 seconds... ({retries}/10)")
            time.sleep(3)
    raise Exception("Could not connect to database after 10 retries")
            

def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock_prices (
        id SERIAL PRIMARY KEY,
        ticker VARCHAR(10),
        date DATE,
        open FLOAT,
        high FLOAT,
        low FLOAT,
        close FLOAT,
        volume BIGINT,
        created_at TIMESTAMP DEFAULT NOW()
    )
    """)
    conn.commit()
    cursor.close()
    conn.close()
    print("Table ready!")

def save_to_db(df , ticker):
    conn = get_db_connection()
    cursor = conn.cursor()
    for index, row in df.iterrows():
        cursor.execute("""
        INSERT INTO stock_prices (ticker, date, open, high, low, close, volume)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        """, (ticker, row['Date'], row['Open'], row['High'], row['Low'], row['Close'], row['Volume']))
    conn.commit()
    cursor.close()
    conn.close()

def fetch_ticker(ticker):
    url = "https://api.twelvedata.com/time_series"
    params = {
        'symbol': ticker,
        'interval': '1day',
        'outputsize': 5,
        'apikey': API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()

    if 'values' not in data:
        print(f"Error fetching data for {ticker}: {data.get('message', 'Unknown error')}")
        return None
    df = pd.DataFrame(data['values'])
    df['Date'] = pd.to_datetime(df['datetime']).dt.date
    df = df.rename(columns={"datetime": "raw_datetime"})
    df[['Open', 'High', 'Low', 'Close']] = df[['open', 'high', 'low', 'close']].astype(float)
    df['Volume'] = df['volume'].astype(int)
    return df

def fetch_stock_data():
    print(f"[{datetime.now()}] Fetching stock data ...")
    for ticker in TICKERS:
        try:

            df = fetch_ticker(ticker)
            
            if df is None or df.empty:
                print(f"No data found for {ticker}")
                continue
            

            #Save to CSV
            filename = f"{ticker}_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
            filepath = os.path.join(RAW_DATA_DIR, filename)
            df.to_csv(filepath , index=False)
            print(f"Saved data for {ticker} to {filepath}")

            #Save to DB
            save_to_db(df , ticker)
            print(f"Saved data to database -> {ticker}")


        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            return None
        #wait a bit before fetching next ticker to avoid hitting API limits
        time.sleep(2)

    print("Done!\n")

#Wait for DB to be ready before starting
wait_for_db()

#create table on startup
create_table()

#Run once immediately when container starts
fetch_stock_data()

#Schedule to run every day at 6 pm
schedule.every().day.at("18:00").do(fetch_stock_data)

print("Scheduler running - will fetch stock data every day at 6 pm")
while True:
    schedule.run_pending()
    time.sleep(60) # Sleep for 1 minute before checking again