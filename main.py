"""
Main entry point for the multi-handle Twitter scraper
"""

from tweet_scraper import TwitterScraper
from config import HANDLES_CONFIG


def main():
    """Main function to run the multi-handle tweet scraper"""
    
    # Create scraper with default configuration
    scraper = TwitterScraper(
        ai_classification=True,     # Enable AI classification
        ai_provider="gpt",          # Use GPT-4o-mini (default)
        handles_config=HANDLES_CONFIG
    )
    
    print("🐦 Starting multi-handle Twitter scraper")
    
    # Scrape from all configured handles
    data = scraper.extract_tweets_from_multiple_handles()
    
    # Save results if we found important tweets
    if data and data['stats']['total_important_tweets'] > 0:
        scraper.save_tweets(data)
        scraper.print_results_summary(data)
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
    
    result = scraper.extract_tweets_from_handle(handle)
    
    if result and result['new_tweets_count'] > 0:
        scraper.save_tweets(result, f"tweets_{handle}.json")
        print(f"\\n✅ Found {result['new_tweets_count']} important tweets from @{handle}")
    else:
        print(f"\\n✅ No important tweets found for @{handle}")
    
    return result


if __name__ == "__main__":
    main()