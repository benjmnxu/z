#!/usr/bin/env python3
"""
AI-powered Twitter scraper for multiple handles with importance classification
Supports GPT-4o-mini and Claude 3.5 Haiku for tweet filtering
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urljoin
import re
import os
try:
    import openai
except ImportError:
    print("Warning: openai package not installed. Run: pip install openai")
    openai = None
    
try:
    import anthropic
except ImportError:
    print("Warning: anthropic package not installed. Run: pip install anthropic")
    anthropic = None

class TwitterScraper:
    def __init__(self, base_url="http://127.0.0.1:8080", seen_tweets_file="seen_tweets.json", 
                 ai_classification=False, ai_provider="gpt", handles_config=None):
        self.base_url = base_url
        self.seen_tweets_file = seen_tweets_file
        self.ai_classification = ai_classification
        self.ai_provider = ai_provider  # "gpt" or "claude"
        
        # Handle configuration: {"handle": {"min_score": X, "context": "..."}}
        self.handles_config = handles_config or {
            "elonmusk": {
                "min_score": 6,
                "context": "Elon Musk tech/business content (Tesla, SpaceX, xAI, Neuralink)"
            }
        }
        
        self.seen_tweet_ids = self.load_seen_tweets()
        
        # Initialize AI clients if needed
        self.openai_client = None
        self.anthropic_client = None
        
        if ai_classification:
            self._init_ai_clients()
        
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

    def load_seen_tweets(self):
        """Load previously seen tweet IDs from file"""
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
        """Save seen tweet IDs to file"""
        try:
            data = {
                'seen_tweet_ids': list(self.seen_tweet_ids),
                'last_updated': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            with open(self.seen_tweets_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Saved {len(self.seen_tweet_ids)} seen tweet IDs to {self.seen_tweets_file}")
        except Exception as e:
            print(f"Error saving seen tweets: {e}")

    def is_new_tweet(self, tweet_id):
        """Check if a tweet ID is new (not seen before)"""
        return tweet_id not in self.seen_tweet_ids

    def mark_tweet_as_seen(self, tweet_id):
        """Mark a tweet ID as seen"""
        self.seen_tweet_ids.add(tweet_id)
    
    def _init_ai_clients(self):
        """Initialize AI API clients"""
        if self.ai_provider == "gpt" and openai:
            # Get API key from environment or config
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                self.openai_client = openai.OpenAI(api_key=api_key)
            else:
                print("Warning: OPENAI_API_KEY not found in environment")
        
        elif self.ai_provider == "claude" and anthropic:
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if api_key:
                self.anthropic_client = anthropic.Anthropic(api_key=api_key)
            else:
                print("Warning: ANTHROPIC_API_KEY not found in environment")
    
    def classify_with_gpt(self, tweet_data, author_context):
        """Classify tweet importance using GPT-4o-mini"""
        if not self.openai_client:
            return 5, "GPT client not available"
        
        text = tweet_data.get('text', '')
        is_retweet = tweet_data.get('is_retweet', False)
        is_pinned = tweet_data.get('is_pinned', False)
        
        prompt = f"""Rate the importance of this tweet on a scale of 1-10 for someone interested in {author_context}.

Consider:
- Business announcements, product launches, earnings (9-10)
- Technical updates, significant news (7-8) 
- General insights, commentary (5-6)
- Social content, memes, casual posts (1-4)

Tweet: "{text}"
Is Retweet: {is_retweet}
Is Pinned: {is_pinned}

