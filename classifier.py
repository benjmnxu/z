#!/usr/bin/env python3
"""
AI-powered tweet classification module
Handles GPT and Claude API calls for importance scoring
"""

import json
import os
try:
    import openai
except ImportError:
    openai = None
    
try:
    import anthropic
except ImportError:
    anthropic = None

from config import AI_CONFIG, KEYWORD_CONFIG


class TweetClassifier:
    """AI-powered tweet importance classifier"""
    
    def __init__(self, ai_provider="gpt"):
        self.ai_provider = ai_provider
        self.openai_client = None
        self.anthropic_client = None
        self._init_ai_clients()
    
    def _init_ai_clients(self):
        """Initialize AI API clients"""
        if self.ai_provider == "gpt" and openai:
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
    
    def classify_with_gpt(self, tweet_data, context):
        """Classify tweet importance using GPT-4o-mini"""
        if not self.openai_client:
            return 5, "GPT client not available"
        
        text = tweet_data.get('text', '')
        is_retweet = tweet_data.get('is_retweet', False)
        is_pinned = tweet_data.get('is_pinned', False)
        
        prompt = f"""Rate the importance of this tweet on a scale of 1-10 for someone interested in {context}.

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
            config = AI_CONFIG["gpt"]
            response = self.openai_client.chat.completions.create(
                model=config["model"],
                messages=[{"role": "user", "content": prompt}],
                max_tokens=config["max_tokens"],
                temperature=config["temperature"]
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get('score', 5), result.get('reason', 'GPT classification')
            
        except Exception as e:
            print(f"GPT classification error: {e}")
            return 5, f"GPT error: {str(e)[:50]}"
    
    def classify_with_claude(self, tweet_data, context):
        """Classify tweet importance using Claude 3.5 Haiku"""
        if not self.anthropic_client:
            return 5, "Claude client not available"
        
        text = tweet_data.get('text', '')
        is_retweet = tweet_data.get('is_retweet', False)
        is_pinned = tweet_data.get('is_pinned', False)
        
        prompt = f"""Rate the importance of this tweet on a scale of 1-10 for someone interested in {context}.

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
            config = AI_CONFIG["claude"]
            response = self.anthropic_client.messages.create(
                model=config["model"],
                max_tokens=config["max_tokens"],
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = json.loads(response.content[0].text)
            return result.get('score', 5), result.get('reason', 'Claude classification')
            
        except Exception as e:
            print(f"Claude classification error: {e}")
            return 5, f"Claude error: {str(e)[:50]}"
    
    def classify_tweet(self, tweet_data, context):
        """Main classification function"""
        if self.ai_provider == "gpt":
            return self.classify_with_gpt(tweet_data, context)
        elif self.ai_provider == "claude":
            return self.classify_with_claude(tweet_data, context)
        else:
            return 5, "Unknown AI provider"
    
    def is_ai_available(self):
        """Check if AI client is properly configured"""
        if self.ai_provider == "gpt":
            return self.openai_client is not None
        elif self.ai_provider == "claude":
            return self.anthropic_client is not None
        return False
    
    def simple_keyword_classification(self, tweet_data):
        """Fallback classification without AI"""
        text = tweet_data.get('text', '').lower()
        score = 5
        
        if tweet_data.get('is_pinned'):
            score = 9
            reason = "Pinned tweet"
        elif any(keyword in text for keyword in KEYWORD_CONFIG["high_priority"]):
            score = 8
            reason = "High priority keyword"
        elif any(keyword in text for keyword in KEYWORD_CONFIG["company_keywords"]):
            score = 7 if not tweet_data.get('is_retweet') else 5
            reason = "Company keyword"
        elif any(keyword in text for keyword in KEYWORD_CONFIG["tech_keywords"]):
            score = 6 if not tweet_data.get('is_retweet') else 4
            reason = "Tech keyword"
        elif tweet_data.get('is_retweet'):
            score = 4
            reason = "Retweet"
        else:
            reason = "Default classification"
        
        return score, reason