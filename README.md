🪙 Silver Tracker API

A robust, full-stack REST API built with FastAPI and Python to track real-time Silver prices across multiple currencies (USD, TRY, SYP). This backend serves as the core engine for the Silver Tracker Mobile App.

It combines real-time financial data, web scraping, and bank rate simulation to provide accurate buy/sell prices, specifically tailored for the Turkish and Syrian markets.

🚀 Features

Multi-Source Data Fetching:

Fetches global spot prices via yfinance (Yahoo Finance).

Automates Syrian Lira (SYP) black market rate scraping using BeautifulSoup.

Simulates/Scrapes Kuveyt Türk bank spreads (Buy/Sell) for accurate local pricing.

Historical Analysis:

Stores and retrieves 5-year historical data for charting.

Uses Pandas for data processing and time-series analysis.

Wallet System:

Integrated SQLite database to track user holdings (grams).

Calculates total wealth in USD, TRY, and SYP instantly.

Security:

Protected endpoints using API Key Authentication to prevent unauthorized wallet modifications.

Robustness:

Includes fallback mechanisms and mathematical calibration to ensure zero downtime even during market holidays or scraping failures.

🛠️ Tech Stack

Framework: FastAPI

Language: Python 3.x

Database: SQLite3

Data Analysis: Pandas, NumPy

Scraping & Finance: Selenium, BeautifulSoup4, YFinance

Server: Uvicorn

🔌 API Endpoints

1. General Data (The Super Endpoint)

GET /all_data

Returns a comprehensive JSON object containing:

Current Silver price per gram (USD, TRY, SYP).

Exchange rates (USD/TRY, USD/SYP).

Bank Buy/Sell simulation prices.

User's wallet balance.

Historical data points (Date & Price) for charts.

2. Wallet Management (Secured)

POST /update_wallet

Updates the user's silver holdings in the database.

Requires Header: x-api-key: YOUR_SECRET_KEY

Body: {"grams": 150.5}

3. Server Health

GET /

Checks if the API is running and connected.

⚙️ How to Run Locally

Clone the repository:

git clone [https://github.com/masalmahn/silver-server.git](https://github.com/masalmahn/silver-server.git)
cd silver-server


Install dependencies:

pip install -r requirements.txt


Run the server:

python -m uvicorn main:app --reload


Access the API:
Open your browser and go to http://127.0.0.1:8000

☁️ Deployment

This project includes a requirements.txt file ready for deployment on cloud platforms like Render, Heroku, or AWS.

Build Command: pip install -r requirements.txt

Start Command: uvicorn main:app --host 0.0.0.0 --port 10000

🛡️ Configuration

You can adjust the calibration settings in main.py to match local bank rates manually if needed:

# Calibration Settings
CALIBRATION = 1.12  # Global price multiplier
BANK_SPREAD = 7.35  # Buy/Sell spread simulation
FALLBACK_SYP_RATE = 15200.0  # Fallback for scraping failure


Developed with ❤️ by Naser Masalmah (@masalmahn)
