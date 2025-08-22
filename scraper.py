#!/usr/bin/env python3
"""
Web scraper for http://127.0.0.1:8080/elonmusk - Extract individual tweets
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urljoin
import re

class ElonMuskScraper:
    def __init__(self, base_url="http://127.0.0.1:8080"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def extract_tweet_stats(self, tweet_element):
        """Extract tweet stats (likes, retweets, etc.)"""
        stats = {}
        stats_elements = tweet_element.find_all('span', class_='tweet-stat')
        
        for stat in stats_elements:
            icon = stat.find('span', class_=lambda x: x and 'icon-' in x)
            if icon:
                stat_type = None
                if 'icon-comment' in icon.get('class', []):
                    stat_type = 'replies'
                elif 'icon-retweet' in icon.get('class', []):
                    stat_type = 'retweets'
                elif 'icon-quote' in icon.get('class', []):
                    stat_type = 'quotes'
                elif 'icon-heart' in icon.get('class', []):
                    stat_type = 'likes'
                elif 'icon-play' in icon.get('class', []):
                    stat_type = 'views'
                
                if stat_type:
                    stat_text = stat.get_text(strip=True)
                    # Extract number from text like "2,848"
                    numbers = re.findall(r'[\d,]+', stat_text)
                    if numbers:
                        stats[stat_type] = numbers[0].replace(',', '')
        
        return stats

    def extract_quoted_tweet(self, tweet_element):
        """Extract quoted tweet information"""
        quote = tweet_element.find('div', class_='quote')
        if not quote:
            return None
            
        quoted_tweet = {}
        
        # Author info
        name_row = quote.find('div', class_='tweet-name-row')
        if name_row:
            fullname_elem = name_row.find('a', class_='fullname')
            username_elem = name_row.find('a', class_='username')
            date_elem = name_row.find('span', class_='tweet-date')
            
            if fullname_elem:
                quoted_tweet['author'] = fullname_elem.get_text(strip=True)
            if username_elem:
                quoted_tweet['username'] = username_elem.get_text(strip=True)
            if date_elem:
                quoted_tweet['date'] = date_elem.get_text(strip=True)
        
        # Quote text
        quote_text = quote.find('div', class_='quote-text')
        if quote_text:
            quoted_tweet['text'] = quote_text.get_text(strip=True)
        
        # Quote link
        quote_link = quote.find('a', class_='quote-link')
        if quote_link and quote_link.get('href'):
            quoted_tweet['link'] = quote_link['href']
        
        return quoted_tweet

    def extract_media_info(self, tweet_element):
        """Extract media information (images, videos)"""
        media = []
        
        # Find attachments
        attachments = tweet_element.find('div', class_='attachments')
        if attachments:
            # Images
            images = attachments.find_all('img')
            for img in images:
                if img.get('src'):
                    media.append({
                        'type': 'image',
                        'src': img['src'],
                        'alt': img.get('alt', '')
                    })
            
            # Videos
            video_containers = attachments.find_all('div', class_='video-container')
            for video in video_containers:
                img = video.find('img')
                if img and img.get('src'):
                    media.append({
                        'type': 'video',
                        'thumbnail': img['src']
                    })
        
        return media

    def extract_tweets(self):
        """Extract individual tweets from the page"""
        try:
            url = f"{self.base_url}/elonmusk"
            print(f"Scraping tweets from: {url}")
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all timeline items (tweets)
            timeline_items = soup.find_all('div', class_='timeline-item')
            
            tweets = []
            for item in timeline_items:
                tweet_data = {}
                
                # Extract tweet link/ID
                tweet_link = item.find('a', class_='tweet-link')
                if tweet_link and tweet_link.get('href'):
                    tweet_data['tweet_url'] = tweet_link['href']
                    # Extract tweet ID from URL
                    match = re.search(r'/status/(\d+)', tweet_link['href'])
                    if match:
                        tweet_data['tweet_id'] = match.group(1)
                
                # Check if it's a retweet
                retweet_header = item.find('div', class_='retweet-header')
                if retweet_header:
                    tweet_data['is_retweet'] = True
                    retweet_text = retweet_header.get_text(strip=True)
                    tweet_data['retweet_info'] = retweet_text
                else:
                    tweet_data['is_retweet'] = False
                
                # Check if it's pinned
                pinned = item.find('div', class_='pinned')
                tweet_data['is_pinned'] = bool(pinned)
                
                # Extract author info
                tweet_header = item.find('div', class_='tweet-header')
                if tweet_header:
                    fullname = tweet_header.find('a', class_='fullname')
                    username = tweet_header.find('a', class_='username')
                    tweet_date = tweet_header.find('span', class_='tweet-date')
                    
                    if fullname:
                        tweet_data['author'] = fullname.get_text(strip=True)
                    if username:
                        tweet_data['username'] = username.get_text(strip=True)
                    if tweet_date:
                        tweet_data['date'] = tweet_date.get_text(strip=True)
                        # Extract full date from title if available
                        date_link = tweet_date.find('a')
                        if date_link and date_link.get('title'):
                            tweet_data['full_date'] = date_link['title']
                
                # Extract tweet content
                tweet_content = item.find('div', class_='tweet-content')
                if tweet_content:
                    tweet_data['text'] = tweet_content.get_text(strip=True)
                
                # Extract quoted tweet
                quoted_tweet = self.extract_quoted_tweet(item)
                if quoted_tweet:
                    tweet_data['quoted_tweet'] = quoted_tweet
                
                # Extract media
                media = self.extract_media_info(item)
                if media:
                    tweet_data['media'] = media
                
                # Extract stats
                stats = self.extract_tweet_stats(item)
                if stats:
                    tweet_data['stats'] = stats
                
                tweets.append(tweet_data)
            
            return {
                'url': url,
                'scrape_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'tweets_count': len(tweets),
                'tweets': tweets
            }
            
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return None
        except Exception as e:
            print(f"Error scraping tweets: {e}")
            return None

    def save_tweets(self, data, filename="tweets.json"):
        """Save tweets data to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Tweets saved to {filename}")
        except Exception as e:
            print(f"Error saving tweets: {e}")

def main():
    """Main function to run the tweet scraper"""
    scraper = ElonMuskScraper()
    
    print("Starting tweet scraper for http://127.0.0.1:8080/elonmusk")
    
    # Extract tweets
    data = scraper.extract_tweets()
    
    if data:
        # Save to file
        scraper.save_tweets(data)
        
        # Print summary
        print(f"\nScraping completed successfully!")
        print(f"Total tweets found: {data['tweets_count']}")
        
        # Show first few tweets as preview
        print(f"\nFirst 3 tweets preview:")
        for i, tweet in enumerate(data['tweets'][:3]):
            print(f"\n--- Tweet {i+1} ---")
            print(f"Author: {tweet.get('author', 'N/A')} ({tweet.get('username', 'N/A')})")
            print(f"Date: {tweet.get('date', 'N/A')}")
            print(f"Text: {tweet.get('text', 'N/A')[:100]}...")
            print(f"Retweet: {tweet.get('is_retweet', False)}")
            print(f"Pinned: {tweet.get('is_pinned', False)}")
            if 'stats' in tweet:
                print(f"Stats: {tweet['stats']}")
    else:
        print("Tweet scraping failed!")

if __name__ == "__main__":
    main()