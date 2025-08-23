#!/usr/bin/env python3
"""
Example configurations and usage patterns for the Twitter scraper
"""

from tweet_scraper import TwitterScraper
from main import scrape_single_handle


def example_multi_handle_default():
    """Example: Default multi-handle setup with GPT"""
    handles_config = {
        "elonmusk": {
            "min_score": 6,
            "context": "Elon Musk tech/business content (Tesla, SpaceX, xAI, Neuralink)"
        },
        "sama": {
            "min_score": 7,  # Higher threshold for Sam Altman
            "context": "Sam Altman content (OpenAI, AI development, tech leadership)"
        },
        "karpathy": {
            "min_score": 6,
            "context": "Andrej Karpathy content (AI research, machine learning, technical insights)"
        }
    }
    
    scraper = TwitterScraper(
        ai_classification=True,
        ai_provider="gpt",
        handles_config=handles_config
    )
    
    return scraper.extract_tweets_from_multiple_handles()


def example_custom_handles():
    """Example: Custom handle selection with Claude"""
    handles_config = {
        "naval": {
            "min_score": 8,  # Very selective
            "context": "Naval Ravikant content (startups, investing, philosophy)"
        },
        "pmarca": {
            "min_score": 7,
            "context": "Marc Andreessen content (VC insights, tech trends, startups)"
        }
    }
    
    scraper = TwitterScraper(
        ai_classification=True,
        ai_provider="claude",  # Use Claude for better reasoning
        handles_config=handles_config
    )
    
    # Only scrape specific handles
    return scraper.extract_tweets_from_multiple_handles(["naval", "pmarca"])


def example_single_handle():
    """Example: Scrape just one handle"""
    return scrape_single_handle(
        handle="elonmusk",
        ai_provider="gpt",
        min_score=7
    )


def example_compare_ai_providers():
    """Example: Compare GPT vs Claude on the same handles"""
    
    handles_config = {
        "elonmusk": {
            "min_score": 6,
            "context": "Elon Musk tech/business content"
        }
    }
    
    # Test GPT
    print("=== TESTING GPT-4o-mini ===")
    gpt_scraper = TwitterScraper(
        ai_classification=True,
        ai_provider="gpt",
        handles_config=handles_config
    )
    gpt_data = gpt_scraper.extract_tweets_from_multiple_handles(["elonmusk"])
    
    # Test Claude  
    print("\\n=== TESTING Claude 3.5 Haiku ===")
    claude_scraper = TwitterScraper(
        ai_classification=True,
        ai_provider="claude", 
        handles_config=handles_config
    )
    claude_data = claude_scraper.extract_tweets_from_multiple_handles(["elonmusk"])
    
    # Compare results
    gpt_count = gpt_data['stats']['total_important_tweets'] if gpt_data else 0
    claude_count = claude_data['stats']['total_important_tweets'] if claude_data else 0
    
    print(f"\\n📊 COMPARISON RESULTS:")
    print(f"GPT-4o-mini found: {gpt_count} important tweets")
    print(f"Claude 3.5 Haiku found: {claude_count} important tweets")


def example_keyword_only():
    """Example: No AI costs, keyword-based filtering only"""
    handles_config = {
        "elonmusk": {"min_score": 6, "context": "Elon Musk"},
        "sama": {"min_score": 7, "context": "Sam Altman"}
    }
    
    scraper = TwitterScraper(
        ai_classification=False,  # No AI costs
        handles_config=handles_config
    )
    
    return scraper.extract_tweets_from_multiple_handles()


def example_high_selectivity():
    """Example: Only extremely important tweets (score 8+)"""
    handles_config = {
        "elonmusk": {
            "min_score": 8,  # Very selective
            "context": "Elon Musk major announcements and business news only"
        }
    }
    
    scraper = TwitterScraper(
        ai_classification=True,
        ai_provider="claude",  # Use Claude for better reasoning
        handles_config=handles_config
    )
    
    return scraper.extract_tweets_from_multiple_handles()


def interactive_menu():
    """Interactive menu to choose examples"""
    print("🐦 Multi-handle Twitter scraper examples")
    print("Choose an example to run:")
    print("1. Default multi-handle (elonmusk, sama, karpathy)")
    print("2. Custom handles (naval, pmarca)")  
    print("3. Single handle only")
    print("4. Compare GPT vs Claude")
    print("5. Keyword-only (no AI costs)")
    print("6. High selectivity (score 8+)")
    
    choice = input("\\nEnter choice (1-6): ").strip()
    
    if choice == "1":
        data = example_multi_handle_default()
    elif choice == "2":
        data = example_custom_handles()
    elif choice == "3":
        data = example_single_handle()
    elif choice == "4":
        example_compare_ai_providers()
        return
    elif choice == "5":
        data = example_keyword_only()
    elif choice == "6":
        data = example_high_selectivity()
    else:
        print("Invalid choice, running default...")
        data = example_multi_handle_default()
    
    # Print results
    if data and 'stats' in data:
        stats = data['stats']
        print(f"\\n✅ Scraping complete!")
        print(f"📈 Important tweets found: {stats['total_important_tweets']}")
        print(f"🎯 Handles processed: {stats['successful_handles']}/{stats['total_handles']}")
    else:
        print("❌ Scraping failed or no data returned")


if __name__ == "__main__":
    interactive_menu()