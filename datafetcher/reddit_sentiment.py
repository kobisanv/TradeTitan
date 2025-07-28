#!/usr/bin/env python3
import os
import time
import requests
import pandas as pd
from datetime import datetime, timedelta
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import pipeline
from dotenv import load_dotenv

load_dotenv()

# Initialize sentiment analyzers (same as your existing code)
vader = SentimentIntensityAnalyzer()
finbert = pipeline("text-classification", model="ProsusAI/finbert", trust_remote_code=True)

class RedditSentimentFetcher:
    def __init__(self):
        self.analyzer = vader
        self.finbert_model = finbert
        print("Reddit sentiment fetcher initialized - using free Tradestie API")
    
    def get_tradestie_reddit_data(self, ticker):
        """Get Reddit sentiment from Tradestie API (free tier)."""
        try:
            url = "https://tradestie.com/api/v1/apps/reddit"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Find ticker in the data
                ticker_data = None
                for item in data:
                    if item.get('ticker', '').upper() == ticker.upper():
                        ticker_data = item
                        break
                
                if ticker_data:
                    return {
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'ticker': ticker,
                        'mentions': ticker_data.get('no_of_comments', 0),
                        'sentiment': ticker_data.get('sentiment', 0),
                        'sentiment_score': ticker_data.get('sentiment_score', 0),
                        'source': 'tradestie_reddit'
                    }
            
        except Exception as e:
            print(f"Error fetching Tradestie Reddit data: {str(e)}")
        
        return None
    
    def get_reddit_posts_pushshift(self, ticker, days_back=1, limit=100):
        """Get Reddit posts using Pushshift API (alternative method)."""
        try:
            # Calculate timestamp for days back
            end_time = int(datetime.now().timestamp())
            start_time = int((datetime.now() - timedelta(days=days_back)).timestamp())
            
            # Search multiple subreddits
            subreddits = ['wallstreetbets', 'stocks', 'investing', 'SecurityAnalysis', 'ValueInvesting']
            all_posts = []
            
            for subreddit in subreddits:
                try:
                    url = f"https://api.pushshift.io/reddit/search/submission/"
                    params = {
                        'subreddit': subreddit,
                        'q': ticker,
                        'after': start_time,
                        'before': end_time,
                        'size': limit,
                        'sort': 'desc',
                        'sort_type': 'score'
                    }
                    
                    response = requests.get(url, params=params, timeout=15)
                    
                    if response.status_code == 200:
                        data = response.json()
                        posts = data.get('data', [])
                        
                        for post in posts:
                            # Combine title and selftext for sentiment analysis
                            text_content = f"{post.get('title', '')} {post.get('selftext', '')}"
                            
                            if len(text_content.strip()) > 10:  # Skip very short posts
                                # Apply same sentiment analysis as your news fetcher
                                vaderScore = self.analyzer.polarity_scores(text_content)["compound"]
                                finbertResult = self.finbert_model(text_content[:512])[0]["label"]  # FinBERT has token limit
                                
                                all_posts.append({
                                    'timestamp': datetime.fromtimestamp(post.get('created_utc', 0)),
                                    'subreddit': subreddit,
                                    'title': post.get('title', ''),
                                    'selftext': post.get('selftext', ''),
                                    'score': post.get('score', 0),
                                    'upvote_ratio': post.get('upvote_ratio', 0),
                                    'num_comments': post.get('num_comments', 0),
                                    'author': post.get('author', 'deleted'),
                                    'url': f"https://reddit.com{post.get('permalink', '')}",
                                    'vaderScore': vaderScore,
                                    'finbertResult': finbertResult
                                })
                    
                    time.sleep(1)  # Rate limiting
                    
                except Exception as e:
                    print(f"Error fetching from r/{subreddit}: {str(e)}")
                    continue
            
            return all_posts
            
        except Exception as e:
            print(f"Error in Reddit posts fetch: {str(e)}")
            return []
    
    def get_reddit_sentiment_summary(self, ticker):
        """Get aggregated Reddit sentiment data."""
        try:
            # Use Tradestie API (free, no keys needed)
            tradestie_data = self.get_tradestie_reddit_data(ticker)
            
            sentiment_data = []
            
            # Add Tradestie data
            if tradestie_data:
                sentiment_data.append(tradestie_data)
                print(f"Found Reddit data for {ticker}: {tradestie_data['mentions']} mentions, sentiment: {tradestie_data['sentiment']}")
            else:
                print(f"No Reddit sentiment data found for {ticker} from Tradestie API")
            
            return sentiment_data, pd.DataFrame()
            
        except Exception as e:
            print(f"Error getting Reddit sentiment summary: {str(e)}")
            return [], pd.DataFrame()
    
    def fetch_and_save_reddit_sentiment(self, ticker, output_dir):
        """Main function to fetch and save Reddit sentiment (matches your news fetcher pattern)."""
        print(f"Fetching Reddit sentiment for {ticker}...")
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Get sentiment data
        sentiment_summary, detailed_posts = self.get_reddit_sentiment_summary(ticker)
        
        # Save summary data (like your news sentiment CSV)
        if sentiment_summary:
            summary_df = pd.DataFrame(sentiment_summary)
            summary_file = os.path.join(output_dir, f"{ticker}_reddit_sentiment.csv")
            
            # Append to existing file or create new (matches your pattern)
            if os.path.exists(summary_file):
                existing_df = pd.read_csv(summary_file)
                combined_df = pd.concat([existing_df, summary_df], ignore_index=True)
                combined_df.to_csv(summary_file, index=False)
            else:
                summary_df.to_csv(summary_file, index=False)
            
            print(f"Saved Reddit sentiment summary to {summary_file}")
        
        # Save detailed posts (like your detailed news data)
        if not detailed_posts.empty:
            detailed_file = os.path.join(output_dir, f"{ticker}_reddit_posts.csv")
            detailed_posts.to_csv(detailed_file, index=False)
            print(f"Saved {len(detailed_posts)} Reddit posts to {detailed_file}")
        
        return sentiment_summary

def main():
    """Test the Reddit sentiment fetcher."""
    fetcher = RedditSentimentFetcher()
    
    # Test with same ticker as your example
    test_ticker = "NVDA"
    output_dir = f"/app/data/{test_ticker}"
    
    sentiment_data = fetcher.fetch_and_save_reddit_sentiment(test_ticker, output_dir)
    
    if sentiment_data:
        print(f"Successfully fetched Reddit sentiment for {test_ticker}")
        for data in sentiment_data:
            print(f"Data: {data}")
    else:
        print(f"No Reddit sentiment data found for {test_ticker}")

if __name__ == "__main__":
    main()