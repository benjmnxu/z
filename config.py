#!/usr/bin/env python3
"""
Configuration file for Twitter handles and their classification settings
"""

# Default handle configurations
HANDLES_CONFIG = {
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
    },
    "naval": {
        "min_score": 8,  # Very selective
        "context": "Naval Ravikant content (startups, investing, philosophy, wealth creation)"
    },
    "pmarca": {
        "min_score": 7,
        "context": "Marc Andreessen content (VC insights, tech trends, startups, market analysis)"
    },
    "balajis": {
        "min_score": 7,
        "context": "Balaji Srinivasan content (crypto, tech trends, geopolitics, innovation)"
    }
}

# AI Provider settings
AI_CONFIG = {
    "gpt": {
        "model": "gpt-4o-mini",
        "max_tokens": 100,
        "temperature": 0.3
    },
    "claude": {
        "model": "claude-3-5-haiku-20241022",
        "max_tokens": 100
    }
}

# Scraper settings
SCRAPER_CONFIG = {
    "base_url": "http://127.0.0.1:8080",
    "seen_tweets_file": "seen_tweets.json",
    "output_file": "tweets_multi_handle.json",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Keyword classification fallback (when AI is disabled)
KEYWORD_CONFIG = {
    "high_priority": [
        "announcement", "announcing", "excited to announce", "breaking:", "news:",
        "launching", "launch", "release", "unveiled", "introducing",
        "acquisition", "merger", "funding", "investment", "ipo", "public",
        "earnings", "quarterly results"
    ],
    "company_keywords": [
        "xai", "spacex", "tesla", "neuralink", "openai", "anthropic",
        "microsoft", "google", "apple", "meta", "nvidia"
    ],
    "tech_keywords": [
        "ai", "artificial intelligence", "machine learning", "deep learning",
        "gpt", "llm", "neural network", "transformer", "model training"
    ]
}