import os
import time
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

# Function to fetch news sentiment
def fetch_news_sentiment(symbol):
    print(f"Fetching news sentiment for {symbol}...")

    try:
        newsapi = NewsApiClient(api_key=NEWS_API_KEY)
    except Exception as e:
        print(f"Failed to initialize News API Client: {e}")
        return

    # Query multiple related terms to get broader results
    queries = [symbol, "SPDR S&P 500 ETF Trust", "S&P 500", "S&P 500 Index"]
    news_data = []

    for query in queries:
        try:
            articles = newsapi.get_everything(q=query, language="en", sort_by="publishedAt", page_size=50)
            
            if "articles" not in articles or not articles["articles"]:
                print(f"No news articles found for '{query}'")
                continue
            
            # Process each article
            for article in articles["articles"]:
                title = article.get("title", "")
                description = article.get("description", "")
                content = article.get("content", "")
                text = f"{title} {description} {content}".strip()

                if not text:
                    continue  # Skip empty articles
                
                # Get VADER sentiment
                vaderScore = vader.polarity_scores(text)["compound"]
                
                # Get FinBERT sentiment
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
            time.sleep(5)  # Avoid hitting API rate limits

    # Save results
    if news_data:
        df = pd.DataFrame(news_data)
        filename = f"{symbol}_news_sentiment.csv"
        df.to_csv(filename, index=False)
        print(f"News sentiment saved to {filename}")
    else:
        print("No valid articles found. Nothing saved.")

# Run function
fetch_news_sentiment("SPDR S&P 500")