Respond with only a JSON object: {{"score": X, "reason": "brief explanation"}}"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get('score', 5), result.get('reason', 'GPT classification')
            
        except Exception as e:
            print(f"GPT classification error: {e}")
            return 5, f"GPT error: {str(e)[:50]}"
    
    def classify_with_claude(self, tweet_data, author_context):
        """Classify tweet importance using Claude 3.5 Haiku"""
        if not self.anthropic_client:
            return 5, "Claude client not available"
        
        text = tweet_data.get('text', '')
        is_retweet = tweet_data.get('is_retweet', False)
        is_pinned = tweet_data.get('is_pinned', False)
        
        prompt = f"""Rate the importance of this tweet on a scale of 1-10 for someone interested in {author_context}.

Scoring guide:
- Major business announcements, earnings, launches: 9-10
- Significant product updates, technical breakthroughs: 7-8
- Industry insights, meaningful commentary: 5-6  
- Social posts, retweets of fluff, memes: 1-4

Tweet: "{text}"
Is Retweet: {is_retweet}
Is Pinned: {is_pinned}

Respond with only a JSON object: {{"score": X, "reason": "brief explanation"}}"""
        
        try:
            response = self.anthropic_client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=100,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            result = json.loads(response.content[0].text)
            return result.get('score', 5), result.get('reason', 'Claude classification')
            
        except Exception as e:
            print(f"Claude classification error: {e}")
            return 5, f"Claude error: {str(e)[:50]}"
    
    def classify_tweet_importance(self, tweet_data, handle):
        """Main classification function that routes to the selected AI provider"""
        handle_config = self.handles_config.get(handle, self.handles_config.get("elonmusk", {}))
        min_score = handle_config.get("min_score", 6)
        context = handle_config.get("context", f"{handle} content")
        
        if not self.ai_classification:
            # Fallback to simple keyword-based classification
            return self._simple_keyword_classification(tweet_data, min_score)
        
        # Use selected AI provider
        if self.ai_provider == "gpt":
            score, reason = self.classify_with_gpt(tweet_data, context)
        elif self.ai_provider == "claude":
            score, reason = self.classify_with_claude(tweet_data, context)
        else:
            score, reason = 5, "Unknown AI provider"
        
        # Determine if tweet meets minimum threshold for this handle
        is_important = score >= min_score
        
        return is_important, score, reason
    
    def _simple_keyword_classification(self, tweet_data, min_score):
        """Fallback classification without AI"""
        text = tweet_data.get('text', '').lower()
        score = 5
        
        if tweet_data.get('is_pinned'):
            score = 9
            reason = "Pinned tweet"
        elif any(word in text for word in ['announcement', 'launching', 'breaking']):
            score = 8
            reason = "Announcement keyword"
        elif any(word in text for word in ['xai', 'spacex', 'tesla', 'neuralink', 'openai']):
            score = 7 if not tweet_data.get('is_retweet') else 5
            reason = "Company keyword"
        elif tweet_data.get('is_retweet'):
            score = 4
            reason = "Retweet"
        else:
            reason = "Default classification"
        
        is_important = score >= min_score
        return is_important, score, reason

    def extract_tweets_from_handle(self, handle):
        """Extract individual tweets from a specific handle"""
        try:
            url = f"{self.base_url}/{handle}"
            print(f"\n🔍 Scraping tweets from: {url}")
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all timeline items (tweets)
            timeline_items = soup.find_all('div', class_='timeline-item')
            
            tweets = []
            new_tweets = []
            skipped_tweets = 0
            filtered_out = 0
            
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
                        
                        # Check if we've seen this tweet before
                        if not self.is_new_tweet(tweet_data['tweet_id']):
                            skipped_tweets += 1
                            continue  # Skip this tweet, we've processed it before
                        
                        # Mark as seen
                        self.mark_tweet_as_seen(tweet_data['tweet_id'])
                
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
                
                # AI-powered importance classification
                is_important, score, reason = self.classify_tweet_importance(tweet_data, handle)
                
                tweet_data['handle'] = handle
                tweet_data['importance_score'] = score
                tweet_data['importance_reason'] = reason
                tweet_data['ai_provider'] = self.ai_provider if self.ai_classification else 'keyword'
                
                if is_important:
                    new_tweets.append(tweet_data)
                    
                    # Alert for high-importance tweets
                    if score >= 8:
                        print(f"\n🚨 HIGH PRIORITY TWEET (@{handle}, Score: {score})")
                        print(f"   Reason: {reason}")
                        print(f"   Author: {tweet_data.get('author', 'N/A')}")
                        print(f"   Text: {tweet_data.get('text', '')[:100]}...")
                else:
                    filtered_out += 1
                    if score <= 3:
                        print(f"   ❌ Filtered (@{handle}, Score: {score}): {reason}")
            
            # Save updated seen tweets list
            self.save_seen_tweets()
            
            handle_config = self.handles_config.get(handle, {})
            min_score = handle_config.get('min_score', 6)
            
            print(f"\n📊 SCRAPING SUMMARY (@{handle}):")
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
        """Extract tweets from multiple handles"""
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
        
        print(f"\n🚀 Starting multi-handle scrape for: {', '.join(['@' + h for h in handles])}")
        
        for handle in handles:
            print(f"\n{'='*50}")
            result = self.extract_tweets_from_handle(handle)
            
            if result:
                all_results.append(result)
                combined_tweets.extend(result['tweets'])
                total_stats['successful_handles'] += 1
                total_stats['total_important_tweets'] += result['new_tweets_count']
                total_stats['total_filtered_tweets'] += result['filtered_out_count']
            else:
                print(f"❌ Failed to scrape @{handle}")
        
        # Sort all tweets by importance score
        combined_tweets.sort(key=lambda x: x.get('importance_score', 0), reverse=True)
        
        return {
            'scrape_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'handles_scraped': handles,
            'individual_results': all_results,
            'combined_tweets': combined_tweets,
            'stats': total_stats
        }

    def save_tweets(self, data, filename="tweets.json"):
        """Save tweets data to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"📁 Tweets saved to {filename}")
        except Exception as e:
            print(f"Error saving tweets: {e}")

def main():
    """Main function to run the multi-handle tweet scraper"""
    
    # Define handles and their specific configurations
    handles_config = {
        "elonmusk": {
            "min_score": 6,
            "context": "Elon Musk tech/business content (Tesla, SpaceX, xAI, Neuralink, major announcements)"
        },
        "sama": {
            "min_score": 7,
            "context": "Sam Altman content (OpenAI, AI development, tech leadership, industry insights)"
        },
        "karpathy": {
            "min_score": 6,
            "context": "Andrej Karpathy content (AI research, machine learning, technical insights)"
        }
    }
    
    scraper = TwitterScraper(
        ai_classification=True,     # Enable AI classification
        ai_provider="gpt",          # Use GPT-4o-mini (default)
        handles_config=handles_config
    )
    
    print("🐦 Starting multi-handle Twitter scraper")
    
    # Scrape from all configured handles
    data = scraper.extract_tweets_from_multiple_handles()
    
    if data and data['stats']['total_important_tweets'] > 0:
        # Save combined results
        scraper.save_tweets(data, "tweets_multi_handle.json")
        
        # Print overall summary
        stats = data['stats']
        print(f"\n{'='*60}")
        print(f"🎯 MULTI-HANDLE SCRAPING COMPLETE!")
        print(f"   📊 Handles processed: {stats['successful_handles']}/{stats['total_handles']}")
        print(f"   ✅ Total important tweets: {stats['total_important_tweets']}")
        print(f"   ❌ Total filtered tweets: {stats['total_filtered_tweets']}")
        
        # Show top tweets across all handles
        if data['combined_tweets']:
            print(f"\n🏆 TOP IMPORTANT TWEETS (All Handles):")
            for i, tweet in enumerate(data['combined_tweets'][:5]):
                score = tweet.get('importance_score', 0)
                reason = tweet.get('importance_reason', 'Unknown')
                handle = tweet.get('handle', 'unknown')
                provider = tweet.get('ai_provider', 'keyword')
                
                print(f"\n--- #{i+1} [@{handle}] [Score: {score}/10 - {provider.upper()}] ---")
                print(f"💡 {reason}")
                print(f"👤 {tweet.get('author', 'N/A')} ({tweet.get('username', 'N/A')})")
                print(f"🕒 {tweet.get('date', 'N/A')}")
                print(f"📝 {tweet.get('text', 'N/A')[:150]}...")
                
                if tweet.get('is_pinned'):
                    print(f"📌 PINNED")
                if tweet.get('is_retweet'):
                    print(f"🔄 RETWEET")
    else:
        print("❌ No important tweets found or scraping failed!")

def scrape_single_handle(handle, ai_provider="gpt", min_score=6):
    """Helper function to scrape a single handle"""
    config = {
        handle: {
            "min_score": min_score,
            "context": f"{handle} content"
        }
    }
    
    scraper = TwitterScraper(
        ai_classification=True,
        ai_provider=ai_provider,
        handles_config=config
    )
    
    return scraper.extract_tweets_from_handle(handle)

if __name__ == "__main__":
    main()