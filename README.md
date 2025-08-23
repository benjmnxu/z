# Multi-Handle AI Twitter Scraper

An intelligent Twitter scraper that monitors multiple handles and uses AI to filter only the most important tweets.

## 🚀 Features

- **Multi-handle support** - Monitor multiple Twitter accounts simultaneously  
- **AI-powered filtering** - GPT-4o-mini or Claude 3.5 Haiku classify tweet importance
- **Real-time deduplication** - Never process the same tweet twice
- **Per-handle configuration** - Different importance thresholds and contexts per account
- **Cost-optimized** - Minimal API costs (~$0.07/month for 5 handles)
- **Instant alerts** - Get notified immediately for high-priority tweets
- **Comprehensive extraction** - Full tweet content, media, stats, and metadata

## 📁 Project Structure

```
├── main.py              # Main entry point
├── tweet_scraper.py     # Core scraping functionality  
├── classifier.py        # AI classification logic
├── config.py           # Configuration and handle settings
├── examples.py         # Example usage patterns
├── requirements.txt    # Dependencies
└── setup.md           # Detailed setup instructions
```

## 🔧 Quick Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set API key (choose one):**
```bash
# For GPT-4o-mini (default, cheapest)
export OPENAI_API_KEY="sk-your-openai-key-here"

# For Claude 3.5 Haiku (better reasoning)  
export ANTHROPIC_API_KEY="sk-ant-your-anthropic-key-here"
```

3. **Run the scraper:**
```bash
python main.py
```

## 💡 Usage Examples

### Basic Multi-Handle Scraping
```python
from tweet_scraper import TwitterScraper

scraper = TwitterScraper(
    ai_classification=True,
    ai_provider="gpt",  # or "claude"
)

data = scraper.extract_tweets_from_multiple_handles()
```

### Custom Handle Configuration
```python
handles_config = {
    "elonmusk": {
        "min_score": 6,
        "context": "Elon Musk tech/business content"
    },
    "naval": {
        "min_score": 8,  # Very selective
        "context": "Naval Ravikant investing/philosophy content"  
    }
}

scraper = TwitterScraper(handles_config=handles_config)
```

### Single Handle
```python
from main import scrape_single_handle

result = scrape_single_handle("elonmusk", ai_provider="claude", min_score=7)
```

## 🎛️ Configuration

Edit `config.py` to customize:
- **Handles** - Add/remove Twitter handles to monitor
- **AI settings** - Model parameters and API configuration
- **Keywords** - Fallback classification terms
- **Scoring thresholds** - Importance levels per handle

## 📊 Cost Analysis

Per handle (~600 tweets/month):
- **GPT-4o-mini**: ~$0.014/month 
- **Claude 3.5 Haiku**: ~$0.023/month
- **Keyword-based**: Free

For 5 handles: ~$0.07-0.12/month

## 🏃 Quick Start

```bash
# Interactive examples
python examples.py

# Default multi-handle scraping
python main.py

# View configuration options  
cat config.py
```

## 📈 Sample Output

```
🚨 HIGH PRIORITY TWEET (@elonmusk, Score: 9)
   Reason: Major business announcement  
   Author: Elon Musk (@elonmusk)
   Text: Announcing the world's first Gigawatt+ AI training supercomputer...

📊 SCRAPING SUMMARY (@elonmusk):
   ✅ Important tweets kept: 3
   ❌ Low-priority filtered: 17  
   🤖 AI Provider: gpt
```

See `setup.md` for detailed configuration options and advanced usage.

## 📋 Requirements

- Python 3.6+
- Local Twitter/X instance on `http://127.0.0.1:8080`
- OpenAI or Anthropic API key (for AI classification)

## 🛠️ Advanced Usage

See the example files for more patterns:
- `examples.py` - Interactive examples and comparisons
- `config_example.py` - Legacy configuration examples  
- `setup.md` - Comprehensive setup guide

## ⚡ Performance

- **Deduplication**: Never processes the same tweet twice
- **Real-time filtering**: Immediate importance classification
- **Batch processing**: Efficient multi-handle operations
- **Cost optimized**: Minimal API usage

## 📝 License

Educational and research use. Ensure compliance with Twitter's Terms of Service.
