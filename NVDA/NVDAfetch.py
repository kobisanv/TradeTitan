import os
import time
import yfinance as yf
import pandas as pd
from dotenv import load_dotenv
from newsapi import NewsApiClient
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import pipeline

# Load environment variables
load_dotenv()
NEWS_API_KEY = os.getenv("NEWSAPI_KEY")
if not NEWS_API_KEY:
    raise ValueError("Missing NewsAPI key. Set NEWSAPI_KEY in environment variables.")

# Initialize sentiment analyzers
vader = SentimentIntensityAnalyzer()
finbert = pipeline("text-classification", model="ProsusAI/finbert", trust_remote_code=True)

symbol = "NVDA"
ticker = yf.Ticker(symbol)

timeframes = {
    "1h": ("2y", "NVDA_1h.csv"),    # 2 years of hourly data
    "1d": ("5y", "NVDA_1d.csv"),    # 5 years of daily data
    "1wk": ("10y", "NVDA_1wk.csv"), # 10 years of weekly data
    "1mo": ("20y", "NVDA_1mo.csv"), # 20 years of monthly data
}

def fetch_and_save_data(interval, period, filename, retries=3):
    print(f"Fetching {period} of {interval} data for {symbol}...")
    
    for attempt in range(retries):
        try:
            data = ticker.history(period=period, interval=interval, auto_adjust=False)
            if data.empty:
                raise ValueError("No data received. Possible API limit or incorrect parameters.")
            
            # Moving Averages (EMA 50 & 200)
            data["50_EMA"] = data["Close"].ewm(span=50, adjust=False).mean()
            data["200_EMA"] = data["Close"].ewm(span=200, adjust=False).mean()
            
            # RSI (Relative Strength Index) (14-day)
            delta = data["Close"].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            data["RSI"] = 100 - (100 / (1 + rs))
            
            # MACD (Moving Average Convergence Divergence) (12,26,9)
            short_ema = data["Close"].ewm(span=12, adjust=False).mean()
            long_ema = data["Close"].ewm(span=26, adjust=False).mean()
            data["MACD"] = short_ema - long_ema
            data["Signal"] = data["MACD"].ewm(span=9, adjust=False).mean()
            
            # OBV (On-Balance Volume)
            data["OBV"] = (data["Volume"] * (data["Close"].diff().apply(lambda x: 1 if x > 0 else -1))).fillna(0).cumsum()
            
            data.to_csv(filename)
            print(f"Data saved to {filename}")
            return
        
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(5)
    
    print(f"Failed to fetch {interval} data after {retries} attempts.")

def fetch_news_sentiment(symbol):
    print(f"Fetching news sentiment for {symbol}...")

    try:
        newsapi = NewsApiClient(api_key=NEWS_API_KEY)
    except Exception as e:
        print(f"Failed to initialize News API Client: {e}")
        return

    queries = [symbol, "NVIDIA", "NVIDIA CORP", "Nvidia"]
    news_data = []

    for query in queries:
        try:
            articles = newsapi.get_everything(q=query, language="en", sort_by="publishedAt", page_size=50)
            
            if "articles" not in articles or not articles["articles"]:
                print(f"No news articles found for '{query}'")
                continue
            
            for article in articles["articles"]:
                title = article.get("title", "")
                description = article.get("description", "")
                content = article.get("content", "")
                text = f"{title} {description} {content}".strip()

                if not text:
                    continue
                
                vaderScore = vader.polarity_scores(text)["compound"]
                
                finbertResult = finbert(text)[0]["label"]

                news_data.append({
                    "query": query,
                    "title": title,
                    "description": description,
                    "content": content,
                    "vaderScore": vaderScore,
                    "finbertResult": finbertResult
                })

            print(f"Processed {len(articles['articles'])} articles for '{query}'")

        except Exception as e:
            print(f"News API error for '{query}': {e}")
            time.sleep(5)

    if news_data:
        df = pd.DataFrame(news_data)
        filename = f"{symbol}_news_sentiment.csv"
        df.to_csv(filename, index=False)
        print(f"News sentiment saved to {filename}")
    else:
        print("No valid articles found. Nothing saved.")

for interval, (period, filename) in timeframes.items():
    fetch_and_save_data(interval, period, filename)
    time.sleep(10)

fetch_news_sentiment("NVDA")