# StockPulse 📈

End-to-end stock market data engineering pipeline built with Python, Docker, PostgreSQL and Apache Airflow.

## Architecture
- **Ingestion** — Fetches OHLCV data for 5 tickers from Tweleve Data API
- **Storage** — Saves raw CSV files to a local data lake (S3-compatible structure)
- **Processing** — PySpark transformations (coming soon)
- **Warehouse** — PostgreSQL (coming soon)
- **Dashboard** — Apache Superset (coming soon)

## Tech Stack
- Python 3.11
- Docker + Docker Compose
- yfinance + pandas
- PostgreSQL (coming soon)
- Apache Airflow (coming soon)
- Apache Superset (coming soon)

## How to Run
```bash
git clone https://github.com/PragyaKatiyar/Stockpulse.git
cd Stockpulse
docker compose up --build
```

## Project Structure
```
stockpulse/
  ingestion/
    ingest.py         # Fetches stock data from Tweleve Data API
    Dockerfile        # Container definition
    requirements.txt  # Python dependencies
  data/
    raw/              # Raw CSV files land here
  docker-compose.yml  # Orchestrates all services
```
