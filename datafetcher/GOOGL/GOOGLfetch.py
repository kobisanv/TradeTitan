#!/usr/bin/env python3
"""GOOGL Stock Data Fetcher with Sentiment Analysis"""

import os
import time
import yfinance as yf
import pandas as pd
from dotenv import load_dotenv
from newsapi import NewsApiClient
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import pipeline

load_dotenv()

class GOOGLFetcher:
    def __init__(self):
        self.symbol = "GOOGL"
        self.ticker = yf.Ticker(self.symbol)
        
        # Initialize sentiment analyzers
        self.vader = SentimentIntensityAnalyzer()
        self.finbert = pipeline("text-classification", model="ProsusAI/finbert", trust_remote_code=True)
        
        # News API setup
        self.news_api_key = os.getenv("NEWSAPI_KEY")
        if not self.news_api_key:
            print("Warning: Missing NewsAPI key. News sentiment analysis will be skipped.")
        
        # Timeframes for data fetching
        self.timeframes = {
            "1h": ("2y", "GOOGL_1h.csv"),    # 2 years of hourly data
            "1d": ("5y", "GOOGL_1d.csv"),    # 5 years of daily data
            "1wk": ("10y", "GOOGL_1wk.csv"), # 10 years of weekly data
            "1mo": ("20y", "GOOGL_1mo.csv"), # 20 years of monthly data
        }
    
    def calculate_technical_indicators(self, data):
        """Calculate technical indicators for the stock data."""
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
        
        return data
    
    def fetch_and_save_data(self, interval, period, filename, retries=3):
        """Fetch stock data and save to CSV with technical indicators."""
        print(f"Fetching {period} of {interval} data for {self.symbol}...")
        
        for attempt in range(retries):
            try:
                data = self.ticker.history(period=period, interval=interval, auto_adjust=False)
                if data.empty:
                    raise ValueError("No data received. Possible API limit or incorrect parameters.")
                
                # Add technical indicators
                data = self.calculate_technical_indicators(data)
                
                data.to_csv(filename)
                print(f"Data saved to {filename}")
                return
            
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                time.sleep(5)
        
        print(f"Failed to fetch {interval} data after {retries} attempts.")
    
    def fetch_news_sentiment(self):
        """Fetch news articles and perform sentiment analysis."""
        if not self.news_api_key:
            print("Skipping news sentiment analysis - no API key provided.")
            return
        
        print(f"Fetching news sentiment for {self.symbol}...")

        try:
            newsapi = NewsApiClient(api_key=self.news_api_key)
        except Exception as e:
            print(f"Failed to initialize News API Client: {e}")
            return

        queries = [self.symbol, "Alphabet", "GOOG", "Google"]
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
                    
                    vader_score = self.vader.polarity_scores(text)["compound"]
                    finbert_result = self.finbert(text)[0]["label"]

                    news_data.append({
                        "query": query,
                        "title": title,
                        "description": description,
                        "content": content,
                        "vaderScore": vader_score,
                        "finbertResult": finbert_result
                    })

                print(f"Processed {len(articles['articles'])} articles for '{query}'")

            except Exception as e:
                print(f"News API error for '{query}': {e}")
                time.sleep(5)

        if news_data:
            df = pd.DataFrame(news_data)
            filename = f"{self.symbol}_news_sentiment.csv"
            df.to_csv(filename, index=False)
            print(f"News sentiment saved to {filename}")
        else:
            print("No valid articles found. Nothing saved.")
    
    def run_complete_fetch(self):
        """Run complete data fetching process."""
        print(f"Starting complete data fetch for {self.symbol}...")
        
        # Fetch all timeframe data
        for interval, (period, filename) in self.timeframes.items():
            self.fetch_and_save_data(interval, period, filename)
            time.sleep(10)
        
        # Fetch news sentiment
        self.fetch_news_sentiment()
        
        print(f"✅ Complete data fetch finished for {self.symbol}")

def main():
    """Main execution function."""
    fetcher = GOOGLFetcher()
    fetcher.run_complete_fetch()

if __name__ == "__main__":
    main()