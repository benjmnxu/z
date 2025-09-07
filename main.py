from tweet_scraper import TwitterScraper
from config import HANDLES_CONFIG
from email_notifier import EmailNotifier


def main():
    notifier = EmailNotifier()
    if notifier.is_configured and notifier.test_email_connection():
        email_enabled = True
    else:
        email_enabled = False
    
    scraper = TwitterScraper(
        ai_classification=True,
        ai_provider="gpt",
        handles_config=HANDLES_CONFIG,
        enable_email_notifications=email_enabled,
        email_min_score=8
    )
    
    data = scraper.extract_tweets_from_multiple_handles()
    
    if data and data['stats']['total_important_tweets'] > 0:
        scraper.save_tweets(data)
        scraper.print_results_summary(data)
        
        if email_enabled:
            high_priority = len([t for t in data['combined_tweets'] if t.get('importance_score', 0) >= 8])
            print(f"\n📧 Sent {high_priority} email notifications")
    else:
        print("No important tweets found!")


def scrape_handle(handle, min_score=6):
    config = {handle: {"min_score": min_score, "context": f"{handle} content"}}
    
    scraper = TwitterScraper(ai_classification=True, ai_provider="gpt", handles_config=config)
    result = scraper.extract_tweets_from_handle(handle)
    
    if result and result['new_tweets_count'] > 0:
        scraper.save_tweets(result, f"tweets_{handle}.json")
        print(f"✅ Found {result['new_tweets_count']} important tweets from @{handle}")
    else:
        print(f"No important tweets found for @{handle}")
    
    return result


if __name__ == "__main__":
    main()