#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import json
import time
import re
import os

from classifier import TweetClassifier
from config import SCRAPER_CONFIG, HANDLES_CONFIG
from email_notifier import EmailNotifier


class TwitterScraper:
    
    def __init__(self, ai_classification=False, ai_provider="gpt", handles_config=None, 
                 enable_email_notifications=False, email_min_score=8):
        self.ai_classification = ai_classification
        self.ai_provider = ai_provider
        self.handles_config = handles_config or HANDLES_CONFIG
        
        self.classifier = TweetClassifier(ai_provider)
        self.email_notifier = None
        self.enable_email_notifications = enable_email_notifications
        if enable_email_notifications:
            self.email_notifier = EmailNotifier(min_score_for_email=email_min_score)
        self.seen_tweets_file = SCRAPER_CONFIG["seen_tweets_file"]
        self.seen_tweet_ids = self.load_seen_tweets()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': SCRAPER_CONFIG["user_agent"]
        })
    
    def load_seen_tweets(self):
        if os.path.exists(self.seen_tweets_file):
            try:
                with open(self.seen_tweets_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return set(data.get('seen_tweet_ids', []))
            except (json.JSONDecodeError, KeyError):
                print(f"Warning: Could not load seen tweets from {self.seen_tweets_file}. Starting fresh.")
                return set()
        return set()
    
    def save_seen_tweets(self):
        try:
            data = {
                'seen_tweet_ids': list(self.seen_tweet_ids),
                'last_updated': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            with open(self.seen_tweets_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving seen tweets: {e}")
    
    def is_new_tweet(self, tweet_id):
        return tweet_id not in self.seen_tweet_ids
    
    def mark_tweet_as_seen(self, tweet_id):
        self.seen_tweet_ids.add(tweet_id)
    
    def extract_tweet_stats(self, tweet_element):
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
                    numbers = re.findall(r'[\\d,]+', stat_text)
                    if numbers:
                        stats[stat_type] = numbers[0].replace(',', '')
        
        return stats
    
    def extract_quoted_tweet(self, tweet_element):
        quote = tweet_element.find('div', class_='quote')
        if not quote:
            return None
            
        quoted_tweet = {}
        
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
        quote_text = quote.find('div', class_='quote-text')
        if quote_text:
            quoted_tweet['text'] = quote_text.get_text(strip=True)
        quote_link = quote.find('a', class_='quote-link')
        if quote_link and quote_link.get('href'):
            quoted_tweet['link'] = quote_link['href']
        
        return quoted_tweet
    
    def extract_media_info(self, tweet_element):
        media = []
        attachments = tweet_element.find('div', class_='attachments')
        if attachments:
            images = attachments.find_all('img')
            for img in images:
                if img.get('src'):
                    media.append({
                        'type': 'image',
                        'src': img['src'],
                        'alt': img.get('alt', '')
                    })
            video_containers = attachments.find_all('div', class_='video-container')
            for video in video_containers:
                img = video.find('img')
                if img and img.get('src'):
                    media.append({
                        'type': 'video',
                        'thumbnail': img['src']
                    })
        
        return media
    
    def classify_tweet_importance(self, tweet_data, handle):
        handle_config = self.handles_config.get(handle, {})
        min_score = handle_config.get("min_score", 6)
        context = handle_config.get("context", f"{handle} content")
        
        if self.ai_classification and self.classifier.is_ai_available():
            score, reason = self.classifier.classify_tweet(tweet_data, context)
        else:
            score, reason = self.classifier.simple_keyword_classification(tweet_data)
            if self.ai_classification and not self.classifier.is_ai_available():
                reason += " (AI not available - using keywords)"
        
        is_important = score >= min_score
        return is_important, score, reason
    
    def extract_tweets_from_handle(self, handle):
        try:
            url = f"{SCRAPER_CONFIG['base_url']}/{handle}"
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            timeline_items = soup.find_all('div', class_='timeline-item')
            
            tweets = []
            new_tweets = []
            skipped_tweets = 0
            filtered_out = 0
            
            for item in timeline_items:
                tweet_data = {}
                
                tweet_link = item.find('a', class_='tweet-link')
                if tweet_link and tweet_link.get('href'):
                    tweet_data['tweet_url'] = tweet_link['href']
                    match = re.search(r'/status/(\d+)', tweet_link['href'])
                    if match:
                        tweet_data['tweet_id'] = match.group(1)
                        if not self.is_new_tweet(tweet_data['tweet_id']):
                            skipped_tweets += 1
                            continue
                        self.mark_tweet_as_seen(tweet_data['tweet_id'])
                retweet_header = item.find('div', class_='retweet-header')
                tweet_data['is_retweet'] = bool(retweet_header)
                if retweet_header:
                    tweet_data['retweet_info'] = retweet_header.get_text(strip=True)
                
                tweet_data['is_pinned'] = bool(item.find('div', class_='pinned'))
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
                        date_link = tweet_date.find('a')
                        if date_link and date_link.get('title'):
                            tweet_data['full_date'] = date_link['title']
                tweet_content = item.find('div', class_='tweet-content')
                if tweet_content:
                    tweet_data['text'] = tweet_content.get_text(strip=True)
                tweet_data['quoted_tweet'] = self.extract_quoted_tweet(item)
                tweet_data['media'] = self.extract_media_info(item)
                tweet_data['stats'] = self.extract_tweet_stats(item)
                
                tweets.append(tweet_data)
                is_important, score, reason = self.classify_tweet_importance(tweet_data, handle)
                
                tweet_data['handle'] = handle
                tweet_data['importance_score'] = score
                tweet_data['importance_reason'] = reason
                tweet_data['ai_provider'] = self.ai_provider if self.ai_classification else 'keyword'
                
                if is_important:
                    new_tweets.append(tweet_data)
                    if score >= 8:
                        print(f"\\n🚨 HIGH PRIORITY TWEET (@{handle}, Score: {score})")
                        print(f"   Reason: {reason}")
                        print(f"   Author: {tweet_data.get('author', 'N/A')}")
                        print(f"   Text: {tweet_data.get('text', '')[:1000]}...")
                else:
                    filtered_out += 1
            self.save_seen_tweets()
            handle_config = self.handles_config.get(handle, {})
            min_score = handle_config.get('min_score', 6)
            
            print(f"\\n📊 SCRAPING SUMMARY (@{handle}):")
            print(f"   Total tweets on page: {len(tweets)}")
            print(f"   Already seen (skipped): {skipped_tweets}")
            print(f"   ✅ Important tweets kept: {len(new_tweets)}")
            print(f"   ❌ Low-priority filtered: {filtered_out}")
            print(f"   🤖 AI Provider: {self.ai_provider if self.ai_classification else 'keyword-based'}")
            print(f"   📈 Min Score Threshold: {min_score}")
            
            return {
                'handle': handle,
                'url': url,
                'scrape_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'tweets_count': len(tweets),
                'new_tweets_count': len(new_tweets),
                'skipped_tweets_count': skipped_tweets,
                'tweets': new_tweets,
                'filtered_out_count': filtered_out,
                'ai_classification_enabled': self.ai_classification,
                'ai_provider': self.ai_provider if self.ai_classification else 'keyword',
                'handle_config': handle_config
            }
            
        except requests.exceptions.RequestException as e:
            print(f"Request error for @{handle}: {e}")
            return None
        except Exception as e:
            print(f"Error scraping tweets for @{handle}: {e}")
            return None
    
    def extract_tweets_from_multiple_handles(self, handles=None):
        if handles is None:
            handles = list(self.handles_config.keys())
        
        all_results = []
        combined_tweets = []
        total_stats = {
            'total_handles': len(handles),
            'successful_handles': 0,
            'total_important_tweets': 0,
            'total_filtered_tweets': 0
        }
        
        for handle in handles:
            result = self.extract_tweets_from_handle(handle)
            
            if result:
                all_results.append(result)
                combined_tweets.extend(result['tweets'])
                total_stats['successful_handles'] += 1
                total_stats['total_important_tweets'] += result['new_tweets_count']
                total_stats['total_filtered_tweets'] += result['filtered_out_count']
            else:
                print(f"❌ Failed to scrape @{handle}")
        
        combined_tweets.sort(key=lambda x: x.get('importance_score', 0), reverse=True)
        if self.email_notifier and self.enable_email_notifications and total_stats['total_important_tweets'] > 0:
            tweets_by_handle = {}
            for result in all_results:
                handle = result['handle']
                tweets_by_handle[handle] = result['tweets']
            self.email_notifier.send_batch_notification(tweets_by_handle, total_stats['total_important_tweets'])
        
        return {
            'scrape_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'handles_scraped': handles,
            'individual_results': all_results,
            'combined_tweets': combined_tweets,
            'stats': total_stats
        }
    
    def save_tweets(self, data, filename=None):
        if filename is None:
            filename = SCRAPER_CONFIG["output_file"]
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"📁 Tweets saved to {filename}")
        except Exception as e:
            print(f"Error saving tweets: {e}")
    
    def print_results_summary(self, data):
        if not data or not data.get('stats', {}).get('total_important_tweets'):
            print("❌ No important tweets found!")
            return
        
        stats = data['stats']
        print(f"\\n{'='*60}")
        print(f"🎯 MULTI-HANDLE SCRAPING COMPLETE!")
        print(f"   📊 Handles processed: {stats['successful_handles']}/{stats['total_handles']}")
        print(f"   ✅ Total important tweets: {stats['total_important_tweets']}")
        print(f"   ❌ Total filtered tweets: {stats['total_filtered_tweets']}")
        if data['combined_tweets']:
            print(f"\\n🏆 TOP IMPORTANT TWEETS (All Handles):")
            for i, tweet in enumerate(data['combined_tweets'][:5]):
                score = tweet.get('importance_score', 0)
                reason = tweet.get('importance_reason', 'Unknown')
                handle = tweet.get('handle', 'unknown')
                provider = tweet.get('ai_provider', 'keyword')
                
                print(f"\\n--- #{i+1} [@{handle}] [Score: {score}/10 - {provider.upper()}] ---")
                print(f"💡 {reason}")
                print(f"👤 {tweet.get('author', 'N/A')} ({tweet.get('username', 'N/A')})")
                print(f"🕒 {tweet.get('date', 'N/A')}")
                print(f"📝 {tweet.get('text', 'N/A')[:150]}...")
                
                if tweet.get('is_pinned'):
                    print(f"📌 PINNED")
                if tweet.get('is_retweet'):
                    print(f"🔄 RETWEET")