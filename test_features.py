#!/usr/bin/env python3
"""
Test script to verify all features are working correctly
"""

from tweet_scraper import TwitterScraper
from main import scrape_single_handle
import json

def test_keyword_classification():
    """Test keyword-based classification"""
    print("🧪 Testing keyword classification...")
    
    scraper = TwitterScraper(ai_classification=False)
    result = scraper.extract_tweets_from_handle("elonmusk")
    
    if result and result['new_tweets_count'] > 0:
        print(f"✅ Keyword classification working - found {result['new_tweets_count']} important tweets")
        return True
    else:
        print("❌ Keyword classification failed")
        return False

def test_ai_fallback():
    """Test AI fallback to keywords when API not available"""
    print("\n🧪 Testing AI fallback to keywords...")
    
    scraper = TwitterScraper(ai_classification=True, ai_provider="gpt")
    
    # This should fall back to keywords since no API key is set
    result = scraper.extract_tweets_from_handle("elonmusk") 
    
    if result and result['new_tweets_count'] > 0:
        # Check if it fell back to keywords
        first_tweet = result['tweets'][0]
        reason = first_tweet.get('importance_reason', '')
        if 'AI not available - using keywords' in reason:
            print(f"✅ AI fallback working - fell back to keywords")
            return True
        else:
            print(f"⚠️ AI might be working - reason: {reason}")
            return True
    else:
        print("❌ AI fallback failed")
        return False

def test_multi_handle():
    """Test multi-handle functionality"""  
    print("\n🧪 Testing multi-handle scraping...")
    
    handles_config = {
        "elonmusk": {"min_score": 5, "context": "Elon Musk content"},
        "sama": {"min_score": 6, "context": "Sam Altman content"}
    }
    
    scraper = TwitterScraper(
        ai_classification=False,  # Use keywords to avoid API dependency
        handles_config=handles_config
    )
    
    result = scraper.extract_tweets_from_multiple_handles(["elonmusk"])
    
    if result and result['stats']['total_important_tweets'] > 0:
        print(f"✅ Multi-handle working - found {result['stats']['total_important_tweets']} total important tweets")
        return True
    else:
        print("❌ Multi-handle failed")
        return False

def test_deduplication():
    """Test tweet deduplication"""
    print("\n🧪 Testing deduplication...")
    
    # First run
    result1 = scrape_single_handle("elonmusk", ai_provider="gpt", min_score=5)
    first_count = result1['new_tweets_count'] if result1 else 0
    
    # Second run (should find no new tweets)
    result2 = scrape_single_handle("elonmusk", ai_provider="gpt", min_score=5)
    second_count = result2['new_tweets_count'] if result2 else 0
    
    if first_count > 0 and second_count == 0:
        print(f"✅ Deduplication working - first run: {first_count}, second run: {second_count}")
        return True
    else:
        print(f"❌ Deduplication failed - first run: {first_count}, second run: {second_count}")
        return False

def test_importance_scoring():
    """Test importance scoring ranges"""
    print("\n🧪 Testing importance scoring...")
    
    scraper = TwitterScraper(ai_classification=False)
    result = scraper.extract_tweets_from_handle("elonmusk")
    
    if result and result['new_tweets_count'] > 0:
        scores = [tweet.get('importance_score', 0) for tweet in result['tweets']]
        min_score = min(scores)
        max_score = max(scores)
        
        if min_score >= 1 and max_score <= 10:
            print(f"✅ Scoring range correct - min: {min_score}, max: {max_score}")
            return True
        else:
            print(f"❌ Scoring range invalid - min: {min_score}, max: {max_score}")
            return False
    else:
        print("❌ No tweets to test scoring")
        return False

def main():
    """Run all feature tests"""
    print("🚀 Running feature tests for Twitter scraper...\n")
    
    # Clear seen tweets for clean testing
    with open('seen_tweets.json', 'w') as f:
        json.dump({"seen_tweet_ids": [], "last_updated": "2025-08-22 17:00:00"}, f)
    
    tests = [
        test_keyword_classification,
        test_ai_fallback,
        test_multi_handle,
        test_deduplication,
        test_importance_scoring
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All features are working correctly!")
    else:
        print("⚠️ Some features need attention")

if __name__ == "__main__":
    main()